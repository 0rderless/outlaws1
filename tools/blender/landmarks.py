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
def lancet(gacc, axis, fixed, sgn, u, y0, y1, w, lit=.45):
    """pointed Gothic window pane on a wall plane (axis 'z': wall at z=fixed spanning x; 'x': wall at x=fixed spanning z)"""
    ys = y1 - w * .7; o = .05 * sgn; hw = w / 2
    if axis == 'z': pts = [(u - hw, y0, fixed + o), (u + hw, y0, fixed + o), (u + hw, ys, fixed + o), (u, y1, fixed + o), (u - hw, ys, fixed + o)]
    else: pts = [(fixed + o, y0, u + hw), (fixed + o, y0, u - hw), (fixed + o, ys, u - hw), (fixed + o, y1, u), (fixed + o, ys, u + hw)]
    if sgn < 0: pts = pts[::-1]
    glass_face(gacc, pts, LR, lit)
def faces4(cx, cz, h):
    """(axis, fixed, sgn, centre-u) for the four walls of a square of half-size h"""
    return [('z', cz + h, 1, cx), ('z', cz - h, -1, cx), ('x', cx + h, 1, cz), ('x', cx - h, -1, cz)]
def wall_box(acc, axis, fixed, sgn, u0, u1, y0, y1, depth, layer, tint, ao=True):
    """a thin box standing proud of a wall (ribs, frames)"""
    if axis == 'z': acc.box(u0, u1, y0, y1, min(fixed, fixed + sgn * depth), max(fixed, fixed + sgn * depth), layer, tint, ao=ao)
    else: acc.box(min(fixed, fixed + sgn * depth), max(fixed, fixed + sgn * depth), y0, y1, u0, u1, layer, tint, ao=ao)
def big_ben(x, z):
    """Elizabeth Tower: honey limestone shaft with Gothic panelling, gilded clock stage, belfry, iron spire with lantern"""
    acc, g = O(x, z), Gl(x, z)
    S1, S2, IRON = '#e7d3a0', '#c9ad72', '#2c3536'
    acc.cbox(x, 0, z, 10.6, 3, 10.6, 'sandstone', S2)
    acc.cbox(x, 3, z, 9, 48.4, 9, 'sandstone', S1)
    for ox, oz in ((-4.5, -4.5), (4.5, -4.5), (-4.5, 4.5), (4.5, 4.5)): acc.cyl(x + ox, z + oz, .8, .8, 0, 52.2, 8, 'sandstone', S2, ry=math.pi / 8)
    for ax, fx, sg, u in faces4(x, z, 4.5):
        for k in (-1.5, 1.5): wall_box(acc, ax, fx, sg, u + k - .18, u + k + .18, 3, 51.4, .3, 'sandstone', S2)
        for y0 in (5.5, 13.5, 21.5, 29.5, 37.5):
            for b in (-3, 0, 3): lancet(g, ax, fx, sg, u + b, y0, y0 + 5.6, 1.05, .35)
        for b in (-3, 0, 3): lancet(g, ax, fx, sg, u + b, 44.5, 49.6, 1.2, .5)
    for y in (3, 11, 19, 27, 35, 43, 51): acc.cbox(x, y, z, 9.6, .5, 9.6, 'sandstone', S2, ao=False)
    # clock stage with a gilded frame round each dial
    acc.cbox(x, 51.4, z, 10.8, 10, 10.8, 'sandstone', S1)
    cy, r, o = 56.4, 3.75, 5.42
    for ax, fx, sg, u in faces4(x, z, 5.4):
        wall_box(acc, ax, fx, sg, u - 4.35, u + 4.35, cy + 3.9, cy + 4.5, .16, 'gold', GOLD, ao=False); wall_box(acc, ax, fx, sg, u - 4.35, u + 4.35, cy - 4.5, cy - 3.9, .16, 'gold', GOLD, ao=False)
        wall_box(acc, ax, fx, sg, u - 4.35, u - 3.9, cy - 4.5, cy + 4.5, .16, 'gold', GOLD, ao=False); wall_box(acc, ax, fx, sg, u + 3.9, u + 4.35, cy - 4.5, cy + 4.5, .16, 'gold', GOLD, ao=False)
        for cu, cv in ((-3.4, 3.4), (3.4, 3.4), (-3.4, -3.4), (3.4, -3.4)): wall_box(acc, ax, fx, sg, u + cu - .45, u + cu + .45, cy + cv - .45, cy + cv + .45, .1, 'gold', GOLD, ao=False)
        f = fx + sg * .19
        if ax == 'z': pts = [(u - r, cy - r, f), (u + r, cy - r, f), (u + r, cy + r, f), (u - r, cy + r, f)]
        else: pts = [(f, cy - r, u + r), (f, cy - r, u - r), (f, cy + r, u - r), (f, cy + r, u + r)]
        if sg < 0: pts = [pts[1], pts[0], pts[3], pts[2]]
        acc.quad(*pts, 'clock', uvs=[(0, 0), (1, 0), (1, 1), (0, 1)] if sg > 0 else [(1, 0), (0, 0), (0, 1), (1, 1)], ao=False)
        wall_box(acc, ax, fx, sg, u - 4.8, u + 4.8, 61, 61.4, .25, 'sandstone', S2, ao=False)
    acc.cbox(x, 61.4, z, 11.4, .9, 11.4, 'gold', GOLD, ao=False)                       # gallery
    # belfry: three tall pointed openings a side, dark inside, gilt tracery
    acc.cbox(x, 62.3, z, 9.4, 6.6, 9.4, 'sandstone', S1)
    for ax, fx, sg, u in faces4(x, z, 4.7):
        for b in (-2.6, 0, 2.6):
            ys = 67.3; w = 1.7; o = .03 * sg
            if ax == 'z': pts = [(u + b - w / 2, 63.2, fx + o), (u + b + w / 2, 63.2, fx + o), (u + b + w / 2, ys, fx + o), (u + b, 68.4, fx + o), (u + b - w / 2, ys, fx + o)]
            else: pts = [(fx + o, 63.2, u + b + w / 2), (fx + o, 63.2, u + b - w / 2), (fx + o, ys, u + b - w / 2), (fx + o, 68.4, u + b), (fx + o, ys, u + b + w / 2)]
            if sg < 0: pts = pts[::-1]
            acc.face(pts, 'metal', '#15191b', ao=False)
            wall_box(acc, ax, fx, sg, u + b - .07, u + b + .07, 63.2, 68.3, .08, 'gold', GOLD, ao=False)
    for ox, oz in ((-4.7, -4.7), (4.7, -4.7), (-4.7, 4.7), (4.7, 4.7)):
        acc.cyl(x + ox, z + oz, .75, .75, 61.4, 70.5, 8, 'sandstone', S2, ry=math.pi / 8); acc.cone(x + ox, z + oz, .8, 70.5, 75, 8, 'gold', GOLD)
    for ax, fx, sg, u in faces4(x, z, 4.7):
        for b in (-1.4, 1.4): pass
    # iron spire with gilt ribs, four dormers, the Ayrton light lantern and a gilt finial
    pyramid(acc, x, z, 4.8, 69, 81, 'slate', IRON, top=1.7)
    for ox, oz in ((-1, -1), (1, -1), (-1, 1), (1, 1)): acc.beam((x + ox * 4.75, 69, z + oz * 4.75), (x + ox * 1.75, 81, z + oz * 1.75), .22, 'gold', GOLD)
    for ax, fx, sg, u in faces4(x, z, 3.6):
        if ax == 'z': acc.cbox(u, 72, fx + sg * .4, 1.6, 2.6, 1.4, 'slate', IRON)
        else: acc.cbox(fx + sg * .4, 72, u, 1.4, 2.6, 1.6, 'slate', IRON)
        if ax == 'z': acc.cone(u, fx + sg * .4, .95, 74.6, 76.4, 4, 'gold', GOLD, ry=math.pi / 4)
        else: acc.cone(fx + sg * .4, u, .95, 74.6, 76.4, 4, 'gold', GOLD, ry=math.pi / 4)
    acc.cbox(x, 81, z, 3.6, 3.2, 3.6, 'gold', GOLD)
    for ax, fx, sg, u in faces4(x, z, 1.8): lancet(g, ax, fx, sg, u, 81.5, 83.8, 1.6, 1.0)
    pyramid(acc, x, z, 1.9, 84.2, 89, 'slate', IRON, top=.25)
    acc.cyl(x, z, .3, .12, 89, 92.5, 8, 'gold', GOLD); acc.sphere(x, 92.7, z, .35, 'gold', GOLD, 8, 5); acc.cbox(x, 93, z, .12, 1.4, .12, 'gold', GOLD); acc.cbox(x, 93.8, z, .7, .12, .12, 'gold', GOLD)
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
    """Two Gothic towers on river piers (the road runs through pointed arches), corner turrets with spires,
    blue-and-white high-level walkways, and the blue suspension chains of the side spans down to shore towers."""
    X = 160; ST, GR, BL, WT = '#d6ceba', '#a99f8c', '#3f86cf', '#f2f5f7'; SL = '#3a4446'
    HW = 8.3; SPR, APX, TOP = 9.5, 14.5, 26.0       # arch: half span, springing, apex; main block top
    for TZ in (-16, 16):
        acc, g = O(X, TZ), Gl(X, TZ)
        acc.cbox(X, -3.6, TZ, 27, 3.6, 12.5, 'stone', GR)                                     # pier
        for sx in (-1, 1): acc.cyl(X + sx * 13.5, TZ, 6.25, 6.25, -3.6, 0, 12, 'stone', GR)   # cutwaters
        for sx in (-1, 1):                                                                     # the two side masses
            acc.box(X + sx * HW if sx > 0 else X - 12, X + 12 if sx > 0 else X - HW, 0, TOP, TZ - 5.5, TZ + 5.5, 'stone', ST)
        acc.box(X - HW, X + HW, APX, TOP, TZ - 5.5, TZ + 5.5, 'stone', ST, bottom=False, sides=(0, 0, 1, 1))
        n = 12; arc = lambda u: SPR + (APX - SPR) * (1 - abs(u)) ** .55
        for k in range(n):                                                                     # spandrels and the arch soffit
            u0, u1 = -1 + 2 * k / n, -1 + 2 * (k + 1) / n; x0, x1 = X + u0 * HW, X + u1 * HW; y0, y1 = arc(u0), arc(u1)
            for zf, sg in ((TZ + 5.5, 1), (TZ - 5.5, -1)):
                pts = [(x0, y0, zf), (x1, y1, zf), (x1, APX, zf), (x0, APX, zf)]
                acc.face(pts if sg > 0 else pts[::-1], 'stone', ST)
            acc.quad((x1, y1, TZ - 5.5), (x0, y0, TZ - 5.5), (x0, y0, TZ + 5.5), (x1, y1, TZ + 5.5), 'stone', '#bdb4a0')
        for zf, sg in ((TZ + 5.5, 1), (TZ - 5.5, -1)):                                         # stone voussoir band round the arch
            for k in range(n):
                u0, u1 = -1 + 2 * k / n, -1 + 2 * (k + 1) / n
                a, b = (X + u0 * HW, arc(u0)), (X + u1 * HW, arc(u1))
                acc.beam((a[0], a[1] + .35, zf + sg * .12), (b[0], b[1] + .35, zf + sg * .12), .7, 'sandstone', '#c4b89c')
        for y in (TOP, 9.5): acc.cbox(X, y, TZ, 24.6, .6, 11.6, 'sandstone', '#c4b89c', ao=False)
        acc.cbox(X, TOP + .6, TZ, 22.4, 6.6, 9.6, 'stone', ST)                                 # top storey
        acc.cbox(X, TOP + 7.2, TZ, 23, .5, 10.2, 'sandstone', '#c4b89c', ao=False)
        for ox in (-10.4, 10.4):                                                              # octagonal corner turrets with spires
            for oz in (-4.4, 4.4):
                acc.cyl(X + ox, TZ + oz, 1.8, 1.8, 0, 35.2, 8, 'stone', ST, ry=math.pi / 8)
                for y in (TOP, 31.5): acc.cyl(X + ox, TZ + oz, 1.95, 1.95, y, y + .45, 8, 'sandstone', '#c4b89c', ry=math.pi / 8)
                acc.cone(X + ox, TZ + oz, 1.9, 35.2, 41.8, 8, 'slate', SL, ry=math.pi / 8); acc.sphere(X + ox, 42.1, TZ + oz, .32, 'gold', GOLD, 6, 4)
        acc.cbox(X, TOP + 7.7, TZ, 12, 3.6, 6.6, 'stone', ST)                                  # lantern storey and the central spire
        pyramid(acc, X, TZ, 4.4, TOP + 11.3, TOP + 21, 'slate', SL, top=.3); acc.cyl(X, TZ, .22, .06, TOP + 21, TOP + 24, 6, 'gold', GOLD)
        for sx in (-1, 1): pyramid(acc, X + sx * 4.6, TZ, 1.4, TOP + 11.3, TOP + 15.5, 'slate', SL)
        for ax, fx, sg, u in (('x', X + 12, 1, TZ), ('x', X - 12, -1, TZ)):                     # lancet windows
            for y0 in (11, 17.5, 28): 
                for b in (-2.6, 0, 2.6): lancet(g, ax, fx, sg, u + b, y0, y0 + 4.3, 1.1, .3)
        for zf, sg in ((TZ + 5.5, 1), (TZ - 5.5, -1)):
            for sx in (-1, 1):
                for y0 in (11, 17.5): lancet(g, 'z', zf, sg, X + sx * 10.15, y0, y0 + 4.3, 1.1, .3)
            for b in (-3, 0, 3): lancet(g, 'z', zf, sg, X + b, 17, 23.6, 1.3, .3)
            for b in (-6, -2, 2, 6): lancet(g, 'z', zf - sg * 1.0, sg, X + b, 28, 32.2, 1.1, .3)
    # high-level walkways: lattice girders between the tower tops, one each side
    acc = O(X, 0)
    for sx in (-1, 1):
        wx = X + sx * 6.2; z0, z1 = -10.5, 10.5
        acc.box(wx - 1.7, wx + 1.7, TOP + 2.2, TOP + 2.9, z0, z1, 'paint', BL)                 # bottom chord + floor
        acc.box(wx - 1.75, wx + 1.75, TOP + 6.4, TOP + 7.1, z0, z1, 'paint', BL)                # top chord
        acc.box(wx - 1.55, wx + 1.55, TOP + 7.1, TOP + 7.5, z0, z1, 'paint', '#2c5f9e')         # roof
        for sd in (-1, 1):
            ox = wx + sd * 1.7
            for k in range(13):
                zz = z0 + k * (z1 - z0) / 12
                acc.box(ox - .1, ox + .1, TOP + 2.9, TOP + 6.4, zz - .14, zz + .14, 'paint', WT)
                if k < 12:
                    zn = z0 + (k + 1) * (z1 - z0) / 12
                    acc.beam((ox, TOP + 2.9, zz), (ox, TOP + 6.4, zn), .12, 'paint', BL); acc.beam((ox, TOP + 6.4, zz), (ox, TOP + 2.9, zn), .12, 'paint', BL)
            acc.box(ox - .08, ox + .08, TOP + 4.5, TOP + 4.75, z0, z1, 'paint', WT)
    # side spans: suspension chains from the tower tops down to the shore towers, with hangers to the deck
    for sz in (-1, 1):
        for sx in (-1, 1):
            cx = X + sx * (HW + 1.3); pts = []
            for k in range(13):
                t = k / 12; zz = sz * (21.5 + 12 * t); yy = (TOP + 3) * (1 - t) + 10.5 * t - 6.5 * math.sin(math.pi * t) * .9
                pts.append((cx, yy, zz))
            for a, b in zip(pts[:-1], pts[1:]):
                acc.beam(a, b, .75, 'paint', BL); acc.beam((a[0], a[1] + .42, a[2]), (b[0], b[1] + .42, b[2]), .16, 'paint', WT)
            for a in pts[1:-1]:
                if abs(a[2]) < RIVER - .5: acc.beam((a[0], a[1], a[2]), (a[0], .9, a[2]), .07, 'paint', WT)
        # shore towers at the river bank
        for sx in (-1, 1):
            tx = X + sx * (HW + 1.6); tz = sz * 33.5; a2 = O(tx, tz)
            a2.cbox(tx, 0, tz, 3.2, 11, 3.2, 'stone', ST); a2.cbox(tx, 11, tz, 3.6, .4, 3.6, 'sandstone', '#c4b89c', ao=False)
            pyramid(a2, tx, tz, 1.8, 11.4, 15.5, 'slate', SL); a2.sphere(tx, 15.7, tz, .25, 'gold', GOLD, 6, 4)
def st_pauls():
    """St Paul's Cathedral: Portland-stone nave and transepts, two-storey west portico, twin west towers, colonnaded drum and lead dome with lantern"""
    cx, cz = 40, -165; acc, g = O(cx, cz), Gl(cx, cz)
    PS, PS2, LEAD = '#ece6d6', '#d6ceb9', '#87918f'
    acc.box(4, 13, 0, .45, cz - 11, cz + 11, 'stone', PS2)                                      # west steps
    acc.box(14, 64, 0, 15, cz - 12, cz + 12, 'stone', PS); acc.box(14, 64, 15, 19.5, cz - 7.5, cz + 7.5, 'stone', PS)
    for sz in (-1, 1):
        acc.box(38, 52, 0, 15, min(cz + sz * 12, cz + sz * 21), max(cz + sz * 12, cz + sz * 21), 'stone', PS)
        acc.cyl(45, cz + sz * 21, 5.2, 5.2, 0, 13.5, 20, 'stone', PS2)                           # rounded transept porticos
        for k in range(9):
            a = (k / 8 - .5) * math.pi; acc.cyl(45 + math.sin(a) * 5.9, cz + sz * (21 + math.cos(a) * 5.9), .38, .38, 0, 12.5, 8, 'stone', PS)
        for x in range(17, 63, 4):                                                                   # two tiers of windows along the aisles
            if 37 < x < 53: continue
            facade_windows(g, 'z', cz + sz * 12, x - .9, x + .9, 3.5, 8, 1, .9, sz, .35); facade_windows(g, 'z', cz + sz * 12, x - .9, x + .9, 10, 13.5, 1, .9, sz, .35)
            facade_windows(g, 'z', cz + sz * 7.5, x - .8, x + .8, 15.8, 18.6, 1, .9, sz, .3)
        for y in (9, 14.6): acc.box(14, 64, y, y + .5, min(cz + sz * 12, cz + sz * 12.35), max(cz + sz * 12, cz + sz * 12.35), 'stone', PS2, ao=False)
    for y0, y1, h in ((15, 15.9, 12.3), (19.5, 20.3, 7.8)): acc.box(13.8, 64.2, y0, y1, cz - h, cz + h, 'stone', PS2, ao=False)   # balustrades
    for sz in (-1, 1):                                                                               # lead roof over the nave
        acc.quad((14, 20.3, cz + sz * 7.5), (64, 20.3, cz + sz * 7.5), (64, 23.5, cz), (14, 23.5, cz), 'slate', LEAD) if sz > 0 else acc.quad((64, 20.3, cz - 7.5), (14, 20.3, cz - 7.5), (14, 23.5, cz), (64, 23.5, cz), 'slate', LEAD)
    acc.cyl(64, cz, 7.5, 7.5, 0, 15, 20, 'stone', PS); acc.sphere(64, 15, cz, 7.5, 'slate', LEAD, 16, 6, sy=.55, half=True)   # apse
    # west front: two-storey portico with paired columns and a pediment
    for k in range(12):
        z = cz - 8.25 + k * 1.5; acc.cyl(10.8, z, .42, .42, .45, 9.2, 10, 'stone', PS)
    acc.box(9.8, 14, 9.2, 10.4, cz - 9, cz + 9, 'stone', PS2)
    for k in range(8):
        z = cz - 5.6 + k * 1.6; acc.cyl(11.2, z, .36, .36, 10.4, 17.2, 10, 'stone', PS)
    acc.box(10.4, 14, 17.2, 18.2, cz - 6.5, cz + 6.5, 'stone', PS2)
    acc.face([(10.4, 18.2, cz + 6.5), (10.4, 18.2, cz - 6.5), (10.4, 21.5, cz)], 'stone', PS2); acc.face([(14, 18.2, cz - 6.5), (14, 18.2, cz + 6.5), (14, 21.5, cz)], 'stone', PS2)
    for sz in (-1, 1): acc.quad((10.4, 18.2, cz + sz * 6.5), (14, 18.2, cz + sz * 6.5), (14, 21.5, cz), (10.4, 21.5, cz), 'slate', LEAD) if sz > 0 else acc.quad((14, 18.2, cz - 6.5), (10.4, 18.2, cz - 6.5), (10.4, 21.5, cz), (14, 21.5, cz), 'slate', LEAD)
    acc.box(12, 14, .45, 17.2, cz - 6.5, cz + 6.5, 'stone', PS)
    # twin baroque west towers
    for sz in (-1, 1):
        tz = cz + sz * 10.5
        acc.box(11, 18, 0, 20, tz - 3.4, tz + 3.4, 'stone', PS); acc.box(10.8, 18.2, 20, 20.7, tz - 3.6, tz + 3.6, 'stone', PS2, ao=False)
        acc.cyl(14.5, tz, 2.6, 2.6, 20.7, 26.5, 12, 'stone', PS)
        for k in range(8): a = k / 8 * math.tau; acc.cyl(14.5 + math.cos(a) * 3.1, tz + math.sin(a) * 3.1, .28, .28, 20.7, 26, 6, 'stone', PS)
        acc.cyl(14.5, tz, 3.4, 3.4, 26.5, 27.2, 12, 'stone', PS2); acc.sphere(14.5, 27.2, tz, 2.4, 'slate', LEAD, 12, 5, sy=1.1, half=True)
        acc.cyl(14.5, tz, .9, .4, 29.8, 31.6, 8, 'stone', PS); acc.sphere(14.5, 32.2, tz, .6, 'gold', GOLD, 8, 5)
    # the dome: square base, colonnaded drum, attic, lead dome with ribs, lantern, golden ball and cross
    dx = 45
    acc.box(dx - 9, dx + 9, 19.5, 23, cz - 9, cz + 9, 'stone', PS)
    acc.cyl(dx, cz, 8.8, 8.8, 23, 31, 32, 'stone', PS2)
    for k in range(32):
        a = k / 32 * math.tau; acc.cyl(dx + math.cos(a) * 10.2, cz + math.sin(a) * 10.2, .38, .38, 23, 30.2, 8, 'stone', PS)
    acc.cyl(dx, cz, 10.8, 10.8, 30.2, 31.3, 32, 'stone', PS2); acc.cyl(dx, cz, 8.5, 8.5, 31.3, 34, 32, 'stone', PS)
    acc.sphere(dx, 34, cz, 8.5, 'slate', LEAD, 32, 10, sy=1.42, half=True)
    for k in range(16):
        a = k / 16 * math.tau
        for j in range(8):
            t0, t1 = j / 8 * math.pi / 2, (j + 1) / 8 * math.pi / 2
            p0 = (dx + math.cos(a) * 8.55 * math.cos(t0), 34 + 8.5 * 1.42 * math.sin(t0), cz + math.sin(a) * 8.55 * math.cos(t0))
            p1 = (dx + math.cos(a) * 8.55 * math.cos(t1), 34 + 8.5 * 1.42 * math.sin(t1), cz + math.sin(a) * 8.55 * math.cos(t1))
            if j < 7: acc.beam(p0, p1, .16, 'slate', '#9aa4a2')
    acc.cyl(dx, cz, 1.7, 1.7, 45.5, 49.5, 12, 'stone', PS)
    for k in range(8): a = k / 8 * math.tau; acc.cyl(dx + math.cos(a) * 2.0, cz + math.sin(a) * 2.0, .18, .18, 45.5, 49, 6, 'stone', PS)
    acc.sphere(dx, 49.5, cz, 1.8, 'slate', LEAD, 12, 5, sy=.9, half=True); acc.cyl(dx, cz, .25, .25, 51, 52.6, 8, 'gold', GOLD)
    acc.sphere(dx, 53.1, cz, .6, 'gold', GOLD, 10, 6); acc.cbox(dx, 53.6, cz, .16, 1.8, .16, 'gold', GOLD); acc.cbox(dx, 54.6, cz, .16, .16, .9, 'gold', GOLD)
def stadium(b):
    """Stamford Bridge, built from five scripts (each exec'd here with these shared names):
    stadium_bowl.py (pitch, seating tiers, roofs, floodlights - the inside), stadium_facade.py (outside walls/cladding of the
    four stands and the corners), stadium_entrance.py (main entrance, gates, turnstiles), stadium_plaza.py (forecourt, club
    shop/hotel, statue, flags, lamps around it). Colliders and walk-through gaps live in tools/stadium_layout.py."""
    x0, x1, z0, z1 = b['x0'] + 3, b['x1'] - 3, b['z0'] + 3, b['z1'] - 3; D = 12
    px0, px1, pz0, pz1 = x0 + D, x1 - D, z0 + D, z1 - D; cx, cz = (px0 + px1) / 2, (pz0 + pz1) / 2
    acc = O(cx, cz); BLUE, WHITE_, CLAD = '#1b3f9e', '#e9eef4', '#cfd3d8'
    SG = dict(globals()); SG.update(b=b, x0=x0, x1=x1, z0=z0, z1=z1, D=D, px0=px0, px1=px1, pz0=pz0, pz1=pz1, cx=cx, cz=cz, acc=acc, BLUE=BLUE, WHITE_=WHITE_, CLAD=CLAD)
    for part in ('stadium_bowl.py', 'stadium_facade.py', 'stadium_entrance.py', 'stadium_plaza.py'):
        exec(open(os.path.join(HERE, part)).read(), SG)
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
if not STADIUM_ONLY: big_ben(-144, -42); parliament(); palace(); london_eye(); tower_bridge(); tower_of_london(); shard(); gherkin(); walkie(); cheesegrater(); st_pauls()
else: EYE = __import__('types').SimpleNamespace(to_object=lambda *a, **k: None)
for _b in L['blocks']:
    if _b['kind'] == 'stadium': stadium(_b)
