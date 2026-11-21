"""Hypercar in the shape of the Bugatti Chiron, built from scratch -> assets/cars/hyper.glb (+ its entry in specs.json).
1. Body: a cage of sections (14 control points per half-section) with three blended zones - hood between raised front
   fenders with a centre spine, a narrow teardrop cabin, and the rear haunches/engine cover - closed with gridded nose
   and tail caps, creased, subdivided twice, wheel arches cut with booleans.
2. Details are projected onto the finished body with BVH ray casts so they sit exactly on the curved surface:
   the horseshoe (one smooth symmetric outline, constant-width accent surround, black fill, oval badge) and the quad-LED
   headlights are the only things on the otherwise clean front; the side C-line and air intake, the full-width rear light bar, diffuser, quad exhausts, roof fin, mirrors.
Blender axes: x = side, y = length (nose at -y), z = up."""
import bpy, bmesh, math, os, json
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
def hexc(h): h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]; return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c] + [1]
MATS = {}
def mat(n, c, r=.5, m=0.0, e=None, es=0.0):
    x = bpy.data.materials.new(n); x.use_nodes = True; b = x.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = hexc(c); b.inputs['Roughness'].default_value = r; b.inputs['Metallic'].default_value = m
    if e: b.inputs['Emission Color'].default_value = hexc(e); b.inputs['Emission Strength'].default_value = es
    MATS[n] = x
bpy.ops.wm.read_factory_settings(use_empty=True)
for a in (('Paint', '#ffffff', .25, .3), ('Carbon', '#0f1826', .3, .5), ('Glass', '#0e1419', .05), ('Black', '#111213', .55), ('Under', '#0a0a0b', .9), ('Gap', '#050505', .9),
          ('Grille', '#0b0c0d', .6), ('Lens', '#1a1d22', .06, .6), ('Chrome', '#d9dde2', .12, 1.0), ('Accent', '#2a6fd8', .25, .6), ('Interior', '#2a2b2e', .8), ('Seat', '#3a2a22', .7),
          ('PlateR', '#f2c200', .4)): mat(*a)
mat('Shoe', '#060708', .85); mat('Mesh', '#34383e', .45, .7); mat('Badge', '#b3101c', .3, .2); mat('LightF', '#f6f7fb', .05, 0, '#ffffff', 2.0); mat('LightR', '#a50d12', .15, 0, '#ff1a1a', 1.6)
SC = bpy.context.scene.collection
# ------------------------------------------------------------------ dimensions
L, W, H, R = 4.544, 2.038, 1.212, .365; W2 = W / 2; FO, WB = .98, 2.711
Y = lambda t: -L / 2 + t * L
def pchip(keys):
    keys = sorted(keys); xs = [k[0] for k in keys]; ys = [k[1] for k in keys]; n = len(xs)
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
# ------------------------------------------------------------------ profiles
plan = pchip([(0, .80), (.02, .90), (.05, .955), (.10, .99), (.18, 1.0), (.26, 1.0), (.36, .955), (.48, .94), (.60, .965), (.72, 1.0), (.86, 1.0), (.94, .97), (.985, .88), (1, .76)])
zb = pchip([(0, .14), (.06, .11), (.94, .12), (1, .22)])
zs0 = pchip([(0, .17), (.06, .15), (.94, .17), (1, .27)])
zs1 = pchip([(0, .25), (.06, .22), (.94, .25), (1, .35)])
zmid = pchip([(0, .35), (.1, .36), (.9, .40), (1, .45)])
zbul = pchip([(0, .42), (.18, .50), (.5, .52), (.75, .58), (1, .60)])
zsh = pchip([(0, .655), (.08, .73), (.20, .80), (.30, .77), (.38, .80), (.60, .86), (.72, .93), (.85, .935), (.95, .90), (1, .855)])
hz = pchip([(0, .615), (.04, .625), (.12, .65), (.22, .67), (.32, .73), (.37, .79)])
zroof = pchip([(.34, .84), (.40, .95), (.46, 1.08), (.52, 1.18), (.57, 1.212), (.63, 1.20), (.70, 1.14), (.78, 1.04), (.86, .975)])
wr = pchip([(.34, .88), (.42, .75), (.50, .645), (.60, .60), (.70, .58), (.80, .53), (.88, .50)])
zc = pchip([(.78, 1.0), (.86, .975), (.94, .94), (1, .885)])
def ring(t):
    """half section: 14 points from the bottom centre round to the top centre"""
    w = W2 * plan(t); s6 = zsh(t)
    zu = zbul(t)
    low = [(0, zb(t)), (w * .80, zb(t)), (w * .93, zs0(t)), (w * .97, zs1(t)), (w * .995, zmid(t)), (w, zu), (w * .998, lerp(zu, s6, .4)), (w * .993, lerp(zu, s6, .75)), (w * .985, s6)]
    h = hz(t); fz = s6 + .03
    A = [(w * .92, s6 + .03), (w * .80, fz + .02), (w * .66, fz + .002), (w * .48, h - .015), (w * .28, h - .005), (w * .09, h + .022), (0, h + .034)]
    zr = zroof(t); r_ = W2 * wr(t); zbelt = s6 + .04
    B = [(w * .90, s6 + .02), (w * .86, zbelt), (lerp(w * .86, r_, .5) - .02, (zbelt + zr - .08) / 2 + .02), (r_, zr - .08), (r_ * .72, zr - .03), (r_ * .36, zr - .008), (0, zr)]
    c_ = zc(t)
    Cc = [(w * .90, s6 + .02), (w * .80, s6 + .04), (w * .64, s6), (w * .46, c_ - .01), (w * .26, c_), (w * .08, c_ + .015), (0, c_ + .02)]
    a = 1 - sm(.34, .41, t); c = sm(.80, .87, t); b = max(0.0, 1 - a - c)
    up = [(A[i][0] * a + B[i][0] * b + Cc[i][0] * c, A[i][1] * a + B[i][1] * b + Cc[i][1] * c) for i in range(7)]
    upm = [up[0]]
    for i in range(1, 7): upm += [((up[i - 1][0] + up[i][0]) / 2, (up[i - 1][1] + up[i][1]) / 2), up[i]]
    return low + upm
# ------------------------------------------------------------------ the C (side two-tone): ellipse open to the front
C_T0, C_A, C_Z0, C_B = .50, .19, .74, .46
def c_rear(z): return C_T0 + C_A * math.sqrt(max(0.0, 1 - ((z - C_Z0) / C_B) ** 2)) if abs(z - C_Z0) < C_B else C_T0
def zone(t): return 'A' if t < .38 else ('C' if t > .84 else 'B')
def old(s): return s if s <= 4 else (5 if s <= 7 else (6 if s == 8 else 7 + (s - 9) // 2))
def classify(t, s, z):
    zn = zone(t); s = old(s)
    if s <= 1: return 'Under'
    if s == 2: return 'Carbon'
    if zn == 'A':
        return 'Paint'
    if zn == 'C': return 'Paint'
    if t < .41: return 'Paint'                         # cowl: the windscreen starts where the surface turns up
    # cabin
    if s in (3, 4, 5, 6, 7):
        if s == 7: return 'Black' if .40 < t < .60 else 'Paint'
        return 'Paint'
    if s in (8, 9): return 'Glass' if .40 < t < .60 else 'Carbon'
    if t < .505: return 'Glass'                        # windscreen
    if .64 < t < .79 and s >= 11: return 'Glass'       # engine-bay window
    return 'Carbon'                                    # roof
# ------------------------------------------------------------------ build the cage
ts = sorted(set([round(x, 4) for x in [0, .008, .02, .04, .065, .095, .13, .17, .21, .25, .29, .307, .313, .33, .36, .385, .41, .44, .47, .505, .53, .552, .558, .575,
                                       .60, .63, .66, .69, .72, .75, .78, .81, .84, .87, .90, .93, .955, .975, .99, 1]]))
bm = bmesh.new(); rings = []; tags = {}; LEAN = {}
for t in ts:
    half = ring(t); y = Y(t)
    lean = lambda z, t=t, half=half: .10 * sm(zb(t) + .12, max(half[-1][1], half[8][1]), z) ** 1.5 * (1 - sm(0, .07, t)) - .05 * sm(zb(t), half[-1][1], z) * sm(.95, 1, t)
    LEAN[t] = lean; full = half + [(-x, z) for x, z in reversed(half[1:-1])]
    rings.append([bm.verts.new((x, y + lean(z), z)) for x, z in full])
n = len(rings[0]); NH = 21; KT = 8
for i in range(len(ts) - 1):
    tm = (ts[i] + ts[i + 1]) / 2; hr = ring(tm)
    for k in range(n):
        f = bm.faces.new((rings[i][k], rings[i][(k + 1) % n], rings[i + 1][(k + 1) % n], rings[i + 1][k]))
        s = k if k < NH else (n - 1 - k); tags[f] = classify(tm, s, (hr[s][1] + hr[s + 1][1]) / 2)
def cap(rg, front, t):
    """end cap: rows 1..KT-1 are horizontal lines between matching ring points on either side; the top row is the ring's
    own upper edge (shoulder -> centre -> shoulder), so the cap shares every boundary vertex with the loft (no T-joints)"""
    hl = rg[:NH + 1]; hr_ = [rg[0]] + rg[NH + 1:][::-1] + [rg[NH]]
    top = hl[KT:NH + 1] + hr_[KT:NH][::-1]
    x0 = hl[KT].co.x; U = [v.co.x / x0 for v in top]; zt0 = hl[KT].co.z; z5 = hl[5].co.z
    yb = Y(t); ln = LEAN[t]; sg = -1 if front else 1
    rows = [[rg[0]] * len(top)]
    for k in range(1, KT):
        xk, zk = hl[k].co.x, hl[k].co.z; al = sm(z5, zt0, zk) ** 1.2 if k > 5 else 0.0
        vf = sm(.5, 3, k) * (1 - sm(5.5, 8, k)); row = []
        for j, u in enumerate(U):
            if j == 0: row.append(hl[k]); continue
            if j == len(U) - 1: row.append(hr_[k]); continue
            z = zk + (top[j].co.z - zt0) * al
            b = (.05 * (1 - u * u) ** 2 + .03 * math.exp(-((abs(u) - .8) / .13) ** 2)) if front else .05 * (1 - u * u) ** 1.5
            row.append(bm.verts.new((u * xk, yb + ln(z) + sg * b * vf, z)))
        rows.append(row)
    rows.append(top); out = []
    for k in range(KT):
        for j in range(len(top) - 1):
            q = []
            for v in (rows[k][j], rows[k][j + 1], rows[k + 1][j + 1], rows[k + 1][j]):
                if v not in q: q.append(v)
            if len(q) < 3: continue
            out.append((bm.faces.new(q if not front else q[::-1]), k, (abs(U[j]) + abs(U[j + 1])) / 2))
    return out
def nose(k, c): return 'Under' if k == 0 else 'Paint'        # clean front: only the horseshoe and the lamps sit on it
for f, k, c in cap(rings[0], True, ts[0]): tags[f] = nose(k, c)
for f, k, c in cap(rings[-1], False, ts[-1]): tags[f] = 'Carbon'
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
cl = bm.edges.layers.float.get('crease_edge') or bm.edges.layers.float.new('crease_edge')
for i in range(len(rings) - 1):
    for k, cv in ((2, .4), (8, .35), (11, .75 if .38 < ts[i] < .84 else (.55 if ts[i] < .38 else .15)), (15, .7 if .38 < ts[i] < .84 else (.3 if ts[i] < .38 else 0)), (21, .35 if ts[i] < .38 else 0)):
        for kk in (k, n - k):
            e = bm.edges.get((rings[i][kk], rings[i + 1][kk]))
            if e: e[cl] = cv
for rg in (rings[0], rings[-1]):
    for k in range(n):
        e = bm.edges.get((rg[k], rg[(k + 1) % n]))
        if e: e[cl] = .45
ORDER = ['Paint', 'Shoe', 'Mesh', 'Badge', 'Carbon', 'Glass', 'Black', 'Under', 'Gap', 'Grille', 'Lens', 'LightF', 'LightR', 'Chrome', 'Accent', 'PlateR', 'Interior', 'Seat']
bm.faces.index_update(); flut = {f.index: tags.get(f, 'Paint') for f in bm.faces}
me = bpy.data.meshes.new('Body'); bm.to_mesh(me); bm.free()
body = bpy.data.objects.new('Body', me); SC.objects.link(body)
for nm in ORDER: me.materials.append(MATS[nm])
for p in me.polygons: p.material_index = ORDER.index(flut[p.index]); p.use_smooth = True
def apply_mod(ob, mtype, **kw):
    m = ob.modifiers.new(mtype, mtype)
    for k, v in kw.items(): setattr(m, k, v)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True); bpy.ops.object.modifier_apply(modifier=m.name); ob.select_set(False)
apply_mod(body, 'SUBSURF', levels=2, render_levels=2)
def prim(name, mname, build, smooth=True):
    bm = bmesh.new(); build(bm); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); SC.objects.link(o); me.materials.append(MATS[mname])
    for p in me.polygons: p.use_smooth = smooth
    return o
def cyl(bm, c, r, d, axis='X', seg=24, r2=None):
    rot = {'X': Matrix.Rotation(math.pi / 2, 4, 'Y'), 'Y': Matrix.Rotation(math.pi / 2, 4, 'X'), 'Z': Matrix.Identity(4)}[axis]
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=d, matrix=Matrix.Translation(Vector(c)) @ rot)
def cube(bm, c, s, rx=0.0, rz=0.0):
    bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation(Vector(c)) @ Matrix.Rotation(rz, 4, 'Z') @ Matrix.Rotation(rx, 4, 'X') @ Matrix.Diagonal((s[0], s[1], s[2], 1)))
yf, yr = -L / 2 + FO, -L / 2 + FO + WB
XI = .66                                                   # wheel wells only reach this far in: the hood and tunnel stay whole
for wy in (yf, yr):
    cut = prim('cut', 'Black', lambda bm, wy=wy: [cyl(bm, (sx * (XI + W2 + .4) / 2, wy, R), R + .05, W2 + .4 - XI, 'X', 48) for sx in (-1, 1)])
    mo = body.modifiers.new('b', 'BOOLEAN'); mo.object = cut; mo.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = body; bpy.ops.object.modifier_apply(modifier=mo.name); bpy.data.objects.remove(cut)
# headlamp recesses carved into the front corners (tools/blender/chiron_recess.py)
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chiron_recess.py')).read())
# recessed glass, side intake
bm = bmesh.new(); bm.from_mesh(me); mi = {nm: i for i, nm in enumerate(ORDER)}; bvh0 = BVHTree.FromBMesh(bm)
for names, th, dp, rim in ((('Glass',), .012, -.014, 'Black'), (('Grille',), .015, -.07, 'Black'), (('Shoe',), .01, -.05, 'Black'), (('Lens',), .012, -.03, 'Black')):
    fs = [f for f in bm.faces if ORDER[f.material_index] in names]
    if fs:
        r = bmesh.ops.inset_region(bm, faces=fs, thickness=th, depth=dp, use_even_offset=True)
        for f in r['faces']: f.material_index = mi[rim]
bm.to_mesh(me)
# ------------------------------------------------------------------ project details onto the body surface
bvh = BVHTree.FromBMesh(bm); bm.free()
def hit(o, d):
    loc, nrm, _, _ = bvh.ray_cast(Vector(o), Vector(d).normalized(), 10)
    return (loc, nrm) if loc is not None else (None, None)
def snap(o, d, guess, off):
    l, n_ = hit(o, d)
    if l is None: l, n_, _, _ = bvh.find_nearest(Vector(guess))
    return l + n_ * off, n_
def on_front(x, z, off=.004): return snap((x, -L / 2 - 1, z), (0, 1, 0), (x, -L / 2 + .05, z), off)
def on_rear(x, z, off=.004): return snap((x, L / 2 + 1, z), (0, -1, 0), (x, L / 2 - .05, z), off)
def on_side(sx, t, z, off=.004): return snap((sx * 2, Y(t), z), (-sx, 0, 0), (sx * W2, Y(t), z), off)
def on_top(x, t, off=.004): return snap((x, Y(t), 3), (0, 0, -1), (x, Y(t), 1.1), off)
def decal(bm, outline, proj, rings_=3):
    """filled patch: outline (2D, convex-ish) + interior rings toward the centroid, every vertex projected onto the body"""
    cx = sum(p[0] for p in outline) / len(outline); cz = sum(p[1] for p in outline) / len(outline)
    R_ = [[bm.verts.new(proj(cx + (px - cx) * (1 - k / (rings_ + 1)), cz + (pz - cz) * (1 - k / (rings_ + 1)))[0]) for px, pz in outline] for k in range(rings_ + 1)]
    c = bm.verts.new(proj(cx, cz)[0]); m = len(outline)
    for k in range(rings_):
        for i in range(m): bm.faces.new((R_[k][i], R_[k][(i + 1) % m], R_[k + 1][(i + 1) % m], R_[k + 1][i]))
    for i in range(m): bm.faces.new((R_[-1][i], R_[-1][(i + 1) % m], c))
    for f in bm.faces:
        f.normal_update(); n_ = bvh.find_nearest(f.calc_center_median())[1]
        if n_ is not None and f.normal.dot(n_) < 0: f.normal_flip()
def tube(bm, path, proj, w=.02, h=.014, closed=False):
    """flat trim strip following a 2D path on the body: width w across the path, standing h off the surface"""
    P = [proj(a, b) for a, b in path]; m = len(P); vs = []
    for i, (p, nrm) in enumerate(P):
        q0, q1 = P[max(0, i - 1)][0], P[min(m - 1, i + 1)][0]
        if closed: q0, q1 = P[(i - 1) % m][0], P[(i + 1) % m][0]
        tng = (q1 - q0).normalized(); side = tng.cross(nrm).normalized() * (w / 2); up = nrm * h
        vs.append([bm.verts.new(p - side), bm.verts.new(p + side), bm.verts.new(p + side + up), bm.verts.new(p - side + up)])
    for i in range(m - (0 if closed else 1)):
        a, b = vs[i], vs[(i + 1) % m]
        for q in range(4): bm.faces.new((a[q], a[(q + 1) % 4], b[(q + 1) % 4], b[q]))
    if not closed: bm.faces.new(vs[0][::-1]); bm.faces.new(vs[-1])
def y0(x, z):                                              # front surface (before any recesses)
    loc, _, _, _ = bvh0.ray_cast(Vector((x, -L / 2 - 1, z)), Vector((0, 1, 0)), 10)
    return loc.y if loc is not None else bvh0.find_nearest(Vector((x, -L / 2, z)))[0].y
def catmull(P, per=12):                                    # closed centripetal Catmull-Rom through P
    out = []; m = len(P)
    for i in range(m):
        p0, p1, p2, p3 = [Vector(P[(i + d) % m]) for d in (-1, 0, 1, 2)]
        def tj(a, b, t): return t + max(1e-6, (b - a).length) ** .5
        t0 = 0; t1 = tj(p0, p1, t0); t2 = tj(p1, p2, t1); t3 = tj(p2, p3, t2)
        for k in range(per):
            t = t1 + (t2 - t1) * k / per
            a1 = p0 * ((t1 - t) / (t1 - t0)) + p1 * ((t - t0) / (t1 - t0)); a2 = p1 * ((t2 - t) / (t2 - t1)) + p2 * ((t - t1) / (t2 - t1)); a3 = p2 * ((t3 - t) / (t3 - t2)) + p3 * ((t - t2) / (t3 - t2))
            b1 = a1 * ((t2 - t) / (t2 - t0)) + a2 * ((t - t0) / (t2 - t0)); b2 = a2 * ((t3 - t) / (t3 - t1)) + a3 * ((t - t1) / (t3 - t1))
            out.append(b1 * ((t2 - t) / (t2 - t1)) + b2 * ((t - t1) / (t2 - t1)))
    return out
def resample(P, n):                                        # n points evenly spaced along the closed curve
    seg = [(P[i], P[(i + 1) % len(P)]) for i in range(len(P))]; tot = sum((b - a).length for a, b in seg); out = []; i = 0; acc = 0.0
    for k in range(n):
        d = tot * k / n
        while acc + (seg[i][1] - seg[i][0]).length < d: acc += (seg[i][1] - seg[i][0]).length; i += 1
        a, b = seg[i]; out.append(a.lerp(b, (d - acc) / max(1e-9, (b - a).length)))
    return out
# horseshoe centreline (front view x, z): round top, sides narrowing toward a softly rounded bottom - symmetric by construction
HALF = [(.12, .598), (.195, .548), (.226, .468), (.224, .385), (.208, .295), (.186, .212), (.152, .158), (.082, .136)]
KEYS = [(0, .616)] + HALF + [(0, .13)] + [(-x, z) for x, z in HALF[::-1]]
CL = resample(catmull([Vector(p) for p in KEYS], 16), 96)
def offset(P, d):                                          # constant-width offset of the closed 2D curve (d > 0 = outward)
    out = []
    for i in range(len(P)):
        t = (P[(i + 1) % len(P)] - P[i - 1]).normalized(); nrm = Vector((t.y, -t.x))
        out.append(P[i] + nrm * d)
    return out
if sum((CL[(i + 1) % len(CL)].x - CL[i].x) * (CL[(i + 1) % len(CL)].y + CL[i].y) for i in range(len(CL))) < 0: CL = CL[::-1]
SO, SI = offset(CL, .017), offset(CL, -.017)
if max(p.y for p in SO) < max(p.y for p in SI): SO, SI = SI, SO
def shoe_frame(bm):
    V = []
    for o, c, i in zip(SO, CL, SI):
        V.append([bm.verts.new((o.x, y0(o.x, o.y) + .02, o.y)), bm.verts.new((o.x, y0(o.x, o.y) - .016, o.y)), bm.verts.new((c.x, y0(c.x, c.y) - .026, c.y)),
                  bm.verts.new((i.x, y0(i.x, i.y) - .016, i.y)), bm.verts.new((i.x, y0(i.x, i.y) + .02, i.y))])
    for k in range(len(V)):
        a, b = V[k], V[(k + 1) % len(V)]
        for q in range(5): bm.faces.new((a[q], a[(q + 1) % 5], b[(q + 1) % 5], b[q]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
prim('shoerim', 'Accent', shoe_frame)
def shoe_fill(bm):                                         # plain black inside the horseshoe
    cx = sum(p.x for p in SI) / len(SI); cz = sum(p.y for p in SI) / len(SI); m = len(SI)
    P = lambda x, z: bm.verts.new((x, y0(x, z) - .003, z))
    R_ = [[P(cx + (p.x - cx) * (1 - k / 4), cz + (p.y - cz) * (1 - k / 4)) for p in SI] for k in range(4)]; c = P(cx, cz)
    for k in range(3):
        for i in range(m): bm.faces.new((R_[k][i], R_[k][(i + 1) % m], R_[k + 1][(i + 1) % m], R_[k + 1][i]))
    for i in range(m): bm.faces.new((R_[-1][i], R_[-1][(i + 1) % m], c))
    for f in bm.faces:
        f.normal_update()
        if f.normal.y > 0: f.normal_flip()
prim('shoe', 'Shoe', shoe_fill)
def badge(bm):
    z = .532; g = bmesh.ops.create_cone(bm, cap_ends=True, segments=28, radius1=.058, radius2=.058, depth=.012, matrix=Matrix.Translation(Vector((0, y0(0, z) - .008, z))) @ Matrix.Rotation(math.pi / 2, 4, 'X'))
    for v in g['verts']: v.co.z = z + (v.co.z - z) * .6
prim('badge', 'Badge', badge)
for sx in (-1, 1):
    # quad-LED headlights (tools/blender/chiron_lamps.py), run once per side with sx = -1 / 1
    exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chiron_lamps.py')).read())
    # side: the C-line and the intake inside it
    def S(t, z, sx=sx, off=.006):
        loc, nrm, _, _ = bvh0.ray_cast(Vector((sx * 2, Y(t), z)), Vector((-sx, 0, 0)), 10)
        if loc is None: loc, nrm, _, _ = bvh0.find_nearest(Vector((sx * W2, Y(t), z)))
        return loc + nrm * off, nrm
    def t_in(z): return C_T0 + (C_A - .03) * math.sqrt(max(0.0, 1 - ((z - C_Z0) / (C_B - .05)) ** 2))
    zz = [.44 + .44 * k / 10 for k in range(11)]
    prim('sideintake', 'Shoe', lambda bm, S=S: decal(bm, [(.585, z) for z in zz[::-1]] + [(t_in(z), z) for z in zz], lambda t, z: S(t, z, off=.004), 2))
    path = [(lerp(.415, C_T0, k / 6), zroof(lerp(.415, C_T0, k / 6)) - .1) for k in range(6)]
    for k in range(25): th = math.pi / 2 - k / 24 * math.pi; path.append((C_T0 + C_A * math.cos(th), min(zroof(C_T0) - .1, C_Z0 + C_B * math.sin(th))))
    path += [(lerp(C_T0, .30, k / 8), C_Z0 - C_B) for k in range(1, 9)]
    prim('cline', 'Chrome', lambda bm, path=path, S=S: tube(bm, path, S, .045, .016))
    def mirror(bm, sx=sx):
        bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=8, radius=1, matrix=Matrix.Translation(Vector((sx * (W2 * .84 + .1), Y(.41), zsh(.41) + .14))) @ Matrix.Diagonal((.1, .05, .05, 1)))
        cube(bm, (sx * (W2 * .84 + .02), Y(.41) + .015, zsh(.41) + .1), (.1, .025, .02), rx=0, rz=0)
    prim('mirror', 'Carbon', mirror)
# rear: full-width light bar, diffuser, quad exhausts, plate, wing, roof fin
prim('lightbar', 'LightR', lambda bm: tube(bm, [(-.95 + 1.9 * k / 24, .805) for k in range(25)], lambda x, z: on_rear(x, z, .006), .045, .02))
prim('diffuser', 'Black', lambda bm: decal(bm, [(-.88, .13), (.88, .13), (.84, .40), (-.84, .40)], lambda x, z: on_rear(x, z, .004), 2))
prim('rearmesh', 'Shoe', lambda bm: decal(bm, [(-.9, .43), (.9, .43), (.92, .75), (-.92, .75)], lambda x, z: on_rear(x, z, .004), 2))
prim('rearslats', 'Mesh', lambda bm: [tube(bm, [(-.86 + 1.72 * j / 16, z) for j in range(17)], lambda x, z: on_rear(x, z, .008), .012, .008) for z in (.49, .56, .63, .70)])
for x in (-.085, .085):
    for z in (.23, .34): prim('pipe', 'Chrome', lambda bm, x=x, z=z: cyl(bm, (x, L / 2 - .08, z), .048, .2, 'Y', 18))
prim('plate', 'PlateR', lambda bm: decal(bm, [(-.26, .44), (.26, .44), (.26, .55), (-.26, .55)], lambda x, z: on_rear(x, z, .008), 1))
prim('wing', 'Carbon', lambda bm: cube(bm, (0, L / 2 - .3, zc(.93) + .018), (W - .6, .42, .022), rx=-.04))
prim('fin', 'Carbon', lambda bm: tube(bm, [(0, .52 + .3 * k / 12) for k in range(13)], lambda x, t: on_top(x, t, .0), .03, .035))
# interior seen through the glass
prim('dash', 'Interior', lambda bm: cube(bm, (0, Y(.47), .72), (1.3, .3, .12)))
prim('seats', 'Seat', lambda bm: [cube(bm, (sx * .36, Y(.555), .45), (.5, .5, .12)) or cube(bm, (sx * .36, Y(.6), .75), (.5, .12, .62), rx=-.3) for sx in (-1, 1)])
prim('tub', 'Interior', lambda bm: cube(bm, (0, Y(.555), .42), (1.5, 1.05, .4)))
# arch liners
def liner(bm, wy, sx):                                     # inside of the wheel well: arched roof facing the wheel + inner wall
    rr = R + .042; th = [math.radians(-12 + 204 * k / 24) for k in range(25)]; xo = sx * W2 * .985; xi = sx * (XI + .005)
    A = [(wy + rr * math.cos(a), R + rr * math.sin(a)) for a in th]
    o = [bm.verts.new((xo, y, z)) for y, z in A]; i = [bm.verts.new((xi, y, z)) for y, z in A]
    for k in range(len(A) - 1):
        f = bm.faces.new((o[k], o[k + 1], i[k + 1], i[k])); f.normal_update()
        if f.normal.dot(Vector((0, wy, R)) - f.calc_center_median()) < 0: f.normal_flip()
    w = bm.faces.new(i + [bm.verts.new((xi, wy, R - .05))]); w.normal_update()
    if w.normal.x * sx < 0: w.normal_flip()
for wy in (yf, yr):
    for sx in (-1, 1): prim('liner', 'Under', lambda bm, wy=wy, sx=sx: liner(bm, wy, sx), smooth=False)
objs = [o for o in bpy.data.objects if o.type == 'MESH']
for o in objs: o.select_set(True)
bpy.context.view_layer.objects.active = body; bpy.ops.object.join()
car = bpy.context.view_layer.objects.active; car.name = 'hyper'
try: car.data.set_sharp_from_angle(angle=math.radians(55))
except Exception: pass
out = os.environ.get('CHIRON_OUT') or os.path.join(ROOT, 'assets', 'cars', 'hyper.glb')   # CHIRON_OUT: test build elsewhere, specs.json untouched
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_apply=True, export_yup=True)
SPEC = os.path.join(ROOT, 'assets', 'cars', 'specs.json'); sp = json.load(open(SPEC)) if os.path.exists(SPEC) else {}
tf, tr = FO / L, (FO + WB) / L
sp['hyper'] = dict(L=L, W=W, H=H, r=R, wz=[round(tf, 4), round(tr, 4)], track=round(min(W2 * plan(tf), W2 * plan(tr)) - .32 * R - .06, 3))
if not os.environ.get('CHIRON_OUT'): json.dump(sp, open(SPEC, 'w'), indent=1)
print('exported', out, sum(len(pl.vertices) - 2 for pl in car.data.polygons), 'tris', sp['hyper'])
