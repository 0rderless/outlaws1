"""City layout generator: writes assets/city/layout.json, shared by the Blender builder and the game.
Coordinates: metres, x east, z south (river runs along x), y up."""
import json, math, random, os
R = random.Random(20261121)
# The city is a round island: a grid of streets inside a circular ring road on the waterfront, sea all around.
RIVER = 30; RW = 7; RWR = 9
RING, RHW = 460.0, 9.0                      # ring road centre radius and half width
RIN, ROUT, PROM = RING - RHW, RING + RHW, RING + RHW + 7   # inner kerb, outer kerb, sea wall
HALF = 480                                  # map extent for the game (minimap, chunks)
XL = [-320, -240, -160, -80, 0, 80, 160, 240, 320]
ZL = [-285, -205, -125, -45, 45, 125, 205, 285]
ZCON = [-285, -205, -125, 125, 205, 285]    # east-west streets that run out to the ring road
RB = round(math.sqrt(RING ** 2 - 36 ** 2), 2)    # x of the ring road's two river bridges
BRIDGES = [-RB, -160, 0, 160, RB]
def hw_x(x): return RW
def hw_z(z): return RW
ZONES = [dict(id='palace', x0=-313, x1=-167, z0=-198, z1=-52), dict(id='parl', x0=-153, x1=-87, z0=-118, z1=-31), dict(id='eye', x0=-153, x1=-87, z0=31, z1=118)]
REMOVED = {((-160, -45), (-80, -45)), ((-160, 45), (-80, 45)), ((-240, -205), (-240, -125)), ((-240, -125), (-240, -45)), ((-240, -125), (-160, -125)), ((-320, -125), (-240, -125))}
MALL = {((-160, -125), (-80, -125)), ((-80, -125), (0, -125))}
# ---------------- road graph ----------------
nodes, edges, nidx = [], [], {}
def node(x, z, kind='j'):
    k = (round(x, 2), round(z, 2))
    if k not in nidx: nidx[k] = len(nodes); nodes.append(dict(x=round(x, 2), z=round(z, 2), k=kind))
    return nidx[k]
def link(a, b, **f):
    ka, kb = (nodes[a]['x'], nodes[a]['z']), (nodes[b]['x'], nodes[b]['z'])
    if (ka, kb) in REMOVED or (kb, ka) in REMOVED: return
    f.setdefault('ring', False); f.setdefault('hw', RW)
    edges.append(dict(a=a, b=b, mall=(ka, kb) in MALL or (kb, ka) in MALL, **f))
for z in ZL:
    for i in range(len(XL) - 1): link(node(XL[i], z), node(XL[i + 1], z))
for x in XL:
    for j in range(len(ZL) - 1):
        if ZL[j] == -45 and x not in BRIDGES: continue
        link(node(x, ZL[j]), node(x, ZL[j + 1]), bridge=(ZL[j] == -45))
ring_pts = {}                                    # angle -> (x, z, is_junction)
def on_ring(x, z, junction): ring_pts[round(math.atan2(z, x), 6)] = (x, z, junction)
for x in XL:                                     # every north-south street runs out to the ring
    zc = math.sqrt(RING ** 2 - x ** 2)
    for s, z0 in ((-1, ZL[0]), (1, ZL[-1])):
        on_ring(x, s * zc, True); link(node(x, z0), node(x, round(s * zc, 2), 'j'))
for z in ZCON:                                   # and these east-west streets
    xc = math.sqrt(RING ** 2 - z ** 2)
    for s, x0 in ((-1, XL[0]), (1, XL[-1])):
        on_ring(s * xc, z, True); link(node(x0, z), node(round(s * xc, 2), z, 'j'))
for s in (-1, 1):
    for z in (-36, 36): on_ring(s * RB, z, False)
angs = sorted(ring_pts)
ring_nodes = []
for i, a in enumerate(angs):
    b = angs[(i + 1) % len(angs)] + (2 * math.pi if i == len(angs) - 1 else 0)
    x, z, jn = ring_pts[a]; ring_nodes.append(node(x, z, 'j' if jn else 'c'))
    nx_, nz_ = ring_pts[angs[(i + 1) % len(angs)]][:2]
    straight = abs(nx_ - x) < .01 and abs(z) == 36 and abs(nz_) == 36          # river crossing: one straight bridge span
    n_mid = 0 if straight else max(0, math.ceil((b - a) * RING / 24) - 1)
    for k in range(1, n_mid + 1):
        t = a + (b - a) * k / (n_mid + 1); ring_nodes.append(node(RING * math.cos(t), RING * math.sin(t), 'c'))
for i in range(len(ring_nodes)):
    a, b = ring_nodes[i], ring_nodes[(i + 1) % len(ring_nodes)]
    na, nb = nodes[a], nodes[b]
    br = abs(na['x'] - nb['x']) < .01 and abs(na['z']) == 36 and abs(nb['z']) == 36
    link(a, b, ring=True, hw=RHW, curve=not br, bridge=br)
for i in ring_nodes: nodes[i]['r'] = 1
deg = [0] * len(nodes)
for e in edges: deg[e['a']] += 1; deg[e['b']] += 1
for i, n in enumerate(nodes): n['deg'] = deg[i]
# ---------------- blocks ----------------
def clip(poly, inside, inter):
    out = []
    for i in range(len(poly)):
        P, Q = poly[i], poly[(i + 1) % len(poly)]
        if inside(Q):
            if not inside(P): out.append(inter(P, Q))
            out.append(Q)
        elif inside(P): out.append(inter(P, Q))
    return out
def clip_rect(poly, x0, x1, z0, z1):
    for ax, v, sg in ((0, x0, 1), (0, x1, -1), (1, z0, 1), (1, z1, -1)):
        poly = clip(poly, lambda p: (p[ax] - v) * sg >= 0, lambda P, Q: tuple(P[k] + (Q[k] - P[k]) * ((v - P[ax]) / (Q[ax] - P[ax])) for k in (0, 1)))
        if not poly: break
    return poly
DISC = [(RIN * math.cos(a), RIN * math.sin(a)) for a in [i / 360 * 2 * math.pi for i in range(360)]]
def area(poly): return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))) / 2
def bounds(lines):
    return [(lines[i] + RW, lines[i + 1] - RW) for i in range(len(lines) - 1)]
XB = bounds(XL); ZB = [b for b in bounds(ZL) if not (b[0] < 0 < b[1])]
def in_zone(x0, x1, z0, z1): return next((zn for zn in ZONES if x0 >= zn['x0'] - 1 and x1 <= zn['x1'] + 1 and z0 >= zn['z0'] - 1 and z1 <= zn['z1'] + 1), None)
SPECIAL = {(200, -85): 'tol', (120, 85): 'shard', (120, -165): 'gherkin', (200, -165): 'cheese', (40, -245): 'walkie', (-120, -165): 'park', (-280, 245): 'park'}
blocks = []
for x0, x1 in XB:
    for z0, z1 in ZB:
        if in_zone(x0, x1, z0, z1): continue
        cx, cz = round((x0 + x1) / 2), round((z0 + z1) / 2)
        blocks.append(dict(x0=x0, x1=x1, z0=z0, z1=z1, cx=cx, cz=cz, kind=SPECIAL.get((cx, cz), 'gen')))
# outer districts between the grid and the ring road: curved polygons (pavement) with a rectangle of buildings inside
INF = 900; E = XL[-1] + RW; EZ = ZL[-1] + RW
xs = [(-INF, -E)] + [(XL[i] + RW, XL[i + 1] - RW) for i in range(len(XL) - 1)] + [(E, INF)]
zs = [(ZCON[i] + RW, ZCON[i + 1] - RW) for i in range(len(ZCON) - 1) if not (ZCON[i] < 0 < ZCON[i + 1])] + [(-125 + RW, -RIVER - 8), (RIVER + 8, 125 - RW)]
regions = [(a, b, -INF, -EZ, 'n') for a, b in xs] + [(a, b, EZ, INF, 's') for a, b in xs] + [(-INF, -E, a, b, 'w') for a, b in zs] + [(E, INF, a, b, 'e') for a, b in zs]
def inscribed(x0, x1, z0, z1, side):
    lim = lambda v: math.sqrt(max(0, RIN ** 2 - v ** 2)) - 6
    if (x0 == -INF or x1 == INF) and (z0 == -INF or z1 == INF):   # corner: square grown from the grid corner
        sx = 1 if x1 == INF else -1; sz = 1 if z1 == INF else -1; ax, az = (x0 if sx > 0 else x1), (z0 if sz > 0 else z1)
        a, b = abs(ax), abs(az); r = RIN - 6; d = (-(a + b) + math.sqrt((a + b) ** 2 - 2 * (a * a + b * b - r * r))) / 2
        return (ax, ax + sx * d)[::sx], (az, az + sz * d)[::sz]
    if side == 'n': return x0, x1, -min(lim(x0), lim(x1)), z1
    if side == 's': return x0, x1, z0, min(lim(x0), lim(x1))
    if side == 'w': return -min(lim(z0), lim(z1)), x1, z0, z1
    return x0, min(lim(z0), lim(z1)), z0, z1
OUTER_KIND = {(-1, -245): 'park', (-1, 245): 'park', (1, 78): 'towers'}
for x0, x1, z0, z1, side in regions:
    poly = clip_rect(DISC, x0, x1, z0, z1)
    if not poly or area(poly) < 40: continue
    corner = (x0 == -INF or x1 == INF) and (z0 == -INF or z1 == INF)
    ins = inscribed(x0, x1, z0, z1, side)
    if len(ins) == 2: (rx0, rx1), (rz0, rz1) = ins
    else: rx0, rx1, rz0, rz1 = ins
    rx0, rx1, rz0, rz1 = max(rx0, min(p[0] for p in poly)), min(rx1, max(p[0] for p in poly)), max(rz0, min(p[1] for p in poly)), min(rz1, max(p[1] for p in poly))
    cx, cz = round((rx0 + rx1) / 2), round((rz0 + rz1) / 2)
    kind = 'park' if corner or rx1 - rx0 < 24 or rz1 - rz0 < 24 else OUTER_KIND.get((1 if cx > 0 else -1, round((z0 + z1) / 2) if side in 'ew' else None), 'gen')
    if side in 'ew' and (1 if cx > 0 else -1, round((z0 + z1) / 2)) in OUTER_KIND: kind = OUTER_KIND[(1 if cx > 0 else -1, round((z0 + z1) / 2))]
    blocks.append(dict(x0=round(min(p[0] for p in poly), 2), x1=round(max(p[0] for p in poly), 2), z0=round(min(p[1] for p in poly), 2), z1=round(max(p[1] for p in poly), 2),
                       cx=cx, cz=cz, kind='district', outer=1, side=side, poly=[[round(p[0], 2), round(p[1], 2)] for p in poly]))
    if rx1 - rx0 < 10 or rz1 - rz0 < 10: continue
    # split deep districts into street-sized blocks with walkways between them
    along_z = side in 'ns'; lo, hi = (rz0, rz1) if along_z else (rx0, rx1); n = max(1, math.ceil((hi - lo) / 70)); gap = 10
    seg = (hi - lo - gap * (n - 1)) / n
    for k in range(n):
        a0 = lo + k * (seg + gap); a1 = a0 + seg
        bx0, bx1, bz0, bz1 = (rx0, rx1, a0, a1) if along_z else (a0, a1, rz0, rz1)
        bcx, bcz = round((bx0 + bx1) / 2), round((bz0 + bz1) / 2)
        blocks.append(dict(x0=round(bx0, 2), x1=round(bx1, 2), z0=round(bz0, 2), z1=round(bz1, 2), cx=bcx, cz=bcz, kind=kind, sub=1))
# ---------------- buildings ----------------
lots, props, colliders, billboards = [], [], [], []
def col(x0, x1, z0, z1, h): colliders.append([round(x0, 2), round(x1, 2), round(z0, 2), round(z1, 2), round(h, 2)])
def prop(t, x, z, ry=0, s=1): props.append([t, round(x, 2), round(z, 2), round(ry, 3), round(s, 2)])
STONE = ['#e3dccb', '#efe6d2', '#d7cfbd', '#c8bfa9']; RENDER = ['#f2efe8', '#ece4d6', '#e8dfcf', '#f6f1e6', '#dfe6e8']
GLASSC = ['#8fb3cf', '#7fa2b8', '#9cc1c9', '#6f8fa8', '#a9bcc9', '#86a7a0']; SHOPC = ['#7b1e2b', '#1f3a5f', '#0f5132', '#3b2b54', '#111418', '#8a5a00', '#5a1d1d', '#24453f', '#a03c14', '#0d4d57']
def glassy(b): return (b['cx'] > 0 and b['cz'] < -120) or (b['cx'] > 80 and b['cz'] > 120) or b['cx'] > 240 or b['kind'] == 'towers'
def gen_block(b, outer=False):
    sx0, sx1, sz0, sz1 = b['x0'] + 5, b['x1'] - 5, b['z0'] + 5, b['z1'] - 5
    if outer:
        sx0, sx1, sz0, sz1 = max(sx0, -HALF + 4), min(sx1, HALF - 4), max(sz0, -HALF + 4), min(sz1, HALF - 4)
    w, d = sx1 - sx0, sz1 - sz0
    if w < 8 or d < 8: return
    north, riverfront = b['cz'] < 0, abs(b['cz']) < 100
    if glassy(b) and not outer:
        n = 2 if w > 50 and R.random() < .6 else 1
        lots.append(dict(style='podium', x0=sx0, x1=sx1, z0=sz0, z1=sz1, h=7, tint='#9aa7b0')); col(sx0, sx1, sz0, sz1, 7)
        for i in range(n):
            tw = w / n - 6; tx0 = sx0 + 3 + i * (w / n); td = d - R.uniform(6, 18); tz0 = sz0 + (d - td) / 2
            h = R.uniform(60, 135) if b['cz'] < -120 or b['cx'] > 240 else R.uniform(34, 72)
            tier = h * R.uniform(.55, .7) if R.random() < .45 else None
            lots.append(dict(style='tower', x0=tx0, x1=tx0 + tw, z0=tz0, z1=tz0 + td, h=h, tier=tier, tint=R.choice(GLASSC), crown=R.random() < .5))
            col(tx0, tx0 + tw, tz0, tz0 + td, h)
        return
    nx = max(2, round(w / R.uniform(13, 20))); lw = w / nx; front = 1 if north else 0
    shops = R.random() < .7 and not outer
    for j in range(2):
        for i in range(nx):
            x0 = sx0 + i * lw; x1 = x0 + lw; z0 = sz0 + j * d / 2; z1 = z0 + d / 2
            r = R.random(); style = 'brick' if r < .42 else 'stone' if r < .75 else 'render'
            h = R.uniform(11, 27) if not outer else R.uniform(14, 38)
            tint = {'brick': R.choice(['#ffffff', '#f3e6dc', '#e9d8cc', '#fff3ea', '#d9c6b8']), 'stone': R.choice(STONE), 'render': R.choice(RENDER)}[style]
            ext = dict(z0=j == 0, z1=j == 1, x0=i == 0, x1=i == nx - 1)
            lot = dict(style=style, x0=x0, x1=x1, z0=z0, z1=z1, h=h, tint=tint, ext=ext, shop=shops, shopc=R.choice(SHOPC),
                       awning=R.random() < .45, roof=R.choice(['flat', 'flat', 'mansard', 'pitched']), chimneys=style == 'brick' or R.random() < .3, seed=R.randrange(1 << 30))
            lots.append(lot); col(x0, x1, z0, z1, h)
            if riverfront and j == front and i == nx // 2 and len(billboards) < 8 and not outer:
                billboards.append(dict(x=(x0 + x1) / 2, y=h + .8, z=z1 - 3 if north else z0 + 3, ry=0 if north else math.pi, ad=len(billboards) % 6))
    if not outer:
        if R.random() < .45: prop('phonebox', b['x0'] + 3.6, b['z0'] + 3.6); col(b['x0'] + 3, b['x0'] + 4.2, b['z0'] + 3, b['z0'] + 4.2, 2.7)
        if R.random() < .35: prop('postbox', b['x1'] - 3.4, b['z1'] - 3.4); col(b['x1'] - 3.7, b['x1'] - 3.1, b['z1'] - 3.7, b['z1'] - 3.1, 1.5)
        if R.random() < .3: prop('bench', (b['x0'] + b['x1']) / 2, b['z0'] + 2.2, 0)
def tree(x, z, s=1.0, kind=None):
    prop(kind or R.choice(['tree1', 'tree2', 'tree1']), x, z, R.uniform(0, 6.28), s); col(x - .35, x + .35, z - .35, z + .35, 3)
def park(b, step=9):
    for x in range(int(b['x0']) + 5, int(b['x1']) - 4, step):
        for z in range(int(b['z0']) + 5, int(b['z1']) - 4, step):
            if R.random() < .62: tree(x + R.uniform(-2, 2), z + R.uniform(-2, 2), R.uniform(.85, 1.25))
    for k in range(3): prop('bench', R.uniform(b['x0'] + 6, b['x1'] - 6), R.uniform(b['z0'] + 6, b['z1'] - 6), R.uniform(0, 6.28))
greens = [[-313, -198, -167, -52], [-150, -116, -98, -70], [-151, 40, -89, 116], [173, -112, 227, -58]]
gravel = [[-249, -152, -186, -98]]
for b in blocks:
    if b['kind'] == 'gen': gen_block(b)
    elif b['kind'] == 'towers': gen_block(b)
    elif b['kind'] == 'park': park(b); greens.append([b['x0'] + 2, b['z0'] + 2, b['x1'] - 2, b['z1'] - 2])
# ---------------- landmark colliders (positions match the Blender models) ----------------
LM = []
def lm(name, x, z, label=True): LM.append(dict(name=name, x=x, z=z, label=label))
col(-149.3, -138.7, -47.3, -36.7, 93); lm('BIG BEN', -144, -42)
col(-139, -99, -62.7, -38.3, 17); col(-109.7, -96.3, -57.2, -43.8, 49); lm('HOUSES OF PARLIAMENT', -119, -50)
for sx, sz in ((-140, -95), (-125, -88), (-110, -96)): col(sx - 1, sx + 1, sz - 1, sz + 1, 3)
col(-282, -248.2, -170, -80, 21); col(-236.4, -235.6, -176, -130, 2.6); col(-236.4, -235.6, -120, -74, 2.6); col(-218, -206, -131, -119, 14)
for z in (-134, -116): col(-234.9, -233.1, z - .9, z + .9, 3)
lm('BUCKINGHAM PALACE', -262, -125)
col(-130, -110, 50.5, 53.5, 4); lm('LONDON EYE', -120, 37)
for tz in (-16, 16):
    for sx in (-1, 1): col(160 + sx * 8.3 if sx > 0 else 148, 172 if sx > 0 else 160 - 8.3, tz - 5.5, tz + 5.5, 42)
for sz in (-1, 1):
    for sx in (-1, 1): col(160 + sx * 9.9 - 1.6, 160 + sx * 9.9 + 1.6, sz * 33.5 - 1.6, sz * 33.5 + 1.6, 15)
lm('TOWER BRIDGE', 160, 0)
for c in ((173, 227, -112, -110), (173, 175, -112, -58), (225, 227, -112, -58), (173, 196, -60, -58), (204, 227, -60, -58)): col(*c, 6)
col(186.6, 213.4, -96.4, -73.6, 19); lm('TOWER OF LONDON', 200, -85)
col(100, 140, 65, 105, 150); lm('THE SHARD', 120, 85)
col(110, 130, -175, -155, 88); lm('THE GHERKIN', 120, -165)
col(29, 51, -256, -234, 86); col(186, 214, -183, -147, 117)
lm('THE MALL', -80, -125, False); lm('SOUTH BANK', -40, 90, False); lm('THE CITY', 160, -230, False); lm("ST THOMAS' HOSPITAL", -200, 85); lm('SCOTLAND YARD', -40, -85); lm('CANARY WHARF', 360, -160); lm('HYDE PARK', -359, -245)
# landmark gardens
for x in range(-146, -101, 11):
    for z in (-113, -73): tree(x, z, .9)
for x in range(-147, -92, 10):
    for z in (70, 90, 110): tree(x + R.uniform(-2, 2), z + R.uniform(-2, 2), R.uniform(.9, 1.15))
for x in range(-310, -170, 13):
    for z in range(-194, -56, 13):
        tx, tz = x + R.uniform(-3, 3), z + R.uniform(-3, 3)
        if -253 < tx < -183 and -156 < tz < -94: continue
        if tx < -248 and -176 < tz < -74: continue
        if -136 < tz < -114 or -240 < tx < -232: continue
        tree(tx, tz, R.uniform(.9, 1.2))
park(dict(x0=-153, x1=-87, z0=-198, z1=-132))
for x, z in ((97, -190), (143, -140), (97, -140), (143, -190)): tree(x, z, .8)
# ---------------- river, bridges, embankments ----------------
gaps = [(b - 8.2 - (2 if abs(b) == RB else 0), b + 8.2 + (2 if abs(b) == RB else 0)) for b in BRIDGES]
for s in (-1, 1):
    x0 = -math.sqrt(PROM ** 2 - RIVER ** 2)
    for g0, g1 in gaps + [(-x0, -x0)]:
        if g0 > x0: col(x0, g0, s * RIVER - .8, s * RIVER + .8, 1)
        x0 = g1
    for x in range(-int(RB) + 16, int(RB) - 14, 14):
        if any(abs(x - b) < 14 for b in BRIDGES) or -156 < x < -84: continue
        tree(x, s * 34, .85)
        if (x // 14) % 2 == 0: prop('lamp', x + 7, s * 31.4, 0 if s > 0 else math.pi); col(x + 6.75, x + 7.25, s * 31.4 - .25, s * 31.4 + .25, 5)
bridges = []
for bx in BRIDGES:
    hwb = RHW if abs(bx) == RB else RW
    bridges.append(dict(x=bx, hw=hwb + .9, style={-160: 'westminster', 160: 'tower', 0: 'stone'}.get(bx, 'modern')))
    for s in (-1, 1):
        col(bx + s * (hwb + .9) - .4, bx + s * (hwb + .9) + .4, -RIVER - 1, RIVER + 1, 1.1)
        for z in range(-RIVER + 6, RIVER - 2, 12): prop('lamp', bx + s * (hwb + .9), z, -s * math.pi / 2 + (math.pi if s < 0 else 0))
# ---------------- street furniture along roads ----------------
for e in edges:
    a, b = nodes[e['a']], nodes[e['b']]
    if e.get('bridge') or e.get('curve'): continue
    hz = a['z'] == b['z']; L = abs(b['x'] - a['x']) if hz else abs(b['z'] - a['z']); hw = e['hw']
    ia = RW + 2 if a['deg'] > 2 else 0; ib = RW + 2 if b['deg'] > 2 else 0
    lo = (min(a['x'], b['x']) if hz else min(a['z'], b['z']))
    first_is_a = (a['x'] if hz else a['z']) == lo
    ilo, ihi = (ia, ib) if first_is_a else (ib, ia)
    def P(t, side): return (lo + t, a['z'] + side) if hz else (a['x'] + side, lo + t)
    for side in (-1, 1):
        for t in range(int(ilo + 12), int(L - ihi - 8), 26 if not e['ring'] else 22):
            x, z = P(t, side * (hw + .55)); facing = (0 if side < 0 else math.pi) if hz else (math.pi / 2 if side < 0 else -math.pi / 2)
            prop('lamp', x, z, facing); col(x - .25, x + .25, z - .25, z + .25, 5)
        if e['ring']:
            for t in range(int(ilo + 25), int(L - ihi - 10), 22):
                x, z = P(t, side * (hw + 2.8)); tree(x, z, .9)
        else:
            for t, ok in ((ilo + 2.2, ilo > 0), (L - ihi - 2.2, ihi > 0)):
                if ok and R.random() < .5: x, z = P(t, side * (hw + .45)); prop('beacon', x, z); col(x - .15, x + .15, z - .15, z + .15, 3)
for x, z, s in ((-40, -54.5, 1), (120, 54.5, -1), (40, -134.5, 1), (-40, 134.5, -1), (280, -54.5, 1), (-280, 54.5, -1)):
    prop('busstop', x, z, 0 if s > 0 else math.pi); col(x - 2, x + 2, z - .8, z + .8, 2.4)
# ring road: lamps on both kerbs, trees on the seafront promenade and along the inner pavement (no map edge: the sea wall is the boundary)
jang = [math.atan2(nodes[i]['z'], nodes[i]['x']) for i in ring_nodes if nodes[i]['k'] == 'j']
def near_junction(a, metres): return any(abs((a - j + math.pi) % (2 * math.pi) - math.pi) * RING < metres for j in jang)
n_l = int(2 * math.pi * RING / 26)
for k in range(n_l):
    a = (k + .5) / n_l * 2 * math.pi; ca, sa = math.cos(a), math.sin(a)
    if abs(RING * sa) < RIVER + 10: continue
    for rr, face in ((RIN - .55, a), (ROUT + .55, a + math.pi)):
        if rr < RING and near_junction(a, 14): continue
        x, z = rr * ca, rr * sa; prop('lamp', x, z, -face + math.pi / 2); col(x - .25, x + .25, z - .25, z + .25, 5)
    if k % 2 == 0:
        x, z = (PROM - 3.2) * ca, (PROM - 3.2) * sa; tree(x, z, .95)
    elif k % 4 == 1: prop('bench', (PROM - 1.6) * ca, (PROM - 1.6) * sa, -a + math.pi / 2)
for b in blocks:   # trees along the curved edge of the outer districts
    if b.get('kind') != 'district': continue
    pts = [p for p in b['poly'] if abs(math.hypot(*p) - RIN) < .5]
    if len(pts) < 2: continue
    angs_b = sorted(math.atan2(p[1], p[0]) for p in pts); a0, a1 = angs_b[0], angs_b[-1]
    if a1 - a0 > math.pi: continue
    n_t = int((a1 - a0) * (RIN - 4) / 13)
    for k in range(1, n_t):
        a = a0 + (a1 - a0) * k / n_t
        if near_junction(a, 16): continue
        tree((RIN - 4) * math.cos(a), (RIN - 4) * math.sin(a), R.uniform(.85, 1.1))
out = dict(half=HALF, river=RIVER, rw=RW, rwr=RWR, chunk=120, nodes=nodes, edges=edges, blocks=blocks, zones=ZONES, lots=lots, props=props,
           colliders=colliders, billboards=billboards, greens=greens, gravel=gravel, bridges=bridges, landmarks=LM, ring=dict(r=RING, hw=RHW, rin=RIN, rout=ROUT, prom=PROM),
           start=[-173, -34.5, math.pi / 2], hospital=[-200, 54.5, 0], station=[-30, -54.5, math.pi])
os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'assets', 'city'), exist_ok=True)
p = os.path.join(os.path.dirname(__file__), '..', 'assets', 'city', 'layout.json')
json.dump(out, open(p, 'w'), separators=(',', ':'))
from collections import Counter
print('nodes', len(nodes), 'edges', len(edges), 'blocks', len(blocks), Counter(b['kind'] for b in blocks), 'lots', len(lots), 'props', len(props), Counter(p[0] for p in props), 'colliders', len(colliders), 'bytes', os.path.getsize(p))
