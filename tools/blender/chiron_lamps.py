"""Quad-LED headlamps for chiron.py (exec'd inside its per-side loop, sharing its globals; sx = -1 or 1).
Four rounded-square units in a row, like the real Chiron: each outline is a glowing light-guide ring (bright core,
warm edges), inside it smoked glass over a dark housing with a small round projector (chrome reflector + lens).
Each unit is rigid and flat: oriented to the chord plane of the surface under it (sampled with on_front, which lands
on the cavity floor once chiron_recess.py has carved it) and seated at the highest floor point under its footprint;
the ring's walls reach back into the floor so no gap shows where the floor falls away."""
if 'LightRing' not in MATS:
    mat('LightRing', '#fff6e8', .2, 0, '#fff3df', 2.0)     # light-guide core (warm white)
    mat('LightRingE', '#ffd29a', .2, 0, '#ffc684', 1.6)    # its warmer edges
    mat('LampHsg', '#0b0c0e', .6)                          # black housing walls
    mat('LampBack', '#6e6a66', .5)                         # smoked interior seen through the glass
    mat('ProjLens', '#8a96a4', .05, 0, '#8a96a4', 1.0)     # projector lens: a dim grey-blue glint by day, lit at night
LX, LZ = (.52, .605, .69, .775), .655                      # unit centres (|x|, z): fixed contract with chiron_recess.py
HA, HB, RC, TW = .0375, .03, .018, .0095                   # half width, half height, corner radius, ring width
F, G, P = .007, .004, .0015                                # ring front, cover glass, back plate (above the floor)
NC = 6                                                     # points per rounded corner
def rrect(a, b, r):
    out = []
    for ci, (cx, cz) in enumerate(((a - r, b - r), (r - a, b - r), (r - a, r - b), (a - r, r - b))):
        for j in range(NC):
            th = (ci + j / (NC - 1)) * math.pi / 2; out.append((cx + r * math.cos(th), cz + r * math.sin(th)))
    return out
def unit_frame(x, z):
    """origin on the floor (its highest point under the footprint) + axes U (sideways), V (up), N (out of the floor)"""
    p0, n0 = on_front(x, z, 0); S = []
    for du in (-.034, -.017, 0, .017, .034):
        for dv in (-.027, 0, .027):
            p, n_ = on_front(x + du, z + dv, 0)
            if abs((p - p0).dot(n0)) < .025: S.append((p, n_))
    N = sum((n_ for p, n_ in S if n_.dot(n0) > .95), Vector((0, 0, 0)))   # the flat floor; a lip or wall under the edge doesn't tilt it
    N = N.normalized() if N.length > 1e-6 else Vector(n0)
    if N.y > 0: N = -N
    V = (Vector((0, 0, 1)) - N * N.z).normalized(); U = V.cross(N)
    d0 = max([0.0] + [(p - p0).dot(N) for p, _ in S])
    print('LAMPDBG', sx, round(x,3), 'd0=%.4f' % d0, 'N=', tuple(round(c, 3) for c in N), 'devs', sorted(round((p - p0).dot(N), 4) for p, _ in S), len(S))
    return p0 + N * min(d0, .015), U, V, N
FR = [unit_frame(sx * x, LZ) for x in LX]
O_OUT, O_IN = rrect(HA, HB, RC), rrect(HA - TW, HB - TW, RC - TW)
def contour(bm, fr, pts, w):
    o, U, V, N = fr; return [bm.verts.new(o + U * u + V * v + N * w) for u, v in pts]
def strip(bm, fr, A, B, face='front'):
    """quads between two closed contours; face = 'front' (normal along N), 'out' / 'in' (away from / toward the centre)"""
    o, U, V, N = fr; m = len(A)
    for i in range(m):
        f = bm.faces.new((A[i], A[(i + 1) % m], B[(i + 1) % m], B[i])); f.normal_update()
        d = N if face == 'front' else (f.calc_center_median() - o) * (1 if face == 'out' else -1)
        if f.normal.dot(d) < 0: f.normal_flip()
def fan(bm, fr, A, w, c=(0, 0)):
    o, U, V, N = fr; cv = bm.verts.new(o + U * c[0] + V * c[1] + N * w); m = len(A)
    for i in range(m):
        f = bm.faces.new((A[i], A[(i + 1) % m], cv)); f.normal_update()
        if f.normal.dot(N) < 0: f.normal_flip()
def ring_pts(off):                                         # outline offset inward by off (0 = outer edge, TW = inner edge)
    return rrect(HA - off, HB - off, RC - off)
def circ(r, n, c):
    return [(c[0] + r * math.cos(2 * math.pi * k / n), c[1] + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
def lamps_housing(bm):                                     # outer wall, from the ring's front edge back into the floor
    for fr in FR: strip(bm, fr, contour(bm, fr, O_OUT, F - .0008), contour(bm, fr, O_OUT, -.02), 'out')
def lamps_edge(bm):                                        # warm edges of the light guide + its inner wall
    e = .0022
    for fr in FR:
        strip(bm, fr, contour(bm, fr, O_OUT, F - .0008), contour(bm, fr, ring_pts(e), F))
        strip(bm, fr, contour(bm, fr, ring_pts(TW - e), F), contour(bm, fr, O_IN, F - .0008))
        strip(bm, fr, contour(bm, fr, O_IN, F - .0008), contour(bm, fr, O_IN, P), 'in')
def lamps_core(bm):
    e = .0022
    for fr in FR: strip(bm, fr, contour(bm, fr, ring_pts(e), F), contour(bm, fr, ring_pts(TW - e), F))
def lamps_glass(bm):
    for fr in FR: fan(bm, fr, contour(bm, fr, O_IN, G), G)
def lamps_back(bm):
    for fr in FR: fan(bm, fr, contour(bm, fr, O_IN, P), P)
PC = (0, -.001)                                            # projector centre in the unit (u, v)
def lamps_reflector(bm):                                   # chrome bowl round the projector lens
    for fr in FR: strip(bm, fr, contour(bm, fr, circ(.015, 14, PC), P + .0003), contour(bm, fr, circ(.0095, 14, PC), P + .0006))
def lamps_lens(bm):
    for fr in FR:
        rim = contour(bm, fr, circ(.0095, 14, PC), .0026)
        strip(bm, fr, contour(bm, fr, circ(.0095, 14, PC), P + .0006), rim, 'out'); fan(bm, fr, rim, .0032, PC)
for nm, fn in (('LampHsg', lamps_housing), ('LightRingE', lamps_edge), ('LightRing', lamps_core), ('Glass', lamps_glass),
               ('LampBack', lamps_back), ('Chrome', lamps_reflector), ('ProjLens', lamps_lens)):
    prim('lamp' + nm, nm, fn)
