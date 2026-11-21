# Landmarks, exec'd inside city.py (shares O(), Gl(), Acc, glass_face, random)
LR = random.Random(99)
SAND, SAND_D, GOLD, SLATE_D = '#f4ecda', '#d9c8a4', '#ffffff', '#3d4846'
def win_strip(gacc, pts, lit=.4): glass_face(gacc, pts, LR, lit)
def facade_windows(gacc, axis, fixed, u0, u1, y0, y1, n, wfrac, sgn, lit=.4):
    """glass panes on a wall plane. axis 'z' -> wall at z=fixed spanning x; 'x' -> wall at x=fixed spanning z. sgn = outward normal sign"""
    step = (u1 - u0) / n
    for i in range(n):
        c = u0 + step * (i + .5); hw = step * wfrac / 2; o = .04 * sgn
        if axis == 'z': pts = [(c - hw, y0, fixed + o), (c + hw, y0, fixed + o), (c + hw, y1, fixed + o), (c - hw, y1, fixed + o)]
        else: pts = [(fixed + o, y0, c + hw), (fixed + o, y0, c - hw), (fixed + o, y1, c - hw), (fixed + o, y1, c + hw)]
        if sgn < 0: pts = [pts[1], pts[0], pts[3], pts[2]]
        win_strip(gacc, pts, lit)
def pyramid(acc, cx, cz, half, y0, y1, layer, tint, top=0.0):
    c = [(cx - half, cz - half), (cx + half, cz - half), (cx + half, cz + half), (cx - half, cz + half)]
    t = [(cx - top, cz - top), (cx + top, cz - top), (cx + top, cz + top), (cx - top, cz + top)]
    for i in range(4):
        a, b = c[i], c[(i + 1) % 4]; ta, tb = t[i], t[(i + 1) % 4]
        if top > 0: acc.quad((b[0], y0, b[1]), (a[0], y0, a[1]), (ta[0], y1, ta[1]), (tb[0], y1, tb[1]), layer, tint)
        else: acc.face([(b[0], y0, b[1]), (a[0], y0, a[1]), (cx, y1, cz)], layer, tint)
def big_ben(x, z):
    acc, g = O(x, z), Gl(x, z)
    acc.cbox(x, 0, z, 8, 45, 8, 'sandstone', SAND)
    for ox, oz in ((-4, -4), (4, -4), (-4, 4), (4, 4)): acc.cbox(x + ox, 0, z + oz, 1.2, 46.5, 1.2, 'sandstone', SAND_D)
    for y in range(8, 44, 6): acc.cbox(x, y, z, 8.35, .4, 8.35, 'sandstone', SAND_D, ao=False)
    for s in (-1.8, 1.8):
        for y in range(9, 44, 6):
            for fx, fz, ax in ((0, 4, 'z'), (0, -4, 'z'), (4, 0, 'x'), (-4, 0, 'x')):
                if ax == 'z': facade_windows(g, 'z', z + fz, x + s - .45, x + s + .45, y + .6, y + 4.6, 1, .8, 1 if fz > 0 else -1, .5)
                else: facade_windows(g, 'x', x + fx, z + s - .45, z + s + .45, y + .6, y + 4.6, 1, .8, 1 if fx > 0 else -1, .5)
    acc.cbox(x, 45, z, 9, 10, 9, 'sandstone', SAND)
    cy = 50.2; r = 3.6; o = 4.56
    for nx, nz in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        if nz: pts = [(x - r, cy - r, z + nz * o), (x + r, cy - r, z + nz * o), (x + r, cy + r, z + nz * o), (x - r, cy + r, z + nz * o)]
        else: pts = [(x + nx * o, cy - r, z + r), (x + nx * o, cy - r, z - r), (x + nx * o, cy + r, z - r), (x + nx * o, cy + r, z + r)]
        if nz < 0 or nx < 0: pts = [pts[1], pts[0], pts[3], pts[2]]
        acc.quad(*pts, 'clock', uvs=[(0, 0), (1, 0), (1, 1), (0, 1)], ao=False)
    acc.cbox(x, 55, z, 9.5, .9, 9.5, 'gold', GOLD, ao=False)
    acc.cbox(x, 55.9, z, 7.4, 5.2, 7.4, 'sandstone', SAND_D)
    for k in (-2.2, 0, 2.2):
        for fx, fz in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            if fz: acc.cbox(x + k, 56.6, z + fz * 3.72, 1.1, 3.6, .12, 'metal', '#24292e')
            else: acc.cbox(x + fx * 3.72, 56.6, z + k, .12, 3.6, 1.1, 'metal', '#24292e')
    for ox, oz in ((-3.6, -3.6), (3.6, -3.6), (-3.6, 3.6), (3.6, 3.6)):
        acc.cbox(x + ox, 55.9, z + oz, 1, 7, 1, 'sandstone', SAND); acc.cone(x + ox, z + oz, .75, 62.9, 66.5, 4, 'gold', GOLD, ry=math.pi / 4)
    pyramid(acc, x, z, 3.9, 61.1, 73.5, 'slate', SLATE_D, top=.35)
    for k in range(4):
        a = k * math.pi / 2; acc.cone(x + math.cos(a) * 2.6, z + math.sin(a) * 2.6, .4, 63.5, 66.2, 4, 'gold', GOLD)
    acc.cyl(x, z, .35, .05, 73.5, 79, 6, 'gold', GOLD)
def parliament():
    x0, x1, z0, z1 = -139, -99, -62, -39; acc, g = O(-119, -50), Gl(-119, -50)
    acc.box(x0, x1, 0, 17, z0, z1, 'sandstone', SAND)
    pyramid(acc, -119, -50.5, 0, 0, 0, 'slate', SLATE_D) if False else None
    acc.box(x0 + 1, x1 - 1, 17, 20.5, z0 + 2.5, z1 - 2.5, 'slate', '#55605d')
    for x in [x0 + .6 + 3.2 * k for k in range(int((x1 - x0) / 3.2) + 1)]:
        for zz in (z1 + .3, z0 - .3):
            acc.cbox(x, 0, zz, .8, 20.5, .8, 'sandstone', SAND_D); acc.cone(x, zz, .55, 20.5, 22.4, 4, 'sandstone', SAND_D, ry=math.pi / 4)
    for y0, y1 in ((2.4, 6.9), (8.4, 12.6), (13.4, 16.0)):
        facade_windows(g, 'z', z1, x0 + .6, x1 - .6, y0, y1, 12, .5, 1, .45); facade_windows(g, 'z', z0, x0 + .6, x1 - .6, y0, y1, 12, .5, -1, .45)
    for y in (7.5, 12.9): acc.box(x0, x1, y, y + .3, z1, z1 + .25, 'sandstone', SAND_D, ao=False); acc.box(x0, x1, y, y + .3, z0 - .25, z0, 'sandstone', SAND_D, ao=False)
    acc.cyl(-119, -50.5, 3.4, 3.4, 17, 30, 8, 'sandstone', SAND); acc.cone(-119, -50.5, 3.6, 30, 42, 8, 'slate', SLATE_D)
    vx, vz = -103, -50.5
    acc.cbox(vx, 0, vz, 12, 49, 12, 'sandstone', SAND)
    for ox, oz in ((-6, -6), (6, -6), (-6, 6), (6, 6)): acc.cbox(vx + ox, 0, vz + oz, 1.5, 54, 1.5, 'sandstone', SAND_D); acc.cone(vx + ox, vz + oz, 1, 54, 57.5, 4, 'sandstone', SAND_D, ry=math.pi / 4)
    for s in (-2.6, 2.6):
        for fz in (6, -6): facade_windows(g, 'z', vz + fz, vx + s - .7, vx + s + .7, 8, 44, 1, 1, 1 if fz > 0 else -1, .4)
    acc.cbox(vx, 49, vz, 10.4, 1.6, 10.4, 'sandstone', SAND_D); acc.cyl(vx, vz, .15, .15, 50.6, 58.6, 6, 'paint', '#eeeeee')
    acc.box(vx + .15, vx + 3.2, 56.6, 58.4, vz - .05, vz + .05, 'paint', '#c8102e', ao=False)
    for sx, sz in ((-140, -95), (-125, -88), (-110, -96)):
        acc.cbox(sx, KERB, sz, 2, 2.4, 2, 'stone', '#cfc8b8'); acc.cbox(sx, 2.5, sz, .8, 2.2, .8, 'metal', '#3d4a45'); acc.sphere(sx, 5.05, sz, .38, 'metal', '#3d4a45', 8, 5)
def palace():
    x0, x1, z0, z1, mz = -282, -252, -170, -80, -125; S, T = '#ebe5d6', '#d8d0bd'
    acc, g = O(-267, -125), Gl(-267, -125)
    acc.box(x0, x1, 0, 21, z0, z1, 'stone', S)
    acc.box(x0 - .3, x1 + .3, 21, 22.1, z0 - .3, z1 + .3, 'stone', T, ao=False); acc.box(x0 + .5, x1 - .5, 22.1, 23.6, z0 + .5, z1 - .5, 'stone', S)
    for zz in [z0 + 1 + 1.2 * k for k in range(int((z1 - z0 - 2) / 1.2) + 1)]: acc.cbox(x1 + .1, 22.1, zz, .3, 1.5, .5, 'stone', T)
    acc.cbox(x1 + 1.2, 0, mz, 2.4, 21, 30, 'stone', S)
    for zz in [mz - 13 + 3.7 * k for k in range(8)]:
        acc.cyl(x1 + 3.1, zz, .62, .55, 1.8, 16.8, 12, 'stone', '#f3eee2'); acc.cbox(x1 + 3.1, 1.3, zz, 1.5, .5, 1.5, 'stone', T); acc.cbox(x1 + 3.1, 16.8, zz, 1.5, .5, 1.5, 'stone', T)
    acc.box(x1 + 2.3, x1 + 3.9, 17.3, 18.7, mz - 14, mz + 14, 'stone', T)
    acc.face([(x1 + 3.9, 18.7, mz - 14), (x1 + 3.9, 18.7, mz + 14), (x1 + 3.9, 22.8, mz)], 'stone', S)
    acc.quad((x1 + 3.9, 18.7, mz + 14), (x1 + .4, 18.7, mz + 14), (x1 + .4, 22.8, mz), (x1 + 3.9, 22.8, mz), 'slate', '#7d817f')
    acc.quad((x1 + .4, 18.7, mz - 14), (x1 + 3.9, 18.7, mz - 14), (x1 + 3.9, 22.8, mz), (x1 + .4, 22.8, mz), 'slate', '#7d817f')
    for y0 in (3.6, 9.2, 14.8):
        for zz in [z0 + 3 + 4 * k for k in range(23)]:
            if abs(zz - mz) < 16 or zz > z1 - 2: continue
            facade_windows(g, 'x', x1, zz - .85, zz + .85, y0, y0 + 2.6, 1, 1, 1, .35); acc.cbox(x1 + .2, y0 + 2.7, zz, .35, .3, 2.1, 'stone', T)
    acc.cbox(x1 + 3.4, 9, mz, 2, .4, 9, 'stone', T)
    acc.cyl(-267, mz, .15, .15, 23.6, 32.6, 6, 'paint', '#eeeeee')
    acc.box(-266.9, -263.6, 30.4, 32.4, mz - .05, mz + .05, 'paint', '#c8102e', ao=False); acc.box(-266.9, -263.6, 31.15, 31.65, mz - .07, mz + .07, 'paint', '#f2f2f2', ao=False); acc.box(-265.5, -265.0, 30.4, 32.4, mz - .08, mz + .08, 'paint', '#1d3f8f', ao=False)
    fx = -236
    for zz in [-176 + 1.2 * k for k in range(86)]:
        if -130 < zz < -120: continue
        acc.cbox(fx, KERB, zz, .1, 2.5, .1, 'metal', '#1c1f22', top=False); acc.cone(fx, zz, .08, 2.6, 2.95, 4, 'gold', GOLD)
    for zz in range(-176, -73, 8):
        if -133 < zz < -118: continue
        acc.cbox(fx, KERB, zz, .45, 3, .45, 'metal', '#1c1f22'); acc.sphere(fx, 3.35, zz, .28, 'gold', GOLD, 8, 5)
    for zc in (-153, -97): acc.box(fx - .05, fx + .05, 2.2, 2.3, zc - 23, zc + 23, 'metal', '#1c1f22'); acc.box(fx - .05, fx + .05, .45, .55, zc - 23, zc + 23, 'metal', '#1c1f22')
    for zz in (-130.5, -119.5): acc.cbox(fx, 0, zz, .7, 4.4, .7, 'gold', GOLD)
    for zz in (-134, -116):
        acc.cbox(fx + 2, KERB, zz, 1.6, 2.8, 1.6, 'paint', '#2b2f33'); pyramid(acc, fx + 2, zz, .9, 2.9, 3.7, 'paint', '#c8102e')
    vx = -212
    acc.cyl(vx, mz, 8.4, 8, KERB, 1.3, 32, 'stone', '#ece7db'); acc.cyl(vx, mz, 5.2, 4.6, 1.3, 4.6, 24, 'stone', '#ece7db')
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4; px, pz = vx + math.cos(a) * 4.8, mz + math.sin(a) * 4.8
        acc.cbox(px, 1.3, pz, 1.3, 2.2, 1.3, 'stone', '#ece7db'); acc.sphere(px, 4.0, pz, .6, 'metal', '#5b6560', 8, 5, sy=1.4)
    acc.cyl(vx, mz, 2, 1.6, 4.6, 13.6, 16, 'stone', '#ece7db'); acc.sphere(vx, 14.4, mz, 1.3, 'gold', GOLD, 10, 6); acc.cbox(vx, 14.6, mz, .5, 2.4, .5, 'gold', GOLD); acc.cbox(vx, 15.85, mz, 3, .3, .6, 'gold', GOLD)
def london_eye():
    global EYE
    hx, hy, hz, R = -120, 29, 37, 25; E = Acc()
    seg = 64
    for k in range(seg):
        a0, a1 = k / seg * math.tau, (k + 1) / seg * math.tau
        E.beam((math.cos(a0) * R, math.sin(a0) * R, 0), (math.cos(a1) * R, math.sin(a1) * R, 0), .9, 'paint', '#f2f4f5')
        E.beam((math.cos(a0) * (R - 2.4), math.sin(a0) * (R - 2.4), 0), (math.cos(a1) * (R - 2.4), math.sin(a1) * (R - 2.4), 0), .35, 'steel', '#dfe3e6')
    for k in range(32):
        a = k / 32 * math.tau
        E.beam((0, 0, -1.2), (math.cos(a) * R, math.sin(a) * R, 0), .1, 'steel', '#e8ecef'); E.beam((0, 0, 1.2), (math.cos(a) * R, math.sin(a) * R, 0), .1, 'steel', '#e8ecef')
        E.beam((math.cos(a) * R, math.sin(a) * R, 0), (math.cos(a + .2) * (R - 2.4), math.sin(a + .2) * (R - 2.4), 0), .14, 'steel', '#e8ecef')
        pa = a + math.pi / 32
        E.sphere(math.cos(pa) * (R + 1.2), math.sin(pa) * (R + 1.2), 1.3, 1.05, 'lampglass', '#cfe3ef', 10, 6, sy=.75)
    E.cyl(0, 0, 1.6, 1.6, -1.6, 1.6, 16, 'steel', '#c9ced2')
    EYE = E
    acc = O(hx, hz + 8)
    for s in (-1, 1): acc.beam((hx + s * 9, KERB, hz + 15), (hx, hy, hz + 1.6), 1.0, 'paint', '#e8ecef')
    acc.beam((hx, KERB, hz + 15), (hx, hy, hz + 1.6), .7, 'paint', '#e8ecef')
def tower_bridge():
    x, S = 160, '#d8c7a0'; B, Wt = '#4f8bc9', '#e8eef4'
    for tz in (-15, 15):
        acc, g = O(x, tz), Gl(x, tz)
        acc.cbox(x, -3.2, tz, 30, 3.2, 14, 'stone', '#9c8f78')
        for sx in (-1, 1):
            lx = x + sx * 11
            acc.cbox(lx, 0, tz, 6, 34, 11, 'stone', S)
            for y in (6, 18, 30): acc.cbox(lx, y, tz, 6.3, .45, 11.3, 'stone', '#c6b58a', ao=False)
            for ox in (-2.4, 2.4):
                for oz in (-4.6, 4.6):
                    acc.cbox(lx + ox, 34, tz + oz, 1.5, 4, 1.5, 'stone', S); pyramid(acc, lx + ox, tz + oz, .8, 38, 42, 'slate', SLATE_D); acc.sphere(lx + ox, 42.2, tz + oz, .2, 'gold', GOLD, 6, 4)
            pyramid(acc, lx, tz, 2.9, 34, 41.5, 'slate', SLATE_D); acc.cyl(lx, tz, .12, .05, 41.5, 44, 6, 'gold', GOLD)
            for y in (8, 16, 24):
                facade_windows(g, 'z', tz + 5.5, lx - .8, lx + .8, y, y + 3.2, 1, 1, 1, .3); facade_windows(g, 'z', tz - 5.5, lx - .8, lx + .8, y, y + 3.2, 1, 1, -1, .3)
        acc.cbox(x, 17, tz, 16, 17, 11, 'stone', S); acc.cbox(x, 15.8, tz, 16.2, 1.2, 11.2, 'stone', '#bba77f')
    acc = O(x, 0)
    for sx in (-1, 1):
        acc.cbox(x + sx * 5, 27.5, 0, 3, 3.6, 19, 'metal', B); acc.cbox(x + sx * 5, 31.1, 0, 3.3, .4, 19.2, 'paint', Wt); acc.cbox(x + sx * 5, 27.2, 0, 3.3, .3, 19.2, 'paint', Wt)
        for zz in range(-8, 8, 2): acc.beam((x + sx * 6.6, 27.6, zz), (x + sx * 6.6, 31, zz + 2), .14, 'paint', Wt)
    for sx in (-1, 1):
        for sz in (-1, 1):
            acc.beam((x + sx * 9.6, 26, sz * 20.5), (x + sx * 9.6, 1, sz * 36), .7, 'metal', B); acc.beam((x + sx * 9.6, 26, sz * 9.5), (x + sx * 9.6, 9, 0), .6, 'metal', B)
            for k in range(1, 6):
                t = k / 6; acc.beam((x + sx * 9.6, 26 - 25 * t, sz * (20.5 + 15.5 * t)), (x + sx * 9.2, 0, sz * (20.5 + 15.5 * t)), .08, 'metal', B)
def tower_of_london():
    cx, cz, S, Wl = 200, -85, '#e6dfcf', '#cdc1a3'; acc, g = O(cx, cz), Gl(cx, cz)
    def seg(x0, x1, z0, z1):
        acc.box(x0, x1, 0, 6, z0, z1, 'stone', Wl); lx = x1 - x0 > z1 - z0; L_ = (x1 - x0) if lx else (z1 - z0)
        for k in range(int(L_ / 1.6)):
            t = k * 1.6 + .4
            if lx: acc.box(x0 + t, x0 + t + .8, 6, 6.8, z0, z1, 'stone', Wl)
            else: acc.box(x0, x1, 6, 6.8, z0 + t, z0 + t + .8, 'stone', Wl)
    for c in ((173, 227, -112, -110), (173, 175, -112, -58), (225, 227, -112, -58), (173, 196, -60, -58), (204, 227, -60, -58)): seg(*c)
    for x, z in ((174, -111), (226, -111), (174, -59), (226, -59)): acc.cyl(x, z, 3, 3, 0, 9, 14, 'stone', Wl)
    acc.box(cx - 11, cx + 11, 0, 19, cz - 9, cz + 9, 'stone', S)
    for x in [cx - 10 + 1.6 * k for k in range(13)]:
        acc.box(x - .4, x + .4, 19, 19.9, cz - 9, cz - 8.4, 'stone', S); acc.box(x - .4, x + .4, 19, 19.9, cz + 8.4, cz + 9, 'stone', S)
    for ox, oz in ((-11, -9), (11, -9), (-11, 9), (11, 9)):
        acc.cyl(cx + ox, cz + oz, 2.4, 2.4, 0, 25, 14, 'stone', S); acc.sphere(cx + ox, 25, cz + oz, 2.5, 'slate', '#7f8c90', 12, 5, half=True); acc.cyl(cx + ox, cz + oz, .08, .08, 27.4, 30, 4, 'gold', GOLD)
    for y in (4, 11):
        facade_windows(g, 'z', cz + 9, cx - 10, cx + 10, y, y + 2.4, 7, .35, 1, .3); facade_windows(g, 'z', cz - 9, cx - 10, cx + 10, y, y + 2.4, 7, .35, -1, .3)
def glass_frustum(cx, cz, b0, b1, y0, y1, rot=0.0, lit=.5, tint=None):
    g = Gl(cx, cz); n = 4
    for i in range(n):
        a0, a1 = rot + i / n * math.tau + math.pi / 4, rot + (i + 1) / n * math.tau + math.pi / 4
        p = lambda a, r, y: (cx + math.cos(a) * r, y, cz + math.sin(a) * r)
        pts = [p(a1, b0, y0), p(a0, b0, y0), p(a0, b1, y1), p(a1, b1, y1)]
        glass_face(g, pts, LR, lit)
def shard():
    glass_frustum(120, 85, 28, 1.4, 0, 150, 0, .55); glass_frustum(121.5, 83.5, 24, .5, 0, 166, .1, .55)
    acc = O(120, 85)
    for k in range(8): acc.beam((120 + LR.uniform(-1, 1), 150, 85 + LR.uniform(-1, 1)), (120 + LR.uniform(-2.5, 2.5), 175, 85 + LR.uniform(-2.5, 2.5)), .25, 'steel', '#d5e1ea')
def gherkin():
    pts = [(0, 0), (10, 0), (13, 14), (14.5, 34), (13, 56), (9, 74), (3.5, 85), (0, 88)]; cx, cz = 120, -165; g = Gl(cx, cz); acc = O(cx, cz); seg = 24
    for j in range(len(pts) - 1):
        (r0, y0), (r1, y1) = pts[j], pts[j + 1]
        for i in range(seg):
            a0, a1 = i / seg * math.tau, (i + 1) / seg * math.tau
            q = [(cx + math.sin(a0) * r0, y0, cz + math.cos(a0) * r0), (cx + math.sin(a1) * r0, y0, cz + math.cos(a1) * r0), (cx + math.sin(a1) * r1, y1, cz + math.cos(a1) * r1), (cx + math.sin(a0) * r1, y1, cz + math.cos(a0) * r1)]
            if r1 < 1e-3: q = q[:3]
            glass_face(g, q, LR, .45)
    for k in range(16):
        a = k / 16 * math.tau
        for j in range(1, len(pts) - 2):
            p0, p1 = pts[j], pts[j + 1]; a0, a1 = a + j * .26, a + (j + 1) * .26
            acc.beam((cx + math.sin(a0) * p0[0] * 1.01, p0[1], cz + math.cos(a0) * p0[0] * 1.01), (cx + math.sin(a1) * p1[0] * 1.01, p1[1], cz + math.cos(a1) * p1[0] * 1.01), .3, 'metal', '#23383b')
def walkie():
    glass_frustum(40, -245, 15, 23, 0, 86, 0, .5); O(40, -245).quad((40 - 16, 86, -245 + 16), (40 + 16, 86, -245 + 16), (40 + 16, 86, -245 - 16), (40 - 16, 86, -245 - 16), 'concrete', '#c8ced2')
def cheesegrater():
    acc, g = O(200, -165), Gl(200, -165)
    for i in range(9):
        d = 36 - i * 3.6; y0, y1 = i * 13, (i + 1) * 13; z0, z1 = -183, -183 + d
        for pts in ([(186, y0, z1), (214, y0, z1), (214, y1, z1), (186, y1, z1)], [(214, y0, z0), (186, y0, z0), (186, y1, z0), (214, y1, z0)], [(214, y0, z1), (214, y0, z0), (214, y1, z0), (214, y1, z1)], [(186, y0, z0), (186, y0, z1), (186, y1, z1), (186, y1, z0)]):
            glass_face(g, pts, LR, .5)
        acc.box(185.8, 214.2, y1 - .4, y1, z0 - .2, z1 + .2, 'paint', '#f0c419')
        for xx in (186, 200, 214): acc.box(xx - .25, xx + .25, y0, y1, z1, z1 + .4, 'paint', '#f0c419', top=False)
EYE = None
big_ben(-144, -42); parliament(); palace(); london_eye(); tower_bridge(); tower_of_london(); shard(); gherkin(); walkie(); cheesegrater()
