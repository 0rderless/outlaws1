"""Street props modelled in Blender -> assets/city/props.glb (one object per prop, instanced by the game)."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector, Matrix, noise
from citylib import *
reset(); R = random.Random(5)
MET = '#1f2724'
def lamp():
    a = Acc()
    a.cyl(0, 0, .26, .24, 0, .5, 8, 'metal', MET); a.cyl(0, 0, .2, .17, .5, .75, 8, 'metal', MET)
    a.cyl(0, 0, .1, .075, .75, 4.4, 10, 'metal', MET)
    for y in (1.2, 2.6, 4.2): a.cyl(0, 0, .13, .13, y, y + .1, 10, 'metal', MET)
    a.cyl(0, 0, .09, .2, 4.4, 4.65, 8, 'metal', MET)
    h0, h1, w0, w1 = 4.65, 5.35, .2, .3
    for i in range(4):
        a0, a1 = i * math.pi / 2 + math.pi / 4, (i + 1) * math.pi / 2 + math.pi / 4
        p = lambda ang, w, y: (math.sin(ang) * w, y, math.cos(ang) * w)
        a.quad(p(a0, w0, h0), p(a1, w0, h0), p(a1, w1, h1), p(a0, w1, h1), 'lampglass', '#fff2d6', ao=False)
        a.beam(p(a0, w0, h0), p(a0, w1, h1), .035, 'metal', MET)
    a.cyl(0, 0, w1 * 1.45, .05, h1, h1 + .35, 4, 'metal', MET, ry=math.pi / 4); a.sphere(0, h1 + .42, 0, .07, 'metal', MET, 6, 4)
    return a
def beacon():
    a = Acc()
    for i in range(6): a.cyl(0, 0, .06, .06, i * .45, (i + 1) * .45, 8, 'paint', '#f2f2f2' if i % 2 else '#151515', cap=i == 5)
    a.sphere(0, 2.95, 0, .2, 'signal', '#ffb11a', 12, 8)
    return a
def leaf_cluster(a, c, r, tint):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    off = Vector((R.random() * 9, R.random() * 9, R.random() * 9))
    for v in bm.verts: v.co *= 1 + .28 * noise.noise(v.co * 1.4 + off)
    a.add_bm(bm, Matrix.Translation(Vector(c)) @ Matrix.Diagonal((1, .82, 1, 1)), 'leaves', tint); bm.free()
def tree(kind):
    a = Acc(); greens = ['#5f8f45', '#6d9a4a', '#557f3b', '#7aa352', '#4f7d3a']
    h = 3.4 if kind == 1 else 2.8
    a.cyl(0, 0, .26, .17, 0, h, 9, 'bark', '#c9b8a4')
    tops = []
    for k in range(5 if kind == 1 else 4):
        ang = k / (5 if kind == 1 else 4) * math.tau + R.uniform(-.3, .3); y0 = h * R.uniform(.7, .95)
        L = R.uniform(1.6, 2.4); p1 = (math.sin(ang) * L * .75, y0 + L * .85, math.cos(ang) * L * .75)
        a.beam((0, y0, 0), p1, .14, 'bark', '#c9b8a4'); tops.append(p1)
    if kind == 1:
        for p in tops: leaf_cluster(a, (p[0], p[1] + .6, p[2]), R.uniform(1.4, 1.9), R.choice(greens))
        leaf_cluster(a, (0, h + 3.1, 0), 2.1, R.choice(greens)); leaf_cluster(a, (.6, h + 4.2, -.4), 1.5, R.choice(greens))
    else:
        leaf_cluster(a, (0, h + 2.4, 0), 2.7, R.choice(greens))
        for p in tops: leaf_cluster(a, (p[0] * .8, p[1] + .3, p[2] * .8), 1.6, R.choice(greens))
    return a
def phonebox():
    a = Acc(); RED = '#c8102e'
    a.box(-.55, .55, 0, .18, -.55, .55, 'paint', RED)
    for sx, sz in ((-1, -1), (1, -1), (-1, 1), (1, 1)): a.cbox(sx * .46, .18, sz * .46, .16, 2.3, .16, 'paint', RED)
    for i in range(4):
        ang = i * math.pi / 2
        c, s = math.cos(ang), math.sin(ang)
        def P(u, y, d): return (c * u + s * d, y, -s * u + c * d)
        a.quad(P(-.38, .35, .47), P(.38, .35, .47), P(.38, 2.1, .47), P(-.38, 2.1, .47), 'lampglass', '#7f8d93', ao=False)
        for k in range(1, 3): a.quad(P(-.38, .35 + k * .58, .48), P(.38, .35 + k * .58, .48), P(.38, .39 + k * .58, .48), P(-.38, .39 + k * .58, .48), 'paint', RED)
        a.quad(P(-.38, 2.2, .52), P(.38, 2.2, .52), P(.38, 2.36, .52), P(-.38, 2.36, .52), 'paint', '#f2f2f2', ao=False)
    a.box(-.56, .56, 2.1, 2.5, -.56, .56, 'paint', RED)
    for i in range(10):
        t0, t1 = i / 10 * math.pi, (i + 1) / 10 * math.pi
        for ax in (0, 1):
            y0, y1 = 2.5 + math.sin(t0) * .22, 2.5 + math.sin(t1) * .22; u0, u1 = -math.cos(t0) * .56, -math.cos(t1) * .56
            if ax == 0: a.quad((u0, y0, .56), (u1, y1, .56), (u1, y1, -.56), (u0, y0, -.56), 'paint', RED)
    return a
def postbox():
    a = Acc(); a.box(-.32, .32, 0, .1, -.32, .32, 'metal', '#151515'); a.cyl(0, 0, .3, .27, .1, 1.35, 14, 'paint', '#c8102e')
    a.sphere(0, 1.35, 0, .31, 'paint', '#c8102e', 14, 5, sy=.45, half=True); a.cbox(0, 1.0, .27, .24, .05, .06, 'metal', '#111'); a.cbox(0, .7, .28, .14, .14, .02, 'paint', '#f4d03f')
    return a
def busstop():
    a = Acc(); F = '#2b3036'
    for dx in (-1.8, 1.8):
        for dz in (-.7, .7): a.cbox(dx, 0, dz, .08, 2.4, .08, 'metal', F)
    a.box(-2, 2, 2.4, 2.5, -.8, .8, 'metal', F)
    a.box(-1.8, 1.8, .3, 2.3, -.72, -.68, 'lampglass', '#9ab8c8', ao=False)
    a.box(-1.82, -1.78, .3, 2.3, -.7, .5, 'lampglass', '#9ab8c8', ao=False)
    a.box(-1.5, 1.5, .45, .5, -.6, -.3, 'metal', '#8b8f94')
    a.cbox(2.6, 0, .5, .1, 3, .1, 'metal', F); a.cyl(2.6, .56, .3, .3, 2.6, 2.66, 16, 'paint', '#d42a20')
    return a
def bench():
    a = Acc()
    for k in range(4): a.box(-.9, .9, .45 + k * 0, .5, -.22 + k * .12, -.14 + k * .12, 'wood', '#b07a4a')
    for k in range(2): a.box(-.9, .9, .62 + k * .16, .72 + k * .16, .24, .28, 'wood', '#b07a4a')
    for dx in (-.8, .8): a.box(dx - .04, dx + .04, 0, .9, -.25, .28, 'metal', MET)
    return a
for name, fn in (('lamp', lamp), ('beacon', beacon), ('tree1', lambda: tree(1)), ('tree2', lambda: tree(2)), ('phonebox', phonebox), ('postbox', postbox), ('busstop', busstop), ('bench', bench)):
    o = fn().to_object(name); print(name, len(o.data.polygons))
export(os.path.join(ROOT, 'assets', 'city', 'props.glb')); print('exported props')
