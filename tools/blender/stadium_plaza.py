"""Stamford Bridge - the forecourt and surroundings: club shop / hotel, statue, flags, lamps.
Exec'd by stadium() in landmarks.py with b, x0, x1, z0, z1, D, px0, px1, pz0, pz1, cx, cz, acc, BLUE, WHITE_, CLAD and all citylib helpers.
Forecourt = FX .. block edge b['x1'] (street kerb), whole east side. The entrance passage approach z EZ0..EZ1 stays clear: the statue
plinth sits just south of it (PZ). Colliders for tools/stadium_layout.py: plinth square PX+-1, PZ+-1; kiosk KX0..KX1, KZ0..KZ1."""
XE = b['x1'] - .02                    # street kerb line (district pavement ends at b['x1'] = -327, road beyond)
ZA, ZB = b['z0'] + .02, b['z1'] - .02
PY = KERB + .008                      # forecourt slabs sit 8 mm above the district pavement (no z-fighting)
def flat(poly, y, layer, tint):       # convex polygon on the ground, split into the chunks it really lies in
    for part in chunks_of(poly):
        fan(O(sum(p[0] for p in part) / len(part), sum(p[1] for p in part) / len(part)), part, y, layer, tint)
flat([(FX - .5, ZA), (FX - .5, ZB), (XE, ZB), (XE, ZA)], PY, 'pavement', '#a9adb1')
for z_ in (ZA, ZB): O(XE, z_).quad((XE, 0, z_), (XE, 0, z_), (XE, PY, z_), (XE, PY, z_), 'kerb', '#c9c6bf', ao=False) if False else None
O(XE, cz - 20).quad((XE, KERB - .01, ZA), (XE, KERB - .01, cz - 2), (XE, PY, cz - 2), (XE, PY, ZA), 'kerb', '#c9c6bf', ao=False)
O(XE, cz + 20).quad((XE, KERB - .01, cz - 2), (XE, KERB - .01, ZB), (XE, PY, ZB), (XE, PY, cz - 2), 'kerb', '#c9c6bf', ao=False)
# ---- round plaza with the statue (just south of the passage approach), tan paving ringed in dark stone
PX, PZ, PR = FX + 9.6, EZ1 + 3.4, 3.3
ring = lambda r, n=28: [(PX + math.cos(k / n * math.tau) * r, PZ + math.sin(k / n * math.tau) * r) for k in range(n)]
flat(ring(PR + .25), PY + .004, 'stone', '#77736c'); flat(ring(PR), PY + .008, 'stone', '#cbb894')
# ---- curved orange line through the forecourt, bowing out toward the street, passing between the entrance and the plaza
YL = PY + .006; N = 36; zl0, zl1 = ZA + 5, ZB - 5
def lx(z): t = (z - cz) / ((zl1 - zl0) / 2); return FX + 2.4 + 3.9 * (1 - t * t)
for k in range(N):
    za_, zb_ = zl0 + (zl1 - zl0) * k / N, zl0 + (zl1 - zl0) * (k + 1) / N; xa_, xb_ = lx(za_), lx(zb_)
    if math.hypot((xa_ + xb_) / 2 - PX, (za_ + zb_) / 2 - PZ) < PR + .4: continue
    O((xa_ + xb_) / 2, (za_ + zb_) / 2).quad((xa_ - .13, YL, zb_), (xa_ + .13, YL, zb_), (xa_ + .13, YL, za_), (xa_ - .13, YL, za_), 'paint', '#e2772b', ao=False) if False else \
        O((xa_ + xb_) / 2, (za_ + zb_) / 2).quad((xa_ - .13, YL, za_), (xb_ - .13, YL, zb_), (xb_ + .13, YL, zb_), (xa_ + .13, YL, za_), 'paint', '#e2772b', ao=False)
# ---- plinth + bronze footballer (blocky, striking a ball, facing the street)
a = O(PX, PZ); ST = '#d9d3c6'; BR = '#6c5436'
a.box(PX - 1, PX + 1, PY, PY + .3, PZ - 1, PZ + 1, 'stone', '#bdb6a8')
a.box(PX - .75, PX + .75, PY + .3, PY + 1.9, PZ - .75, PZ + .75, 'stone', ST)
a.box(PX - .85, PX + .85, PY + 1.9, PY + 2.05, PZ - .85, PZ + .85, 'stone', ST)
Y0, S = PY + 2.05, 1.2
P = lambda dx, dy, dz: (PX + dx * S, Y0 + dy * S, PZ + dz * S)
a.beam(P(0, 0, -.12), P(0, .95, -.1), .17 * S, 'metal', BR)                 # standing leg
a.beam(P(.02, .95, .1), P(-.28, .52, .14), .17 * S, 'metal', BR)            # kicking leg drawn back: thigh
a.beam(P(-.28, .52, .14), P(-.5, .2, .14), .15 * S, 'metal', BR)            # shin
a.box(PX - .02 * S, PX + .2 * S, Y0, Y0 + .08 * S, PZ - .2 * S, PZ - .05 * S, 'metal', BR)
a.beam(P(-.5, .2, .14), P(-.62, .12, .14), .1 * S, 'metal', BR)
a.beam(P(0, .92, 0), P(.1, 1.58, 0), .26 * S, 'metal', BR, w2=.42 * S)     # torso (leaning in)
a.sphere(*P(.13, 1.76, 0), .12 * S, 'metal', BR, 8, 5)
a.beam(P(.08, 1.5, -.23), P(.22, 1.12, -.55), .1 * S, 'metal', BR)         # arms out for balance
a.beam(P(.08, 1.5, .23), P(-.12, 1.22, .55), .1 * S, 'metal', BR)
a.sphere(*P(.38, .11, .02), .11 * S, 'metal', BR, 8, 5)                     # ball
# ---- bollards along the street edge, lamps, flags, benches
LAMPS = [-110, -97, -59, -46]; FLAGS = [PZ - 8.5 if False else EZ0 - 4, PZ + 5.5]
skip = LAMPS + FLAGS
z_ = ZA + 1.2
while z_ < ZB - 1:
    if min(abs(z_ - s) for s in skip) > .8:
        O(XE - .45, z_).cyl(XE - .45, z_, .1, .1, PY, PY + .85, 6, 'metal', '#2c3036'); O(XE - .45, z_).cyl(XE - .45, z_, .11, .11, PY + .62, PY + .7, 6, 'paint', '#e9eef4', cap=False)
    z_ += 1.7
for lz in LAMPS:
    l = O(XE - .6, lz); lx_ = XE - .6
    l.cyl(lx_, lz, .16, .16, PY, PY + .5, 6, 'metal', '#2f3a48'); l.cyl(lx_, lz, .08, .06, PY + .5, PY + 5.6, 6, 'metal', '#2f3a48')
    l.beam((lx_, PY + 5.5, lz), (lx_ - 1.1, PY + 5.75, lz), .07, 'metal', '#2f3a48')
    l.box(lx_ - 1.45, lx_ - .85, PY + 5.5, PY + 5.75, lz - .2, lz + .2, 'metal', '#2f3a48'); l.box(lx_ - 1.4, lx_ - .9, PY + 5.42, PY + 5.5, lz - .15, lz + .15, 'lampglass', '#fff3d6', ao=False)
for fz in FLAGS:
    f = O(XE - .7, fz); fx = XE - .7
    f.cyl(fx, fz, .2, .2, PY, PY + .25, 6, 'stone', '#bdb6a8'); f.cyl(fx, fz, .06, .045, PY + .25, PY + 9, 6, 'metal', '#eef1f4'); f.sphere(fx, PY + 9.05, fz, .08, 'gold', '#d9b860', 6, 3)
    for sd in (1, -1):                # two-sided flag, slight wave, hanging toward the stadium
        pts = [(fx, PY + 8.8, fz), (fx - 1.1, PY + 8.8, fz + .18), (fx - 1.1, PY + 7.4, fz + .18), (fx, PY + 7.4, fz)]
        pts2 = [(fx - 1.1, PY + 8.8, fz + .18), (fx - 2.2, PY + 8.7, fz), (fx - 2.2, PY + 7.3, fz), (fx - 1.1, PY + 7.4, fz + .18)]
        for q in (pts, pts2): f.quad(*(q if sd > 0 else q[::-1]), 'paint', BLUE)
    f.quad((fx - .9, PY + 8.35, fz + .2), (fx - 1.4, PY + 8.35, fz + .2), (fx - 1.4, PY + 7.85, fz + .2), (fx - .9, PY + 7.85, fz + .2), 'paint', '#f2f2f2', ao=False)
def bench(bx, bz, along_z=True, face=-1):
    g = O(bx, bz); hl = .9
    if along_z:
        g.box(bx - .22, bx + .22, PY + .42, PY + .48, bz - hl, bz + hl, 'wood', '#9b7046')
        bk = bx - face * .24; g.box(min(bk, bk - face * .06), max(bk, bk - face * .06), PY + .55, PY + .9, bz - hl, bz + hl, 'wood', '#9b7046')
        for s in (-1, 1): g.box(bx - .24, bx + .24, PY, PY + .42, bz + s * (hl - .1) - .04, bz + s * (hl - .1) + .04, 'metal', '#2c3036')
    else:
        g.box(bx - hl, bx + hl, PY + .42, PY + .48, bz - .22, bz + .22, 'wood', '#9b7046')
        bk = bz - face * .24; g.box(bx - hl, bx + hl, PY + .55, PY + .9, min(bk, bk - face * .06), max(bk, bk - face * .06), 'wood', '#9b7046')
        for s in (-1, 1): g.box(bx + s * (hl - .1) - .04, bx + s * (hl - .1) + .04, PY, PY + .42, bz - .24, bz + .24, 'metal', '#2c3036')
for bz_ in (cz - 20, cz + 20, cz + 28): bench(XE - 2.2, bz_, True, -1)   # facing the stadium
bench(PX, PZ + PR + .9, False, -1)                                         # on the plaza, facing the statue
# ---- club shop kiosk at the north end of the forecourt: blue box, white fascia, lit shop window toward the street
KX0, KX1, KZ0, KZ1 = FX + 5, FX + 10, ZA + 9, ZA + 16
k_ = O((KX0 + KX1) / 2, (KZ0 + KZ1) / 2); g_ = Gl((KX0 + KX1) / 2, (KZ0 + KZ1) / 2)
k_.box(KX0, KX1, PY, PY + 3.2, KZ0, KZ1, 'paint', BLUE, sides=(0, 1, 1, 1), top=False)
k_.box(KX1 - .15, KX1, PY, PY + .5, KZ0, KZ1, 'paint', BLUE, top=False)
for zz in (KZ0, KZ1 - .3): k_.box(KX1 - .3, KX1, PY + .5, PY + 2.5, zz, zz + .3, 'paint', BLUE, top=False)
glass_face(g_, [(KX1 - .1, PY + .5, KZ1 - .3), (KX1 - .1, PY + .5, KZ0 + .3), (KX1 - .1, PY + 2.5, KZ0 + .3), (KX1 - .1, PY + 2.5, KZ1 - .3)], LR, 1.0)
k_.box(KX0 - .3, KX1 + .5, PY + 2.5, PY + 3.25, KZ0 - .3, KZ1 + .3, 'paint', '#f2f4f6')            # fascia
k_.box(KX1 + .5, KX1 + .52, PY + 2.62, PY + 3.13, KZ0 + .6, KZ1 - .6, 'paint', BLUE, sides=(1, 0, 0, 0), top=False)
k_.box(KX0 - .4, KX1 + .7, PY + 3.25, PY + 3.4, KZ0 - .4, KZ1 + .4, 'metal', '#dfe3e7')            # roof slab
for j in range(3):                                                                                # white shirt shapes on the sign
    zc = KZ0 + 1.6 + j * 1.9; xs = KX1 + .53
    k_.quad((xs, PY + 2.7, zc + .2), (xs, PY + 2.7, zc - .2), (xs, PY + 3.0, zc - .2), (xs, PY + 3.0, zc + .2), 'paint', '#ffffff', ao=False)
    k_.quad((xs, PY + 2.88, zc + .38), (xs, PY + 2.88, zc - .38), (xs, PY + 3.05, zc - .38), (xs, PY + 3.05, zc + .38), 'paint', '#ffffff', ao=False)
