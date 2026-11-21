"""Car builder v2: python3 -I cars.py <type> <out.glb>
Body = a lofted cage (ring of 11 control points per side per section, profiles keyed per model) closed with gridded
front/rear fascias, creased, subdivided, then wheel arches cut with booleans. Lights, grilles, intakes, plates and
glass are regions of the cage, recessed with insets after subdivision so they sit exactly in the bodywork.
Blender axes: x = side (vehicle right is -x), y = length (front at -y), z = up."""
import bpy, bmesh, sys, math
from mathutils import Vector, Matrix
TYPE = sys.argv[-2]; OUT = sys.argv[-1]
def hexc(h, a=1.0):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c] + [a]
MATS = {}
def mat(name, col, rough=.5, metal=0.0, emis=None, es=0.0):
    if name in MATS: return MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = hexc(col); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emis: b.inputs['Emission Color'].default_value = hexc(emis); b.inputs['Emission Strength'].default_value = es
    MATS[name] = m; return m
bpy.ops.wm.read_factory_settings(use_empty=True)
for a in (('Paint', '#ffffff', .3, .2), ('Glass', '#0e1419', .05), ('Black', '#121314', .55), ('Under', '#0b0b0c', .9), ('Gap', '#050505', .9),
          ('Grille', '#0c0d0e', .6), ('Chrome', '#d9dde2', .12, 1.0), ('Interior', '#2a2b2e', .8), ('Seat', '#1d1e21', .85),
          ('PlateF', '#f4f4f0', .4), ('PlateR', '#f2c200', .4), ('Clear', '#c9ccd0', .1, .3), ('Livery', '#ffffff', .35, .1)): mat(*a)
mat('Lens', '#4a5058', .06, .9); mat('Carbon', '#0f1826', .3, .5); mat('LightF', '#f6f3ea', .05, 0, '#fff6e0', 1.5); mat('LightR', '#a50d12', .15, 0, '#ff1a1a', 1.2); mat('Amber', '#d27a0f', .2, 0, '#ff8a00', .6)
mat('Taxi', '#ffcc22', .3, 0, '#ffcc22', 1.2); mat('BarBlue', '#16308a', .2, 0, '#3b6bff', 0.0); mat('BarRed', '#8a1616', .2, 0, '#ff3030', 0.0)
# ------------------------------------------------------------------ helpers
def pchip(keys):
    keys = sorted(keys); keys = [k for i, k in enumerate(keys) if i == 0 or k[0] - keys[i - 1][0] > 1e-6]
    xs = [k[0] for k in keys]; ys = [k[1] for k in keys]; n = len(xs)
    h = [xs[i + 1] - xs[i] for i in range(n - 1)]; d = [(ys[i + 1] - ys[i]) / h[i] for i in range(n - 1)]
    m = [0.0] * n; m[0] = d[0]; m[-1] = d[-1]
    for i in range(1, n - 1):
        if d[i - 1] * d[i] <= 0: m[i] = 0
        else: w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]; m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    def f(x):
        if x <= xs[0]: return ys[0]
        if x >= xs[-1]: return ys[-1]
        i = max(j for j in range(n - 1) if xs[j] <= x); t = (x - xs[i]) / h[i]
        return (2 * t ** 3 - 3 * t ** 2 + 1) * ys[i] + (t ** 3 - 2 * t ** 2 + t) * h[i] * m[i] + (-2 * t ** 3 + 3 * t ** 2) * ys[i + 1] + (t ** 3 - t ** 2) * h[i] * m[i + 1]
    return f
def sm(a, b, x): t = max(0.0, min(1.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)
def lerp(a, b, t): return a + (b - a) * t
# ------------------------------------------------------------------ models (metres). front/rear: fascia heights for p2..p6 at the nose/tail
S = {
 'saloon': dict(L=4.70, W=1.83, H=1.44, r=.335, FO=.84, WB=2.85, rock=.27, mid=.60, drop=.10, beltF=.90, beltR=.99,
   top=[(0, .745), (.02, .775), (.07, .81), (.16, .85), (.30, .92), (.315, .945), (.44, 1.40), (.5, 1.44), (.64, 1.43), (.80, 1.06), (.85, 1.05), (.96, 1.02), (1, .96)],
   cowl=.30, wstop=.44, roofend=.645, deck=.80, side_end=.765, pillars=[('B', .535)], doors=[.285, .535, .705],
   front=(.25, .36, .50, .60, .715), rear=(.33, .44, .56, .78, .93), wroof=[(.30, .93), (.44, .78), (.64, .78), (.80, .92)],
   plan=[(0, .74), (.012, .87), (.035, .945), (.08, .985), (.16, 1), (.84, 1), (.92, .985), (.97, .94), (.99, .86), (1, .76)], grille='wide'),
 'hatch': dict(L=4.28, W=1.79, H=1.46, r=.325, FO=.88, WB=2.63, rock=.27, mid=.60, drop=.10, beltF=.90, beltR=.98,
   top=[(0, .75), (.02, .78), (.07, .815), (.16, .86), (.31, .935), (.33, .96), (.47, 1.41), (.55, 1.46), (.82, 1.44), (.88, 1.36), (.95, 1.06), (.985, 1.02), (1, .97)],
   cowl=.31, wstop=.47, roofend=.82, deck=.95, side_end=.865, pillars=[('B', .565)], doors=[.32, .565, .735],
   front=(.26, .37, .51, .61, .725), rear=(.32, .44, .55, .86, 1.0), wroof=[(.31, .93), (.47, .80), (.82, .80), (.95, .86)],
   plan=[(0, .74), (.012, .87), (.035, .945), (.08, .985), (.16, 1), (.86, 1), (.93, .985), (.975, .94), (.99, .86), (1, .78)], grille='slim'),
 'suv': dict(L=4.88, W=1.98, H=1.80, r=.39, FO=.90, WB=2.92, rock=.40, mid=.74, drop=.11, beltF=1.10, beltR=1.16,
   top=[(0, .90), (.02, .97), (.06, 1.03), (.15, 1.07), (.29, 1.11), (.31, 1.13), (.42, 1.73), (.48, 1.80), (.90, 1.79), (.93, 1.72), (.975, 1.28), (.99, 1.20), (1, 1.12)],
   cowl=.29, wstop=.42, roofend=.905, deck=.975, side_end=.925, pillars=[('B', .53), ('C', .735)], doors=[.30, .53, .735],
   front=(.38, .50, .64, .80, .92), rear=(.42, .55, .70, 1.00, 1.12), wroof=[(.29, .95), (.42, .86), (.90, .86), (.975, .90)],
   plan=[(0, .80), (.01, .90), (.03, .96), (.07, .99), (.14, 1), (.88, 1), (.94, .99), (.98, .955), (.995, .9), (1, .82)], grille='tall', clad=True, rails=True),
 'sports': dict(L=4.50, W=1.94, H=1.25, r=.345, FO=1.0, WB=2.55, rock=.20, mid=.46, drop=.09, beltF=.78, beltR=.88,
   top=[(0, .52), (.02, .58), (.06, .64), (.20, .72), (.36, .79), (.38, .815), (.53, 1.21), (.60, 1.25), (.69, 1.20), (.85, .925), (.92, .905), (.98, .87), (1, .80)],
   cowl=.36, wstop=.53, roofend=.70, deck=.86, side_end=.80, pillars=[('B', .655)], doors=[.33, .655],
   front=(.18, .27, .37, .46, .54), rear=(.24, .33, .46, .66, .80), wroof=[(.36, .86), (.53, .70), (.69, .70), (.86, .86)],
   plan=[(0, .70), (.012, .84), (.04, .93), (.12, .975), (.30, .95), (.45, .93), (.68, .995), (.82, 1), (.93, .975), (.98, .91), (.995, .82), (1, .72)], grille='intake', spoiler=True),
 'hyper': dict(L=4.544, W=2.038, H=1.212, r=.365, FO=.98, WB=2.711, rock=.19, mid=.42, drop=.08, beltF=.80, beltR=.93,
   top=[(0, .60), (.03, .655), (.10, .725), (.20, .785), (.33, .84), (.36, .875), (.50, 1.165), (.56, 1.212), (.66, 1.17), (.80, .995), (.88, .945), (.96, .905), (1, .845)],
   cowl=.36, wstop=.50, roofend=.66, deck=.86, side_end=.60, pillars=[], doors=[.31, .555],
   front=(.16, .25, .36, .455, .555), rear=(.25, .35, .50, .72, .845), wroof=[(.36, .86), (.50, .63), (.62, .60), (.78, .66), (.86, .80)],
   plan=[(0, .60), (.012, .79), (.04, .90), (.10, .975), (.18, 1.0), (.25, 1.0), (.36, .94), (.50, .925), (.62, .965), (.72, 1.0), (.86, 1.0), (.94, .975), (.985, .89), (1, .77)],
   grille='horseshoe', cline=True, lightbar=True, twotone=True),
 'police': dict(L=4.71, W=1.83, H=1.48, r=.335, FO=.84, WB=2.85, rock=.27, mid=.60, drop=.10, beltF=.90, beltR=.98,
   top=[(0, .745), (.02, .775), (.07, .81), (.16, .85), (.30, .92), (.315, .945), (.44, 1.40), (.5, 1.46), (.88, 1.44), (.93, 1.30), (.975, 1.03), (.99, .99), (1, .94)],
   cowl=.30, wstop=.44, roofend=.885, deck=.975, side_end=.905, pillars=[('B', .535), ('C', .715)], doors=[.285, .535, .715],
   front=(.25, .36, .50, .60, .715), rear=(.33, .45, .57, .84, .98), wroof=[(.30, .93), (.44, .79), (.88, .79), (.975, .88)],
   plan=[(0, .74), (.012, .87), (.035, .945), (.08, .985), (.16, 1), (.86, 1), (.93, .985), (.975, .94), (.99, .86), (1, .78)], grille='wide', rails=True),
 'cab': dict(L=4.57, W=1.95, H=1.83, r=.345, FO=.74, WB=2.89, rock=.30, mid=.66, drop=.10, beltF=1.02, beltR=1.06,
   top=[(0, .80), (.03, .88), (.08, .94), (.16, .98), (.26, 1.01), (.28, 1.05), (.37, 1.70), (.42, 1.80), (.47, 1.83), (.88, 1.82), (.925, 1.74), (.965, 1.30), (.99, 1.12), (1, 1.04)],
   cowl=.27, wstop=.40, roofend=.92, deck=.965, side_end=.915, pillars=[('B', .485), ('C', .735)], doors=[.27, .485, .735],
   front=(.32, .44, .55, .66, .84), rear=(.36, .47, .60, .90, 1.02), wroof=[(.27, .92), (.40, .84), (.92, .84), (.965, .88)],
   plan=[(0, .66), (.015, .80), (.04, .90), (.09, .965), (.17, 1), (.86, 1), (.93, .985), (.975, .94), (.99, .87), (1, .78)], grille='cab', round_lamps=True),
}
p = S[TYPE]; L, W, H, R = p['L'], p['W'], p['H'], p['r']; W2 = W / 2
Y = lambda t: -L / 2 + t * L
top = pchip(p['top']); plan = pchip(p['plan']); wroof = pchip([(0, p['wroof'][0][1])] + p['wroof'] + [(1, p['wroof'][-1][1])])
F, Rr = p['front'], p['rear']; rk, md = p['rock'], p['mid']
beltb = pchip([(0, F[4]), (.06, F[4] + .03), (p['cowl'], p['beltF']), (p['deck'], p['beltR']), (.95, Rr[4] + .02), (1, Rr[4])])
def heights(t):
    """p2..p6 heights at section t: nose fascia -> body -> tail fascia"""
    body = [rk, rk + .10, md, beltb(t) - p['drop'], beltb(t)]
    fe, re = sm(0, .13, t), sm(1, .87, t)
    out = []
    for k in range(5):
        v = body[k] if k >= 3 else lerp(F[k], body[k], fe)
        if k < 3: v = lerp(Rr[k], v, re)
        out.append(v)
    out[3] = lerp(F[3], out[3], sm(0, .10, t)); out[3] = lerp(Rr[3], out[3], sm(1, .9, t))
    return out
def gh(t): return sm(p['cowl'] - .005, p['cowl'] + .02, t) * (1 - sm(p['deck'] - .02, p['deck'] + .005, t))
def ring0(t):
    """half section (x>=0) from bottom centre to top centre: 11 points"""
    w = W2 * plan(t); z2, z3, z4, z5, z6 = heights(t); zt = max(top(t), z6 + .01); zu = z2 - .05
    g = gh(t); wr = W2 * wroof(t)
    k9 = .92 if (t < p['wstop'] or t > p['roofend']) else .74
    hood = [(w - .035, z6 + .012), (w * .66, lerp(z6, zt, .72)), (w * .33, zt - .006)]
    green = [(w - .065, z6 + .022), (wr, zt - .075), (wr * k9, zt - .016)]
    up = [(lerp(hood[i][0], green[i][0], g), lerp(hood[i][1], green[i][1], g)) for i in range(3)]
    return [(0, zu), (w * .80, zu), (w * .93, z2), (w * .962, z3), (w * .992, z4), (w, z5), (w - .03, z6)] + up + [(0, zt)]
# wheel wells: cut per side from x=±XI outward only (the hood, tunnel and cabin between them stay whole). XI stays outside
# the tyre's inner corner (front tyres steer up to .34 rad in the engine; tyre half-width .335r, corner radius ~.6r)
TW = (p['FO'] / L, (p['FO'] + p['WB']) / L)
track = min(W2 * plan(TW[0]), W2 * plan(TW[1])) - .32 * R - .055
XI = (track - .60 * R - .03, track - .34 * R - .03)
RC = R + .055                                              # arch cut radius about the axle
ZF = 2 * R + .055 + .045                                   # bodywork over a well must stay above the cut top (+ skin)
FEND = []                                                  # fender lift per axle for cage points 6, 7, 8 (only where too low)
for a in (0, 1):
    h = ring0(TW[a]); d6, d7 = max(0, ZF - h[6][1]), max(0, ZF + .012 - h[7][1]); d8 = max(0, ZF - h[8][1]) if h[8][0] > XI[a] - .1 else 0
    FEND.append((d6, d7, d8))
    if d6 + d7 + d8 > 0: print('fender lift axle', a, [round(v, 3) for v in (d6, d7, d8)])
def ring(t):
    h = ring0(t)
    for a in (0, 1):
        b = sm(1.6 * RC, .55 * RC, abs(t - TW[a]) * L); d6, d7, d8 = FEND[a]
        if b <= 0 or d6 + d7 + d8 == 0: continue
        h[5] = (h[5][0], h[5][1] + .4 * d6 * b); h[6] = (h[6][0], h[6][1] + d6 * b); h[7] = (h[7][0], h[7][1] + d7 * b); h[8] = (h[8][0], h[8][1] + d8 * b)
    return h
# ------------------------------------------------------------------ sections (with door shut-line pairs and pillar strips)
G = .0028
base = [0, .006, .015, .028, .045, .065, .09, .115] + [.14 + i * (.72 / 26) for i in range(27)] + [.885, .91, .935, .955, .972, .986, .994, 1]
feat = [p['cowl'] - .012, p['cowl'], p['cowl'] + .012, p['wstop'], p['roofend'], p['deck'], p['deck'] + .006, p['side_end']]
for d in p['doors']: feat += [d - G, d + G]
for kind, tp in p['pillars']: feat += [tp - .014, tp + .014]
ts = sorted(set(round(x, 4) for x in base + feat if 0 <= x <= 1))
ts = [t for i, t in enumerate(ts) if i == 0 or t - ts[i - 1] > .0015]
C_T0, C_A, C_Z0, C_B = .50, .19, .74, .46
def c_rear(z): return C_T0 + C_A * math.sqrt(max(0.0, 1 - ((z - C_Z0) / C_B) ** 2)) if abs(z - C_Z0) < C_B else C_T0
def two_tone(t, s, z, base):
    if base not in ('Paint', 'Gap'): return base
    if s >= 8 and t > p['cowl'] + .01: return 'Carbon'                 # roof, engine cover
    if s <= 2: return 'Carbon' if t > .30 else base                    # dark sills
    if t > c_rear(z) or z > C_Z0 + C_B: return 'Carbon'                # rear haunches behind the C
    if t > .57 and .42 < z < 1.0: return 'Grille'                      # side air intake inside the C
    return base
def classify(t, s, side_glass_range):
    """material of the cage face in segment s (0..9) whose mid-section is t"""
    cw, ws, re, dk, se = p['cowl'], p['wstop'], p['roofend'], p['deck'], p['side_end']
    in_gap = any(abs(t - d) < G for d in p['doors'])
    green = cw < t < dk
    if s <= 1: return 'Under'
    if s == 2: return 'Black' if p.get('clad') else ('Gap' if in_gap else 'Paint')
    if s in (3, 4, 5):
        if in_gap and cw - .03 < t < dk + .02: return 'Gap'
        if p.get('clad') and s == 3: return 'Black'
        if s == 5 and t < .045 and not p.get('round_lamps'): return 'Lens'
        if s == 5 and t > .965: return 'LightR'
        return 'Paint'
    if s == 6: return 'Black' if (cw + .01 < t < se) else 'Paint'
    if s == 7:
        if not green: return 'Paint'
        if cw - .012 < t < cw + .012: return 'Black'
        for kind, tp in p['pillars']:
            if abs(t - tp) < .014: return 'Black' if kind == 'B' else 'Paint'
        return 'Glass' if cw + .012 < t < se else 'Paint'
    if s == 8: return 'Black' if cw - .012 < t < cw + .012 else 'Paint'
    if s == 9:
        if cw - .012 < t < cw + .006: return 'Black'
        if cw + .006 < t < ws - .004: return 'Glass'
        if re + .004 < t < dk - .004: return 'Glass'
        if dk < t < dk + .006: return 'Gap'
        return 'Paint'
    return 'Paint'
# ------------------------------------------------------------------ build cage
bm = bmesh.new(); rings = []; tags = {}
for t in ts:
    half = ring(t); y = Y(t)
    full = [(x, z) for x, z in half] + [(-x, z) for x, z in reversed(half[1:-1])]
    fz0, fz1 = heights(t)[0], max(top(t), heights(t)[4])
    lean = lambda z: .085 * sm(fz0, fz1, z)
    ef, er = 1 - sm(0, .06, t), sm(.94, 1, t)
    rings.append([bm.verts.new((x, y + lean(z) * ef - lean(z) * .6 * er, z)) for x, z in full])
n = len(rings[0]); NH = 10
for i in range(len(ts) - 1):
    tm = (ts[i] + ts[i + 1]) / 2
    for k in range(n):
        f = bm.faces.new((rings[i][k], rings[i][(k + 1) % n], rings[i + 1][(k + 1) % n], rings[i + 1][k]))
        s = k if k < NH else (n - 1 - k)
        tags[f] = classify(tm, s, None)
        if p.get('twotone'):
            hr = ring(tm); tags[f] = two_tone(tm, s, (hr[s][1] + hr[s + 1][1]) / 2, tags[f])
COLS = [0, .2, .36, .47, .6, .8, 1.0]
def cap(rg, front):
    """grid-fill the end ring: rows = ring segments, columns at fixed width fractions; returns faces with (row, colfrac)"""
    hl = rg[:NH + 1]; hr = [rg[0]] + rg[NH + 1:][::-1] + [rg[NH]]   # left/right halves bottom->top, sharing p0 and p10
    fr = [-c for c in COLS[::-1]] + COLS[1:]
    grid = []
    for k in range(NH + 1):
        a, b = hr[k].co, hl[k].co
        if k in (0, NH): grid.append([hl[k]] * len(fr)); continue
        row = []
        for c in fr:
            if c == 1.0: row.append(hl[k])
            elif c == -1.0: row.append(hr[k])
            else:
                u = (c + 1) / 2; co = a.lerp(b, u); co.y += (-1 if front else 1) * .045 * (1 - c * c) * sm(1, 4, k); row.append(bm.verts.new(co))
        grid.append(row)
    out = []
    for k in range(NH):
        for j in range(len(fr) - 1):
            q = [grid[k][j], grid[k][j + 1], grid[k + 1][j + 1], grid[k + 1][j]]
            uq = []
            for v in q:
                if v not in uq: uq.append(v)
            if len(uq) < 3: continue
            f = bm.faces.new(uq if not front else uq[::-1]); out.append((f, k, (abs(fr[j]) + abs(fr[j + 1])) / 2))
    return out
def front_mat(k, c):
    g = p['grille']
    if k <= 1: return 'Black'
    if k == 2: return 'Grille' if (c < .8 and g in ('intake', 'wide', 'slim', 'tall')) else 'Paint'
    if g == 'horseshoe':
        if 2 <= k <= 6 and c < .2: return 'Grille'
        if k in (2, 3) and .3 < c < .9: return 'Grille'
        if k == 5 and c >= .45: return 'Lens'
        return 'Black' if k <= 1 else 'Paint'
    if k == 3:
        if c < .36 and not p.get('round_lamps'): return 'PlateF'
        if g == 'intake' and c < .8: return 'Grille'
        return 'Paint'
    if k == 4: return 'Grille' if ((g in ('wide', 'tall') and c < .47) or (g == 'slim' and c < .36)) else 'Paint'
    if k == 5:
        if c >= .6 and not p.get('round_lamps'): return 'Lens'
        if g in ('wide', 'tall', 'slim') and c < .47: return 'Grille'
        return 'Paint'
    return 'Paint'
def rear_mat(k, c):
    if k <= 1: return 'Black'
    if k == 2: return 'Black'
    if k == 3: return 'Paint'
    if k == 4: return 'PlateR' if c < .36 else 'Paint'
    if k == 5: return 'LightR' if (c >= .6 or p.get('lightbar')) else ('Clear' if c >= .47 and TYPE != 'sports' else 'Paint')
    return 'Paint'
for f, k, c in cap(rings[0], True): tags[f] = front_mat(k, c)
for f, k, c in cap(rings[-1], False): tags[f] = rear_mat(k, c) if not p.get('twotone') else ('Carbon' if rear_mat(k, c) == 'Paint' else rear_mat(k, c))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
cl = bm.edges.layers.float.get('crease_edge') or bm.edges.layers.float.new('crease_edge')
CRE = {2: .45, 5: .7, 6: .9, 7: .8, 8: .55}
for i in range(len(rings) - 1):
    for k, cv in CRE.items():
        for kk in (k, n - k):
            e = bm.edges.get((rings[i][kk], rings[i + 1][kk]))
            if e: e[cl] = cv
for rg in (rings[0], rings[-1]):
    for k in range(n):
        e = bm.edges.get((rg[k], rg[(k + 1) % n]))
        if e: e[cl] = .5
# ------------------------------------------------------------------ to mesh, subdivide, cut arches, recess regions
ORDER = ['Paint', 'Glass', 'Black', 'Under', 'Gap', 'Grille', 'Lens', 'LightF', 'LightR', 'Clear', 'PlateF', 'PlateR', 'Chrome', 'Livery', 'Carbon']
bm.faces.index_update(); flut = {f.index: tags.get(f, 'Paint') for f in bm.faces}
me = bpy.data.meshes.new('Body'); bm.to_mesh(me); bm.free()
body = bpy.data.objects.new('Body', me); bpy.context.scene.collection.objects.link(body)
for nm in ORDER: me.materials.append(MATS[nm])
for poly in me.polygons: poly.material_index = ORDER.index(flut[poly.index]); poly.use_smooth = True
def apply_mod(ob, mtype, **kw):
    m = ob.modifiers.new(mtype, mtype)
    for k, v in kw.items(): setattr(m, k, v)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True); bpy.ops.object.modifier_apply(modifier=m.name); ob.select_set(False)
apply_mod(body, 'SUBSURF', levels=1, render_levels=2)
def prim(name, matname, build, smooth=True):
    bm = bmesh.new(); build(bm); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob); me.materials.append(MATS[matname])
    for pp in me.polygons: pp.use_smooth = smooth
    return ob
def cube(bm, c, s, rx=0.0, rz=0.0, bev=0.0):
    r = bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation(Vector(c)) @ Matrix.Rotation(rz, 4, 'Z') @ Matrix.Rotation(rx, 4, 'X') @ Matrix.Diagonal((s[0], s[1], s[2], 1)))
    if bev: bmesh.ops.bevel(bm, geom=[e for e in bm.edges if all(v in r['verts'] for v in e.verts)], offset=bev, segments=2, affect='EDGES', profile=.5)
def cyl(bm, c, r, depth, axis='X', seg=20, r2=None):
    rot = {'X': Matrix.Rotation(math.pi / 2, 4, 'Y'), 'Y': Matrix.Rotation(math.pi / 2, 4, 'X'), 'Z': Matrix.Identity(4)}[axis]
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=depth, matrix=Matrix.Translation(Vector(c)) @ rot)
yf, yr = -L / 2 + p['FO'], -L / 2 + p['FO'] + p['WB']
for wy, xi in ((yf, XI[0]), (yr, XI[1])):
    cut = prim('cut', 'Black', lambda bm, wy=wy, xi=xi: [cyl(bm, (sx * (xi + W2 + .4) / 2, wy, R), RC, W2 + .4 - xi, 'X', 40) for sx in (-1, 1)])
    mo = body.modifiers.new('b', 'BOOLEAN'); mo.object = cut; mo.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = body; bpy.ops.object.modifier_apply(modifier=mo.name); bpy.data.objects.remove(cut)
# recess glass/lights/grilles/plates with insets (seals and bezels come from the inset rims)
bm = bmesh.new(); bm.from_mesh(me); mi = {nm: i for i, nm in enumerate(ORDER)}
def region(names): return [f for f in bm.faces if ORDER[f.material_index] in names]
for names, th, dp, rim in ((('Glass',), .012, -.014, 'Black'), (('Lens', 'LightF', 'LightR', 'Clear'), .008, -.010, 'Black'), (('Grille',), .014, -.035, 'Chrome' if p['grille'] in ('tall', 'cab', 'horseshoe') else 'Black'),
                           (('PlateF', 'PlateR'), .006, .006, 'Black')):
    fs = region(names)
    if not fs: continue
    r = bmesh.ops.inset_region(bm, faces=fs, thickness=th, depth=dp, use_even_offset=True)
    for f in r['faces']: f.material_index = mi[rim]
bm.to_mesh(me); bm.free()
for poly in me.polygons: poly.use_smooth = True
if TYPE == 'police':   # Battenburg panels on the doors and wings (uv drives the checks in the engine)
    li = ORDER.index('Livery'); uv = me.uv_layers.new(name='UVMap')
    for poly in me.polygons:
        c = poly.center
        if poly.material_index == 0 and abs(poly.normal.x) > .6 and rk + .14 < c.z < beltb(.5) - p['drop'] - .02 and -L / 2 + .25 < c.y < L / 2 - .25: poly.material_index = li
    for poly in me.polygons:
        for l in poly.loop_indices:
            v = me.vertices[me.loops[l].vertex_index].co; uv.data[l].uv = (v.y / .55, (v.z - .3) / .55)
# ------------------------------------------------------------------ details
zb = beltb(.5)
def liner(bm, wy, sx, xi):   # inside of the wheel well: arched roof facing the wheel + inner wall (open below, never encloses the tyre)
    rr = R + .042; th = [math.radians(-12 + 204 * k / 24) for k in range(25)]; xo = sx * (W2 * plan((wy + L / 2) / L) - .015); xi = sx * (xi + .005)
    A = [(wy + rr * math.cos(a), R + rr * math.sin(a)) for a in th]
    o = [bm.verts.new((xo, y, z)) for y, z in A]; i = [bm.verts.new((xi, y, z)) for y, z in A]
    for k in range(len(A) - 1):
        f = bm.faces.new((o[k], o[k + 1], i[k + 1], i[k])); f.normal_update()
        if f.normal.dot(Vector((xi, wy, R)) - f.calc_center_median()) < 0: f.normal_flip()
    w = bm.faces.new(i + [bm.verts.new((xi, wy, R - .05))]); w.normal_update()
    if w.normal.x * sx < 0: w.normal_flip()
for wy, xi in ((yf, XI[0]), (yr, XI[1])):   # arch liners and lips
    for sx in (-1, 1): prim('liner', 'Under', lambda bm, wy=wy, sx=sx, xi=xi: liner(bm, wy, sx, xi), smooth=False)
    def lip(bm, wy=wy):
        for sx in (-1, 1):
            segs = 18; vs = []
            for j in range(segs + 1):
                a = math.radians(-8) + (math.radians(188)) * j / segs; ca, sa = math.cos(a), math.sin(a)
                rr = R + .058; x = sx * (W2 * plan((wy + L / 2) / L) - .005)
                vs.append([bm.verts.new((x + sx * dx, wy + ca * (rr + dr), R + sa * (rr + dr))) for dx, dr in ((0, 0), (.035, 0), (.035, .03), (0, .03))])
            for j in range(segs):
                for q in range(4): bm.faces.new((vs[j][q], vs[j][(q + 1) % 4], vs[j + 1][(q + 1) % 4], vs[j + 1][q]))
    prim('lip', 'Black' if p.get('clad') else 'Paint', lip)
cw_y = Y(p['cowl']); dk_y = Y(p['deck'])
for sx in (-1, 1):   # mirrors on the doors at the A-pillar base, door handles, side repeaters
    mx = sx * (W2 * .99); my = cw_y + .16; mz = zb + .07
    prim('mirror', 'Carbon' if p.get('twotone') else 'Paint', lambda bm, sx=sx: cube(bm, (sx * (W2 + .09), my, mz + .02), (.17, .09, .11), bev=.03))
    prim('mglass', 'Chrome', lambda bm, sx=sx: cube(bm, (sx * (W2 + .09), my + .048, mz + .02), (.14, .008, .085)))
    prim('stalk', 'Black', lambda bm, sx=sx: cube(bm, (sx * (W2 + .02), my, mz - .015), (.08, .05, .035)))
    for d0, d1 in zip(p['doors'][:-1], p['doors'][1:]) if len(p['doors']) > 2 else [(p['doors'][0], p['doors'][1])]:
        hy = Y(d1) - .18
        prim('handle', 'Chrome' if TYPE in ('cab', 'saloon') else 'Paint', lambda bm, sx=sx, hy=hy: cube(bm, (sx * (W2 * plan((hy + L / 2) / L) + .004), hy, zb - p['drop'] - .03), (.025, .15, .03), bev=.008))
    ry = yf + R + .18
    prim('rep', 'Amber', lambda bm, sx=sx, ry=ry: cube(bm, (sx * (W2 * plan((ry + L / 2) / L) + .003), ry, zb - p['drop'] + .02), (.012, .06, .025), bev=.004))
if not p.get('round_lamps'):
    capw = W2 * plan(0); yc = lambda x, z=(F[3] + F[4]) / 2: -L / 2 - .045 * (1 - min(1, abs(x) / capw) ** 2) + .085 * sm(F[0], max(top(0), F[4]), z)
    zlo, zhi = F[3], F[4]
    for sx in (-1, 1):
        for xf in ((.66, .75, .84, .93) if p.get('cline') else (.70, .86)):
            x = sx * capw * xf
            pr = .022 if p.get('cline') else .036
            prim('proj', 'Chrome', lambda bm, x=x: cyl(bm, (x, yc(x) + .02, (zlo + zhi) / 2 + .005), pr, .03, 'Y', 18))
            prim('projl', 'LightF', lambda bm, x=x: cyl(bm, (x, yc(x) + .002, (zlo + zhi) / 2 + .005), pr * .66, .012, 'Y', 18))
        def drl(bm, sx=sx):
            n = 8; vs = []
            for j in range(n + 1):
                x = sx * capw * (.62 + .38 * j / n); vs.append([bm.verts.new((x, yc(x, zlo + .02) - .002 + dy, zlo + .014 + dz)) for dy, dz in ((0, 0), (0, .012), (.01, .012), (.01, 0))])
            for j in range(n):
                for q in range(4): bm.faces.new((vs[j][q], vs[j][(q + 1) % 4], vs[j + 1][(q + 1) % 4], vs[j + 1][q]))
        prim('drl', 'LightF', drl)
if p.get('cline'):
    def surf_x(t, z):   # body half-width at height z on section t (from the cage ring)
        h = ring(t)
        for a, b in zip(h[2:8], h[3:9]):
            if a[1] <= z <= b[1]: return lerp(a[0], b[0], (z - a[1]) / max(1e-6, b[1] - a[1]))
        return h[8][0] if z > h[8][1] else h[2][0]
    path = [(lerp(.42, C_T0, k / 6), top(lerp(.42, C_T0, k / 6)) - .09) for k in range(6)]
    for k in range(25):
        th = math.pi / 2 - k / 24 * math.pi; path.append((C_T0 + C_A * math.cos(th), min(top(C_T0) - .09, C_Z0 + C_B * math.sin(th))))
    path += [(lerp(C_T0, .31, k / 8), C_Z0 - C_B) for k in range(1, 9)]
    def cline(bm):
        for sx in (-1, 1):
            vs = []
            for t, z in path:
                x = sx * (surf_x(t, z) + .006); y = Y(t)
                vs.append([bm.verts.new((x + sx * dx, y + dy, z + dz)) for dx, dy, dz in ((0, 0, -.022), (.014, 0, -.022), (.014, 0, .022), (0, 0, .022))])
            for j in range(len(vs) - 1):
                for q in range(4): bm.faces.new((vs[j][q], vs[j][(q + 1) % 4], vs[j + 1][(q + 1) % 4], vs[j + 1][q]))
    prim('cline', 'Chrome', cline)
    prim('fin', 'Carbon', lambda bm: cube(bm, (0, Y(.66), top(.66) + .025), (.025, (.80 - .52) * L, .06), bev=.008))       # roof spine
    prim('spine', 'Paint', lambda bm: cube(bm, (0, Y(.19), top(.19) + .006), (.05, (.33 - .05) * L, .03), rx=.09, bev=.01))   # hood centre ridge
    prim('wing', 'Carbon', lambda bm: cube(bm, (0, L / 2 - .32, top(.93) + .035), (W - .5, .42, .025), rx=-.05, bev=.008))     # flush active wing
    for k in (-1.5, -.5, .5, 1.5): prim('pipe', 'Chrome', lambda bm, k=k: cyl(bm, (k * .085, L / 2 - .03, Rr[0] + .07), .045, .14, 'Y', 14))
    for k in range(5): prim('diff', 'Black', lambda bm, k=k: cube(bm, (-.6 + k * .3, L / 2 - .2, Rr[0] - .03), (.02, .4, .12)))
# wipers
for sx in (-.28, .28):
    prim('wiper', 'Black', lambda bm, sx=sx: cube(bm, (sx, cw_y + .05, top(p['cowl']) + .03), (.55, .02, .015), rz=.12 * (1 if sx > 0 else -1)))
# interior: tub, dashboard, seats, steering wheel (right-hand drive: driver on -x)
seat_y = cw_y + (1.15 if TYPE != 'sports' else 1.0); rseat_y = seat_y + .88
fl = rk + .14
def tub(bm):   # cabin tub, narrowed where it passes a wheel well so nothing pokes into the open wells
    ys = sorted(set([cw_y + .04, dk_y - .04] + [v for wy in (yf, yr) for v in (wy - RC - .02, wy + RC + .02) if cw_y + .04 < v < dk_y - .04]))
    for y0, y1 in zip(ys[:-1], ys[1:]):
        wd = min([W - .26] + [2 * (XI[a] - .01) for a, wy in enumerate((yf, yr)) if abs((y0 + y1) / 2 - wy) < RC + .02])
        cube(bm, (0, (y0 + y1) / 2, (fl + zb - .06) / 2), (wd, y1 - y0, zb - .06 - fl))
prim('tub', 'Interior', tub)
prim('dash', 'Interior', lambda bm: cube(bm, (0, cw_y + .32, zb - .1), (W - .3, .44, .17), bev=.05))
def seat(bm, x, y, w=.52):
    room = top(min(1, max(0, (y + .36 + L / 2) / L))) - .08 - fl   # keep headrests under the roof line
    k = min(1.0, room / 1.1)
    cube(bm, (x, y, fl + .26 * k), (w, .52, .12), bev=.04); cube(bm, (x, y + .3, fl + .62 * k), (w, .12, .62 * k), rx=-.22, bev=.04)
    if k > .8: cube(bm, (x, y + .36, fl + 1.0 * k), (.26, .1, .18), rx=-.22, bev=.04)
prim('seats', 'Seat', lambda bm: (seat(bm, -.38, seat_y), seat(bm, .38, seat_y), (seat(bm, 0, rseat_y, min(W - .4, 2 * XI[1] - .04) if rseat_y + .45 > yr - RC else W - .4) if TYPE != 'sports' else None)))
def wheel_(bm):
    seg, rr, rt = 24, .19, .02; vs = []
    for i in range(seg):
        a = i / seg * math.tau; row = []
        for j in range(8):
            b = j / 8 * math.tau; rad = rr + rt * math.cos(b)
            row.append(bm.verts.new((-.38 + math.cos(a) * rad, cw_y + .62 + rt * math.sin(b), zb + .02 + math.sin(a) * rad)))
        vs.append(row)
    for i in range(seg):
        for j in range(8): bm.faces.new((vs[i][j], vs[(i + 1) % seg][j], vs[(i + 1) % seg][(j + 1) % 8], vs[i][(j + 1) % 8]))
    bmesh.ops.rotate(bm, verts=[v for r_ in vs for v in r_], cent=(-.38, cw_y + .62, zb + .02), matrix=Matrix.Rotation(-.45, 3, 'X'))
prim('steer', 'Black', wheel_)
# exhaust, aerial, model specifics
for sx in ((-1, 1) if TYPE in ('sports', 'saloon') else (1,)):
    prim('exhaust', 'Chrome', lambda bm, sx=sx: cyl(bm, (sx * (W2 * .55), L / 2 - .02, Rr[0] + .06), .042, .12, 'Y', 16))
if TYPE not in ('cab',):
    prim('fin', 'Black', lambda bm: cube(bm, (0, Y(p['roofend']) - .12, top(p['roofend'] - .03) + .03), (.06, .2, .07), rx=.3, bev=.02))
if p.get('rails'):
    for sx in (-1, 1): prim('rail', 'Black' if TYPE == 'police' else 'Chrome', lambda bm, sx=sx: cube(bm, (sx * (W2 * wroof(.6) - .06), (Y(p['wstop']) + Y(p['roofend'])) / 2, H + .03), (.04, (p['roofend'] - p['wstop']) * L * .9, .04), bev=.012))
if p.get('spoiler') and not p.get('twotone'):
    prim('spoiler', 'Paint', lambda bm: cube(bm, (0, L / 2 - .2, top(.96) + .1), (W - .32, .26, .03), rx=-.08, bev=.01))
    for sx in (-1, 1): prim('post', 'Black', lambda bm, sx=sx: cube(bm, (sx * .55, L / 2 - .2, top(.96) + .05), (.05, .08, .1)))
if p.get('round_lamps'):   # London cab face: round headlamps in chrome bezels, chrome grille and bumper, amber TAXI sign
    zl = F[3] + .03
    for sx in (-1, 1):
        prim('bezel', 'Chrome', lambda bm, sx=sx: cyl(bm, (sx * .62, -L / 2 + .07, zl), .125, .07, 'Y', 28))
        prim('lamp', 'LightF', lambda bm, sx=sx: cyl(bm, (sx * .62, -L / 2 + .035, zl), .105, .02, 'Y', 28))
        prim('ind', 'Amber', lambda bm, sx=sx: cube(bm, (sx * .78, -L / 2 + .09, F[2] - .02), (.09, .03, .05), bev=.01))
    prim('grillef', 'Chrome', lambda bm: cyl(bm, (0, -L / 2 + .03, F[3]), .27, .035, 'Y', 32))
    def bars(bm):
        for k in range(-5, 6): cube(bm, (k * .042, -L / 2 + .02, F[3]), (.016, .03, .36 * math.sqrt(max(.05, 1 - (k / 6) ** 2))))
    prim('grilleb', 'Grille', bars)
    prim('bumper', 'Chrome', lambda bm: cube(bm, (0, -L / 2 + .03, F[1] - .02), (W - .2, .1, .1), bev=.03))
    prim('bumperR', 'Chrome', lambda bm: cube(bm, (0, L / 2 - .03, Rr[1] - .02), (W - .2, .1, .1), bev=.03))
    prim('plate', 'PlateF', lambda bm: cube(bm, (0, -L / 2 + .07, F[1] - .14), (.52, .02, .11)))
    prim('taxi', 'Taxi', lambda bm: cube(bm, (0, Y(p['wstop']) + .2, H + .07), (.5, .16, .13), bev=.03))
if TYPE == 'police':   # slim LED bar
    prim('bar', 'Black', lambda bm: cube(bm, (0, Y(p['wstop']) + .45, H + .04), (1.2, .26, .05), bev=.015))
    prim('barL', 'BarBlue', lambda bm: cube(bm, (-.33, Y(p['wstop']) + .45, H + .1), (.54, .22, .08), bev=.02))
    prim('barR', 'BarRed', lambda bm: cube(bm, (.33, Y(p['wstop']) + .45, H + .1), (.54, .22, .08), bev=.02))
# ------------------------------------------------------------------ join + export
objs = [o for o in bpy.data.objects if o.type == 'MESH']
for o in objs: o.select_set(True)
bpy.context.view_layer.objects.active = body; bpy.ops.object.join()
car = bpy.context.view_layer.objects.active; car.name = TYPE
try: car.data.set_sharp_from_angle(angle=math.radians(50))
except Exception: pass
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_apply=True, export_yup=True)
import json, os
SPEC = os.path.join(os.path.dirname(OUT), 'specs.json'); sp = json.load(open(SPEC)) if os.path.exists(SPEC) else {}
tf, tr = TW
sp[TYPE] = dict(L=L, W=W, H=H, r=R, wz=[round(tf, 4), round(tr, 4)], track=round(track, 3))
json.dump(sp, open(SPEC, 'w'), indent=1)
print('exported', OUT, len(car.data.polygons), 'faces', sum(len(pl.vertices) - 2 for pl in car.data.polygons), 'tris')
