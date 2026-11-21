"""Stamford Bridge - the bowl (inside): pitch, markings, goals, seating tiers, stand backs, roofs and floodlights.
Exec'd by stadium() in landmarks.py with b, x0, x1, z0, z1, D, px0, px1, pz0, pz1, cx, cz, acc, BLUE, WHITE_, CLAD and all citylib helpers."""
Y = KERB + .1 + .005
n = 12
for k in range(n):                                                                               # mown stripes
    if k % 2: acc.quad((px0 + (px1 - px0) * k / n, Y, pz1), (px0 + (px1 - px0) * (k + 1) / n, Y, pz1), (px0 + (px1 - px0) * (k + 1) / n, Y, pz0), (px0 + (px1 - px0) * k / n, Y, pz0), 'grass', '#c7dcb6', ao=False)
L_ = lambda a, b_, c, d: acc.quad((a, Y + .005, d), (b_, Y + .005, d), (b_, Y + .005, c), (a, Y + .005, c), 'paint', '#f4f4f0', ao=False)
m = 2.5; ax0, ax1, az0, az1 = px0 + m, px1 - m, pz0 + m, pz1 - m; w = .12
L_(ax0, ax1, az0, az0 + w); L_(ax0, ax1, az1 - w, az1); L_(ax0, ax0 + w, az0, az1); L_(ax1 - w, ax1, az0, az1); L_(cx - w / 2, cx + w / 2, az0, az1)
for k in range(32):                                                                              # centre circle
    a0, a1 = k / 32 * math.tau, (k + 1) / 32 * math.tau; r = 6.5
    acc.quad((cx + math.cos(a0) * r, Y + .005, cz + math.sin(a0) * r), (cx + math.cos(a1) * r, Y + .005, cz + math.sin(a1) * r), (cx + math.cos(a1) * (r - w), Y + .005, cz + math.sin(a1) * (r - w)), (cx + math.cos(a0) * (r - w), Y + .005, cz + math.sin(a0) * (r - w)), 'paint', '#f4f4f0', ao=False)
for sx, ex in ((1, ax0), (-1, ax1)):                                                             # penalty boxes and goals
    bx = ex + sx * 12; L_(min(ex, bx), max(ex, bx), cz - 15, cz - 15 + w); L_(min(ex, bx), max(ex, bx), cz + 15 - w, cz + 15); L_(min(bx, bx + sx * w), max(bx, bx + sx * w), cz - 15, cz + 15)
    gx = ex - sx * .1
    for zz in (cz - 3.66, cz + 3.66): acc.cyl(gx, zz, .07, .07, Y, Y + 2.44, 8, 'paint', '#ffffff')
    acc.box(gx - .07, gx + .07, Y + 2.37, Y + 2.51, cz - 3.66, cz + 3.66, 'paint', '#ffffff')
    acc.box(min(gx, gx - sx * 2), max(gx, gx - sx * 2), Y + 2.4, Y + 2.44, cz - 3.66, cz + 3.66, 'metal', '#9aa0a6', ao=False)
BLUE, WHITE_, CLAD = '#1b3f9e', '#e9eef4', '#cfd3d8'
def stand(axis, sgn, a0, a1):
    """tiers rising away from the pitch edge; axis 'x' -> stand runs along z on the x side"""
    edge = (px0 if sgn < 0 else px1) if axis == 'x' else (pz0 if sgn < 0 else pz1)
    for k in range(10):
        i0, i1 = edge + sgn * k * 1.1, edge + sgn * (k + 1) * 1.1; h = .9 + k * .75
        lo, hi = min(i0, i1), max(i0, i1); col = WHITE_ if k in (4,) else BLUE
        if axis == 'x': acc.box(lo, hi, 0, h, a0, a1, 'concrete', '#9aa0a8'); acc.box(lo + .3 * (sgn < 0), hi - .3 * (sgn > 0), h, h + .45, a0, a1, 'paint', col)
        else: acc.box(a0, a1, 0, h, lo, hi, 'concrete', '#9aa0a8'); acc.box(a0, a1, h, h + .45, lo + .3 * (sgn < 0), hi - .3 * (sgn > 0), 'paint', col)
    back = edge + sgn * 11.5; lo, hi = min(back, back + sgn * .5), max(back, back + sgn * .5)
    if axis == 'x':
        acc.box(lo, hi, 0, 14, a0, a1, 'concrete', CLAD); acc.box(lo - .05, hi + .05, 10, 11, a0, a1, 'paint', BLUE)
        acc.box(min(edge - sgn * 1.5, back + sgn * .5), max(edge - sgn * 1.5, back + sgn * .5), 14, 14.5, a0, a1, 'metal', '#e4e7ea')
        acc.box(min(edge - sgn * 1.5, edge - sgn * 1.0), max(edge - sgn * 1.5, edge - sgn * 1.0), 13.2, 14, a0, a1, 'lampglass', '#fff7e6', ao=False)
    else:
        acc.box(a0, a1, 0, 14, lo, hi, 'concrete', CLAD); acc.box(a0, a1, 10, 11, lo - .05, hi + .05, 'paint', BLUE)
        acc.box(a0, a1, 14, 14.5, min(edge - sgn * 1.5, back + sgn * .5), max(edge - sgn * 1.5, back + sgn * .5), 'metal', '#e4e7ea')
        acc.box(a0, a1, 13.2, 14, min(edge - sgn * 1.5, edge - sgn * 1.0), max(edge - sgn * 1.5, edge - sgn * 1.0), 'lampglass', '#fff7e6', ao=False)
