"""Builds the whole city in Blender from assets/city/layout.json -> assets/city/city.glb (+ eye.glb).
Run: python3 -I tools/blender/city.py"""
import sys, os, math, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from citylib import *
L = json.load(open(os.path.join(ROOT, 'assets', 'city', 'layout.json')))
HALF, RIVER, RW, RWR, CH = L['half'], L['river'], L['rw'], L['rwr'], L['chunk']
reset()
CHUNKS = {}
def ck(x, z):
    k = (math.floor((x + HALF + 200) / CH), math.floor((z + HALF + 200) / CH))
    if k not in CHUNKS: CHUNKS[k] = (Acc(), Acc())
    return CHUNKS[k]
def O(x, z): return ck(x, z)[0]
def Gl(x, z): return ck(x, z)[1]
BRICKS = ['#b65a3c', '#a5583f', '#8c4a36', '#c9a86a', '#bf9b62', '#9a6b4f', '#b8714f', '#c2a070']
WINLIT = [(1.0, .82, .52, 1), (1.0, .9, .7, 1), (.85, .9, 1.0, 1)]
def glass_face(acc, pts, rnd, lit_p=.35):
    acc.face(pts, 0, WHITE, ao=False)
    c = rnd.choice(WINLIT) if rnd.random() < lit_p else (0, 0, 0, 1)
    for i in range(len(pts)): acc.C[-1 - i] = c
# ---------------------------------------------------------------- buildings
def facade(acc, gacc, lot, face, wall, tint, rnd, ground_shop):
    """Exterior wall with real window openings: piers, bands, reveals, glass, frames, sills."""
    x0, x1, z0, z1, top = lot['x0'], lot['x1'], lot['z0'], lot['z1'], lot['htop']
    if face in ('z0', 'z1'):
        a, b = x0, x1; zc = z1 if face == 'z1' else z0; sgn = 1 if face == 'z1' else -1
        P = lambda u, y, d=0: (u, y, zc - sgn * d) if True else None
        def Q(u0, u1, y0, y1, d=0, lay=wall, t=tint, acc_=None):
            pts = [(u0, y0, zc - sgn * d), (u1, y0, zc - sgn * d), (u1, y1, zc - sgn * d), (u0, y1, zc - sgn * d)]
            if sgn < 0: pts = [pts[1], pts[0], pts[3], pts[2]]
            (acc_ or acc).quad(*pts, lay, t)
            return pts
    else:
        a, b = z0, z1; xc = x1 if face == 'x1' else x0; sgn = 1 if face == 'x1' else -1
        def Q(u0, u1, y0, y1, d=0, lay=wall, t=tint, acc_=None):
            pts = [(xc - sgn * d, y0, u1), (xc - sgn * d, y0, u0), (xc - sgn * d, y1, u0), (xc - sgn * d, y1, u1)]
            if sgn < 0: pts = [pts[1], pts[0], pts[3], pts[2]]
            (acc_ or acc).quad(*pts, lay, t)
            return pts
    def side(u, y0, y1, d, inward):   # reveal quad perpendicular to facade at position u, facing +-u
        if face in ('z0', 'z1'):
            p = [(u, y0, zc), (u, y0, zc - sgn * d), (u, y1, zc - sgn * d), (u, y1, zc)]
            if (sgn > 0) == inward: p = [p[1], p[0], p[3], p[2]]
        else:
            p = [(xc, y0, u), (xc - sgn * d, y0, u), (xc - sgn * d, y1, u), (xc, y1, u)]
            if (sgn > 0) != inward: p = [p[1], p[0], p[3], p[2]]
        acc.quad(*p, wall, tint)
    def flat(u0, u1, y, d, up):        # horizontal reveal (head/sill) of depth d
        if face in ('z0', 'z1'):
            p = [(u0, y, zc), (u1, y, zc), (u1, y, zc - sgn * d), (u0, y, zc - sgn * d)]
            if (sgn > 0) != up: p = [p[1], p[0], p[3], p[2]]
        else:
            p = [(xc, y, u1), (xc, y, u0), (xc - sgn * d, y, u0), (xc - sgn * d, y, u1)]
            if (sgn > 0) != up: p = [p[1], p[0], p[3], p[2]]
        acc.quad(*p, wall, tint)
    W = b - a; m = max(1, round((W - .8) / 2.7)); s = W / m; ww = min(1.35, s * .52)
    cols = [a + s * (i + .5) for i in range(m)]
    style = lot['style']; frame = '#f4f1ea' if style != 'brick' or rnd.random() < .7 else '#2c2f33'
    floors = lot['floors']; depth = .17
    # ground floor
    if ground_shop:
        Q(a, b, 0, .55, lay='paint', t='#2a2d31')                                   # stall riser
        for i in range(m + 1):                                                       # pilasters
            u = a + s * i; Q(max(a, u - .22), min(b, u + .22), .55, 3.3, lay='stone' if style != 'render' else 'paint', t='#ddd6c6')
        for i in range(m):
            u0, u1 = a + s * i + .22, a + s * (i + 1) - .22
            if u1 - u0 < .4: continue
            pts = Q(u0, u1, .55, 3.3, d=.28, acc_=gacc, lay=0, t=WHITE)
            gacc.C[-4:] = [(1, .86, .6, 1)] * 4 if rnd.random() < .8 else [(0, 0, 0, 1)] * 4
            side(u0, .55, 3.3, .28, True); side(u1, .55, 3.3, .28, False); flat(u0, u1, 3.3, .28, False)
            Q(u0, u1, 2.6, 2.64, d=.25, lay='paint', t='#1d1f22')                   # transom bar
        Q(a, b, 3.3, 4.05, lay='paint', t=lot['shopc'], ) if True else None          # fascia
        Q(a - .05, b + .05, 4.05, 4.4, lay='stone', t='#e6e0d2')
    else:
        Q(a, b, 0, .5, lay='stone', t='#cfc7b5')
        door = cols[len(cols) // 2]
        for c in cols:
            if c == door:
                Q(max(a, c - .55 - .3), c - .55, .5, 4.4); Q(c + .55, min(b, c + .55 + .3), .5, 4.4)
                Q(c - .55, c + .55, 2.7, 4.4); Q(c - .55, c + .55, .5, 2.7, d=.2, lay='paint', t=rnd.choice(['#1d3b2a', '#232a40', '#5a1d1d', '#111']))
                side(c - .55, .5, 2.7, .2, True); side(c + .55, .5, 2.7, .2, False); flat(c - .55, c + .55, 2.7, .2, False)
            else:
                y0, y1 = 1.0, 3.2; Q(c - ww / 2, c + ww / 2, .5, y0); Q(c - ww / 2, c + ww / 2, y1, 4.4)
                pts = Q(c - ww / 2, c + ww / 2, y0, y1, d=depth, acc_=gacc, lay=0); gacc.C[-4:] = [rnd.choice(WINLIT) if rnd.random() < .3 else (0, 0, 0, 1)] * 4
                side(c - ww / 2, y0, y1, depth, True); side(c + ww / 2, y0, y1, depth, False); flat(c - ww / 2, c + ww / 2, y1, depth, False); flat(c - ww / 2, c + ww / 2, y0, depth, True)
        # piers between columns on the ground floor
        edges_u = [a]
        for c in cols: edges_u += [c - (ww / 2 if c != door else .55 + (.3 if c == door else 0)), c + (ww / 2 if c != door else .55 + .3)]
        edges_u.append(b)
        for i in range(0, len(edges_u), 2):
            if edges_u[i + 1] - edges_u[i] > .01: Q(edges_u[i], edges_u[i + 1], .5, 4.4)
    # upper floors
    y = 4.4
    for f in range(floors):
        y0w, y1w = y + .85, y + .85 + 1.95
        Q(a, b, y, y0w); Q(a, b, y1w, y + 3.4)
        last = a
        for c in cols:
            Q(last, c - ww / 2, y0w, y1w); last = c + ww / 2
            pts = Q(c - ww / 2, c + ww / 2, y0w, y1w, d=depth, acc_=gacc, lay=0); gacc.C[-4:] = [rnd.choice(WINLIT) if rnd.random() < .28 else (0, 0, 0, 1)] * 4
            side(c - ww / 2, y0w, y1w, depth, True); side(c + ww / 2, y0w, y1w, depth, False); flat(c - ww / 2, c + ww / 2, y1w, depth, False); flat(c - ww / 2, c + ww / 2, y0w, depth, True)
            Q(c - .025, c + .025, y0w, y1w, d=depth - .03, lay='paint', t=frame); Q(c - ww / 2, c + ww / 2, y0w + 1.2, y0w + 1.25, d=depth - .03, lay='paint', t=frame)
            Q(c - ww / 2 - .1, c + ww / 2 + .1, y0w - .09, y0w, d=-.07, lay='stone', t='#e4ddcc')        # sill
            if style == 'brick': Q(c - ww / 2 - .08, c + ww / 2 + .08, y1w, y1w + .22, d=-.01, lay='stone', t='#e4ddcc')
        Q(last, b, y0w, y1w)
        if style != 'brick' and f < floors - 1: Q(a - .06, b + .06, y + 3.3, y + 3.42, d=-.06, lay='stone', t='#ece6d8')
        y += 3.4
    Q(a, b, y, top)
def building(lot, rnd):
    x0, x1, z0, z1 = lot['x0'], lot['x1'], lot['z0'], lot['z1']; cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    acc, gacc = O(cx, cz), Gl(cx, cz)
    st = lot['style']
    if st in ('tower', 'podium'): return tower(lot, rnd, acc, gacc)
    wall = {'brick': 'brick', 'stone': 'stone', 'render': 'paint'}[st]
    tint = rnd.choice(BRICKS) if st == 'brick' else lot['tint']
    floors = max(1, int((lot['h'] - 4.4) / 3.4)); lot['floors'] = floors; lot['htop'] = 4.4 + floors * 3.4 + .9
    ext = lot['ext']
    for face in ('x0', 'x1', 'z0', 'z1'):
        if ext.get(face): facade(acc, gacc, lot, face, wall, tint, rnd, lot['shop'])
        else:
            if face == 'x1': acc.quad((x1, 0, z1), (x1, 0, z0), (x1, lot['htop'], z0), (x1, lot['htop'], z1), wall, tint)
            if face == 'x0': acc.quad((x0, 0, z0), (x0, 0, z1), (x0, lot['htop'], z1), (x0, lot['htop'], z0), wall, tint)
            if face == 'z1': acc.quad((x0, 0, z1), (x1, 0, z1), (x1, lot['htop'], z1), (x0, lot['htop'], z1), wall, tint)
            if face == 'z0': acc.quad((x1, 0, z0), (x0, 0, z0), (x0, lot['htop'], z0), (x1, lot['htop'], z0), wall, tint)
    h = lot['htop']; corn = '#e9e3d5'
    acc.box(x0 - .25, x1 + .25, h - .35, h, z0 - .25, z1 + .25, 'stone', corn, ao=False)                 # cornice
    r = lot['roof']
    if r == 'mansard' and min(x1 - x0, z1 - z0) > 7:
        i = 1.4; hh = 2.6
        acc.quad((x0, h, z1), (x1, h, z1), (x1 - i, h + hh, z1 - i), (x0 + i, h + hh, z1 - i), 'slate')
        acc.quad((x1, h, z0), (x0, h, z0), (x0 + i, h + hh, z0 + i), (x1 - i, h + hh, z0 + i), 'slate')
        acc.quad((x1, h, z1), (x1, h, z0), (x1 - i, h + hh, z0 + i), (x1 - i, h + hh, z1 - i), 'slate')
        acc.quad((x0, h, z0), (x0, h, z1), (x0 + i, h + hh, z1 - i), (x0 + i, h + hh, z0 + i), 'slate')
        acc.quad((x0 + i, h + hh, z1 - i), (x1 - i, h + hh, z1 - i), (x1 - i, h + hh, z0 + i), (x0 + i, h + hh, z0 + i), 'concrete', '#8a8a86')
        for k in range(max(1, int((x1 - x0) / 4))):                                   # dormers
            dx = x0 + 2 + k * (x1 - x0 - 4) / max(1, int((x1 - x0) / 4) - 1 or 1)
            for zz, sg in ((z1, 1), (z0, -1)):
                if not ext.get('z1' if sg > 0 else 'z0'): continue
                acc.cbox(dx, h + .2, zz - sg * .9, 1.2, 1.5, .9, 'paint', '#ece8de'); acc.cbox(dx, h + 1.7, zz - sg * .9, 1.4, .15, 1.1, 'slate')
    elif r == 'pitched' and min(x1 - x0, z1 - z0) > 6:
        hh = min(4, (z1 - z0) * .35)
        acc.quad((x0 - .2, h, z1 + .2), (x1 + .2, h, z1 + .2), (x1 + .2, h + hh, (z0 + z1) / 2), (x0 - .2, h + hh, (z0 + z1) / 2), 'slate')
        acc.quad((x1 + .2, h, z0 - .2), (x0 - .2, h, z0 - .2), (x0 - .2, h + hh, (z0 + z1) / 2), (x1 + .2, h + hh, (z0 + z1) / 2), 'slate')
        for xx, sg in ((x0, -1), (x1, 1)):
            pts = [(xx, h, z0), (xx, h, z1), (xx, h + hh, (z0 + z1) / 2)] if sg > 0 else [(xx, h, z1), (xx, h, z0), (xx, h + hh, (z0 + z1) / 2)]
            acc.face(pts, wall, tint)
    else:
        acc.quad((x0, h - .05, z1), (x1, h - .05, z1), (x1, h - .05, z0), (x0, h - .05, z0), 'concrete', '#9c9a94')
        acc.box(x0, x1, h, h + .7, z0, z0 + .25, wall, tint); acc.box(x0, x1, h, h + .7, z1 - .25, z1, wall, tint)
        if rnd.random() < .6: acc.cbox(x0 + 2 + rnd.random() * max(.1, x1 - x0 - 4), h, z0 + 2.5, 2.2, 1.4, 2.2, 'metal', '#8b8f94')
        if rnd.random() < .3: acc.cyl(x1 - 2.5, z1 - 2.5, 1.1, 1.1, h, h + 2.6, 10, 'metal', '#6e7378')
    if lot['chimneys']:
        for cxk in (x0 + 1.6, x1 - 1.6) if x1 - x0 > 9 else (x0 + 1.6,):
            ch_h = h + (2.6 if r != 'pitched' else 4.2)
            acc.box(cxk - .55, cxk + .55, h - .3, ch_h, cz - 1.3, cz + 1.3, 'brick', rnd.choice(BRICKS))
            acc.box(cxk - .65, cxk + .65, ch_h - .2, ch_h, cz - 1.4, cz + 1.4, 'stone', '#ddd5c3')
            for k in (-.7, 0, .7): acc.cyl(cxk, cz + k, .13, .11, ch_h, ch_h + .5, 6, 'paint', '#b0603a')
    if lot['shop'] and lot['awning']:
        for face in ('z0', 'z1'):
            if not ext.get(face): continue
            zz = z1 if face == 'z1' else z0; sg = 1 if face == 'z1' else -1
            c = rnd.choice(['#1d5d3a', '#7b1e2b', '#1f3a5f', '#e4ddcc', '#2a2a2a', '#8a5a00'])
            p = [(x0 + .3, 3.2, zz), (x1 - .3, 3.2, zz), (x1 - .3, 2.55, zz + sg * 1.6), (x0 + .3, 2.55, zz + sg * 1.6)]
            if sg < 0: p = [p[1], p[0], p[3], p[2]]
            acc.quad(*p, 'paint', c, ao=False)
    return
def tower(lot, rnd, acc, gacc):
    x0, x1, z0, z1, h = lot['x0'], lot['x1'], lot['z0'], lot['z1'], lot['h']
    if lot['style'] == 'podium':
        acc.box(x0, x1, 3.8, h, z0, z1, 'stone', '#cfc9bc'); acc.box(x0 - .3, x1 + .3, h, h + .4, z0 - .3, z1 + .3, 'concrete', '#d8dadc')
        for f in ('x0', 'x1', 'z0', 'z1'):
            pts = {'z1': [(x0, 0, z1 - .3), (x1, 0, z1 - .3), (x1, 3.8, z1 - .3), (x0, 3.8, z1 - .3)], 'z0': [(x1, 0, z0 + .3), (x0, 0, z0 + .3), (x0, 3.8, z0 + .3), (x1, 3.8, z0 + .3)],
                   'x1': [(x1 - .3, 0, z1), (x1 - .3, 0, z0), (x1 - .3, 3.8, z0), (x1 - .3, 3.8, z1)], 'x0': [(x0 + .3, 0, z0), (x0 + .3, 0, z1), (x0 + .3, 3.8, z1), (x0 + .3, 3.8, z0)]}[f]
            glass_face(gacc, pts, rnd, .9)
        return
    tint = lot['tint']; tier = lot.get('tier')
    def block(a0, a1, y0, y1, b0, b1):
        for pts in ([(a0, y0, b1), (a1, y0, b1), (a1, y1, b1), (a0, y1, b1)], [(a1, y0, b0), (a0, y0, b0), (a0, y1, b0), (a1, y1, b0)],
                    [(a1, y0, b1), (a1, y0, b0), (a1, y1, b0), (a1, y1, b1)], [(a0, y0, b0), (a0, y0, b1), (a0, y1, b1), (a0, y1, b0)]):
            gacc.face(pts, 0, WHITE, ao=False)
            lit = (1, .93, .8, 1) if rnd.random() < .5 else (.75, .85, 1, 1)
            for i in range(4): gacc.C[-1 - i] = lit
        acc.quad((a0, y1, b1), (a1, y1, b1), (a1, y1, b0), (a0, y1, b0), 'concrete', '#9da2a6')
        for k in range(int(y0 / 3.8) + 1, int(y1 / 3.8)):
            yy = k * 3.8; acc.box(a0 - .12, a1 + .12, yy, yy + .35, b0 - .12, b1 + .12, 'steel', tint, top=False)
        n = max(2, int((a1 - a0) / 3))
        for k in range(n + 1):
            u = a0 + (a1 - a0) * k / n
            acc.box(u - .12, u + .12, y0, y1, b1, b1 + .3, 'steel', '#c4ccd2', top=False); acc.box(u - .12, u + .12, y0, y1, b0 - .3, b0, 'steel', '#c4ccd2', top=False)
    if tier:
        block(x0, x1, 7, tier, z0, z1); block(x0 + 3, x1 - 3, tier, h, z0 + 3, z1 - 3)
        acc.box(x0 - .2, x1 + .2, tier, tier + .5, z0 - .2, z1 + .2, 'concrete', '#e1e4e6')
    else: block(x0, x1, 7, h, z0, z1)
    i = 3 if tier else 0
    acc.box(x0 + i + (x1 - x0 - 2 * i) * .22, x1 - i - (x1 - x0 - 2 * i) * .22, h, h + 3.2, z0 + i + (z1 - z0 - 2 * i) * .22, z1 - i - (z1 - z0 - 2 * i) * .22, 'metal', '#5f6a73')
    if lot.get('crown'): acc.cyl((x0 + x1) / 2, (z0 + z1) / 2, .25, .1, h + 3.2, h + 14, 6, 'steel')
for k, lot in enumerate(L['lots']): building(lot, random.Random(lot.get('seed', k)))
print('buildings done', flush=True)
# ---------------------------------------------------------------- ground, roads, kerbs
nodes, edges = L['nodes'], L['edges']
KERB = .12
def pave(x0, x1, z0, z1, layer='pavement', tint=WHITE, h=KERB):
    for xa in range(int(math.floor((x0 + HALF + 200) / CH)), int(math.floor((x1 - 1e-6 + HALF + 200) / CH)) + 1):
        for za in range(int(math.floor((z0 + HALF + 200) / CH)), int(math.floor((z1 - 1e-6 + HALF + 200) / CH)) + 1):
            ax0 = max(x0, xa * CH - HALF - 200); ax1 = min(x1, (xa + 1) * CH - HALF - 200); az0 = max(z0, za * CH - HALF - 200); az1 = min(z1, (za + 1) * CH - HALF - 200)
            acc = O((ax0 + ax1) / 2, (az0 + az1) / 2)
            acc.quad((ax0, h, az1), (ax1, h, az1), (ax1, h, az0), (ax0, h, az0), layer, tint, ao=False)
    acc = O((x0 + x1) / 2, (z0 + z1) / 2)
    acc.box(x0, x1, 0, h, z0, z1, 'kerb', '#c9c6bf', top=False)
RG = L['ring']; RING, RIN, ROUT, PROM = RG['r'], RG['rin'], RG['rout'], RG['prom']
def clip_poly(poly, x0, x1, z0, z1):
    for ax, v, sg in ((0, x0, 1), (0, x1, -1), (1, z0, 1), (1, z1, -1)):
        out = []
        for i in range(len(poly)):
            P, Q = poly[i], poly[(i + 1) % len(poly)]; ip, iq = (P[ax] - v) * sg >= 0, (Q[ax] - v) * sg >= 0
            if iq:
                if not ip: t = (v - P[ax]) / (Q[ax] - P[ax]); out.append((P[0] + (Q[0] - P[0]) * t, P[1] + (Q[1] - P[1]) * t))
                out.append(Q)
            elif ip: t = (v - P[ax]) / (Q[ax] - P[ax]); out.append((P[0] + (Q[0] - P[0]) * t, P[1] + (Q[1] - P[1]) * t))
        poly = out
        if not poly: break
    return poly
def fan(acc, poly, y, layer, tint=WHITE):
    cx = sum(p[0] for p in poly) / len(poly); cz = sum(p[1] for p in poly) / len(poly)
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        acc.face([(cx, y, cz), (b[0], y, b[1]), (a[0], y, a[1])], layer, tint, ao=False)
def chunks_of(poly):
    xs = [p[0] for p in poly]; zs = [p[1] for p in poly]
    for xa in range(int(math.floor((min(xs) + HALF + 200) / CH)), int(math.floor((max(xs) - 1e-6 + HALF + 200) / CH)) + 1):
        for za in range(int(math.floor((min(zs) + HALF + 200) / CH)), int(math.floor((max(zs) - 1e-6 + HALF + 200) / CH)) + 1):
            x0, z0 = xa * CH - HALF - 200, za * CH - HALF - 200
            part = clip_poly(poly, x0, x0 + CH, z0, z0 + CH)
            if len(part) >= 3: yield part
def pave_poly(poly, layer='pavement', h=KERB):
    for part in chunks_of(poly):
        cx = sum(p[0] for p in part) / len(part); cz = sum(p[1] for p in part) / len(part); fan(O(cx, cz), part, h, layer)
    for i in range(len(poly)):   # kerb faces
        a, b = poly[i], poly[(i + 1) % len(poly)]
        O((a[0] + b[0]) / 2, (a[1] + b[1]) / 2).quad((b[0], 0, b[1]), (a[0], 0, a[1]), (a[0], h, a[1]), (b[0], h, b[1]), 'kerb', '#c9c6bf', ao=False)
for b in L['blocks']:
    if b.get('poly'): pave_poly([tuple(p) for p in b['poly']])
    elif not b.get('sub'): pave(b['x0'], b['x1'], b['z0'], b['z1'])
for zn in L['zones']: pave(zn['x0'], zn['x1'], zn['z0'] if zn['z0'] > 0 else zn['z0'], zn['z1'] if zn['z1'] < 0 else zn['z1'])
for s in (-1, 1):
    brs = sorted(L['bridges'], key=lambda br: br['x'])
    for a, b in zip(brs[:-1], brs[1:]):
        x0, g0 = a['x'] + a['hw'], b['x'] - b['hw']
        if g0 > x0: pave(x0, g0, RIVER if s > 0 else -RIVER - 8, RIVER + 8 if s > 0 else -RIVER)
for g in L['greens']:
    x0, z0, x1, z1 = g; acc = O((x0 + x1) / 2, (z0 + z1) / 2)
    acc.box(x0, x1, KERB, KERB + .1, z0, z1, 'grass', toplayer='grass', ao=False)
for g in L['gravel']:
    x0, z0, x1, z1 = g; O((x0 + x1) / 2, (z0 + z1) / 2).box(x0, x1, KERB, KERB + .12, z0, z1, 'gravel', ao=False)
# asphalt base: the island disc, minus the river
ISLAND = [(PROM * math.cos(a), PROM * math.sin(a)) for a in [i / 240 * 2 * math.pi for i in range(240)]]
for half_ in (clip_poly(ISLAND, -9999, 9999, -9999, -RIVER), clip_poly(ISLAND, -9999, 9999, RIVER, 9999)):
    for part in chunks_of(half_):
        cx = sum(p[0] for p in part) / len(part); cz = sum(p[1] for p in part) / len(part); fan(O(cx, cz), part, -.02, 'asphalt')
# seafront: promenade between the ring road and the sea wall, wall face down to the water, parapet on top
NS = 240
for k in range(NS):
    a0, a1 = k / NS * 2 * math.pi, (k + 1) / NS * 2 * math.pi
    p = lambda r, a: (r * math.cos(a), r * math.sin(a))
    if min(abs(PROM * math.sin(a0)), abs(PROM * math.sin(a1))) < RIVER + .5: continue
    (x0, z0), (x1, z1) = p(ROUT, a0), p(ROUT, a1); (X0, Z0), (X1, Z1) = p(PROM, a0), p(PROM, a1); (Y0, W0), (Y1, W1) = p(PROM - .6, a0), p(PROM - .6, a1)
    acc = O((x0 + X1) / 2, (z0 + Z1) / 2)
    acc.quad((x0, KERB, z0), (x1, KERB, z1), (X1, KERB, Z1), (X0, KERB, Z0), 'pavement', ao=False)
    acc.quad((x1, 0, z1), (x0, 0, z0), (x0, KERB, z0), (x1, KERB, z1), 'kerb', '#c9c6bf', ao=False)
    acc.quad((X1, -4, Z1), (X0, -4, Z0), (X0, KERB, Z0), (X1, KERB, Z1), 'stone', '#b5ab95')
    acc.quad((Y0, 1.05, W0), (Y1, 1.05, W1), (X1, 1.05, Z1), (X0, 1.05, Z0), 'stone', '#ddd5c2', ao=False)
    acc.quad((X1, KERB, Z1), (X0, KERB, Z0), (X0, 1.05, Z0), (X1, 1.05, Z1), 'stone', '#cfc6b0')
    acc.quad((Y0, KERB, W0), (Y1, KERB, W1), (Y1, 1.05, W1), (Y0, 1.05, W0), 'stone', '#cfc6b0')
def strip(p0, p1, hw, layer, tint=WHITE, y=0.0, v0=0.0):
    (ax, az), (bx, bz) = p0, p1; dx, dz = bx - ax, bz - az; Ln = math.hypot(dx, dz)
    if Ln < .01: return v0
    nx, nz = -dz / Ln, dx / Ln; sc = UVS[layer]
    pts = [(ax + nx * hw, y, az + nz * hw), (ax - nx * hw, y, az - nz * hw), (bx - nx * hw, y, bz - nz * hw), (bx + nx * hw, y, bz + nz * hw)]
    if nx * 1 + 0 < -1: pass
    uvs = [(0, v0), (1, v0), (1, v0 + Ln / sc), (0, v0 + Ln / sc)]
    a = Vector(pts[1]) - Vector(pts[0]); c = Vector(pts[3]) - Vector(pts[0])
    if a.cross(c).y < 0: pts = [pts[1], pts[0], pts[3], pts[2]]; uvs = [uvs[1], uvs[0], uvs[3], uvs[2]]
    O((ax + bx) / 2, (az + bz) / 2).quad(*pts, layer, tint, uvs=uvs, ao=False)
    return v0 + Ln / sc
for e in edges:
    a, b = nodes[e['a']], nodes[e['b']]; hw = e['hw']; lay = 'roadring' if e['ring'] else ('redasphalt' if e['mall'] else 'road')
    dx, dz = b['x'] - a['x'], b['z'] - a['z']; Ln = math.hypot(dx, dz); ux, uz = dx / Ln, dz / Ln
    ia = hw if a['deg'] > 2 else 0; ib = hw if b['deg'] > 2 else 0
    pa = (a['x'] + ux * ia, a['z'] + uz * ia); pb = (b['x'] - ux * ib, b['z'] - uz * ib)
    strip(pa, pb, hw, lay, '#ffffff' if lay != 'redasphalt' else '#ffffff')
    if e.get('curve'):  # fill the outer wedge gaps of the curved segment with plain asphalt
        strip((a['x'], a['z']), (b['x'], b['z']), hw + .6, 'asphalt', y=-.01)
    if not e['ring'] and not e.get('bridge') and not e.get('curve'):
        for t, ok in ((ia + 2.4, ia > 0), (Ln - ib - 2.4, ib > 0)):
            if not ok: continue
            cx, cz = a['x'] + ux * t, a['z'] + uz * t
            strip((cx - ux * 1.3, cz - uz * 1.3), (cx + ux * 1.3, cz + uz * 1.3), hw - .6, 'zebra', y=.012)
for i, n in enumerate(nodes):
    if n['deg'] > 2 and n.get('r'):   # ring junctions: a round patch of asphalt
        fan(O(n['x'], n['z']), [(n['x'] + (RG['hw'] + .8) * math.cos(a), n['z'] + (RG['hw'] + .8) * math.sin(a)) for a in [k / 16 * 2 * math.pi for k in range(16)]], .004, 'asphalt')
    elif n['deg'] > 2:
        hw = RW
        O(n['x'], n['z']).quad((n['x'] - hw, 0, n['z'] + hw), (n['x'] + hw, 0, n['z'] + hw), (n['x'] + hw, 0, n['z'] - hw), (n['x'] - hw, 0, n['z'] - hw), 'asphalt', ao=False)
print('streets done', flush=True)
# ---------------------------------------------------------------- river walls & bridges
XW = math.sqrt(PROM ** 2 - RIVER ** 2)
for s in (-1, 1):
    for x in range(-int(XW), int(XW), 40):
        acc = O(x + 20, s * RIVER)
        z = s * RIVER; acc.quad(*([(x, -4, z), (x + 40, -4, z), (x + 40, KERB, z), (x, KERB, z)] if s < 0 else [(x + 40, -4, z), (x, -4, z), (x, KERB, z), (x + 40, KERB, z)]), 'stone', '#b5ab95')
    x0 = -XW
    for br in L['bridges'] + [dict(x=XW + .4, hw=0)]:
        g0 = br['x'] - br['hw'] - .4
        if g0 > x0:
            for xx in range(int(x0), int(g0), 20):
                xe = min(g0, xx + 20); acc = O((xx + xe) / 2, s * RIVER)
                acc.box(xx, xe, KERB, 1.05, s * RIVER - (.55 if s < 0 else 0) - (0 if s < 0 else -.0), s * RIVER + (0 if s < 0 else .55), 'stone', '#cfc6b0')
                acc.box(xx, xe, 1.05, 1.18, s * RIVER - (.65 if s < 0 else .1), s * RIVER + (.1 if s < 0 else .65), 'stone', '#ddd5c2', ao=False)
        x0 = br['x'] + br['hw'] + .4
COLS = {'westminster': ('#3d6b4f', 'metal'), 'tower': ('#4f8bc9', 'metal'), 'stone': ('#b9b4a8', 'stone'), 'modern': ('#9aa3aa', 'steel')}
for br in L['bridges']:
    bx, hw = br['x'], br['hw']; col, lay = COLS[br['style']]
    for zz in range(-RIVER, RIVER, 15):
        acc = O(bx, zz + 7.5)
        acc.box(bx - hw, bx + hw, -1.4, -.01, zz, zz + 15, 'concrete', '#a8a59e', top=False, bottom=True)
        for sg in (-1, 1):
            acc.box(bx + sg * hw - .3, bx + sg * hw + .3, 0, 1.15, zz, zz + 15, lay, col)
            if br['style'] == 'westminster':
                for k in range(5): acc.cbox(bx + sg * hw, .1, zz + 1.5 + k * 3, .5, 1.1, .3, 'metal', col)
    for zz in (-14, 0, 14) if br['style'] != 'tower' else ():
        acc = O(bx, zz); acc.box(bx - hw + 1, bx + hw - 1, -4, -1.4, zz - 2.2, zz + 2.2, 'stone', '#958a77')
        if br['style'] in ('stone', 'westminster'):
            for sg in (-1, 1): acc.cyl(bx + sg * (hw - .2), zz, 2.4, 2.4, -1.6, .0, 12, 'stone', '#958a77')
print('bridges done', flush=True)
# ---------------------------------------------------------------- billboards
for bb in L['billboards']:
    x, y, z, ry, ad = bb['x'], bb['y'], bb['z'], bb['ry'], bb['ad']
    acc = O(x, z); s = 1 if ry == 0 else -1
    u0, v0 = (ad % 2) * .5, 1 - (ad // 2 + 1) * (170 / 512); u1, v1 = u0 + .5, v0 + 170 / 512
    pts = [(x - 7.5, y + .4, z + s * .05), (x + 7.5, y + .4, z + s * .05), (x + 7.5, y + 5.3, z + s * .05), (x - 7.5, y + 5.3, z + s * .05)]
    uvs = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
    if s < 0: pts = [pts[1], pts[0], pts[3], pts[2]]
    acc.quad(*pts, 'ads', uvs=uvs, ao=False)
    acc.box(x - 7.7, x + 7.7, y + .2, y + 5.5, z - s * .25, z, 'metal', '#2b2f33')
    for k in (-5, 0, 5): acc.box(x + k - .15, x + k + .15, y - 1, y + .3, z - s * .5, z - s * .2, 'metal', '#2b2f33')
# ---------------------------------------------------------------- landmarks
exec(open(os.path.join(HERE, 'landmarks.py')).read())
print('landmarks done', flush=True)
# ---------------------------------------------------------------- output
col = bpy.context.scene.collection
n_tris = 0
for (i, j), (acc, gacc) in sorted(CHUNKS.items()):
    o = acc.to_object('C_%d_%d' % (i, j)); g = gacc.to_object('G_%d_%d' % (i, j), glass=True)
    n_tris += sum(len(f) - 2 for f in acc.F) + sum(len(f) - 2 for f in gacc.F)
print('chunks', len(CHUNKS), 'triangles', n_tris, flush=True)
export(os.path.join(ROOT, 'assets', 'city', 'city.glb'))
print('exported city.glb', flush=True)
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
EYE.to_object('EyeWheel'); export(os.path.join(ROOT, 'assets', 'city', 'eye.glb')); print('exported eye.glb')
