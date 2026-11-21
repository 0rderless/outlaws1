"""Sport motorbike -> assets/cars/bike.glb
Nodes: Body (empty, children = bodywork, frame, engine...), WheelF / WheelR (empties on the axles, children = tyre, rim, discs).
Game space: x right, y up, z forward. Front axle z=+.71, rear z=-.71."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector, Matrix
from citylib import hexc, ROOT
bpy.ops.wm.read_factory_settings(use_empty=True)
SC = bpy.context.scene.collection
M = {}
def mat(n, c, r, m=0.0, e=None):
    x = bpy.data.materials.new(n); x.use_nodes = True; b = x.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = list(hexc(c)) + [1]; b.inputs['Roughness'].default_value = r; b.inputs['Metallic'].default_value = m
    if e: b.inputs['Emission Color'].default_value = list(hexc(e)) + [1]; b.inputs['Emission Strength'].default_value = 1.5
    M[n] = x
mat('Paint', '#ffffff', .3, .3); mat('Black', '#151618', .5); mat('Alloy', '#8f969d', .35, .8); mat('Steel', '#c9ced4', .2, 1.0)
mat('Leather', '#1b1b1d', .65); mat('Tyre', '#121212', .9); mat('Screen', '#141c24', .05, .2); mat('Plate', '#f2c200', .4); mat('Disc', '#8d9297', .4, .6)
mat('LightF', '#f6f3ea', .05, 0, '#fff6e0'); mat('LightR', '#a50d12', .15, 0, '#ff1a1a')
G = lambda p: Vector((p[0], -p[2], p[1]))  # game -> blender
def empty(name, pos):
    o = bpy.data.objects.new(name, None); o.location = G(pos); SC.objects.link(o); return o
def mk(name, bm, mname, parent, smooth=True, subsurf=0):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(M[mname])
    for p in me.polygons: p.use_smooth = smooth
    o = bpy.data.objects.new(name, me); SC.objects.link(o); o.parent = parent
    if subsurf: m = o.modifiers.new('sub', 'SUBSURF'); m.levels = m.render_levels = subsurf
    return o
def sweep(bm, secs, n=12, p=2.6, cap=True, xoff=0.0):
    """secs: [(y, z, w, h)] along a path in the y-z plane (game space); rings are superellipses perpendicular to the path."""
    rings = []
    for i, (y, z, w, h) in enumerate(secs):
        a, b = secs[max(0, i - 1)], secs[min(len(secs) - 1, i + 1)]
        ty, tz = b[0] - a[0], b[1] - a[1]; l = math.hypot(ty, tz) or 1; ty, tz = ty / l, tz / l
        ny, nz = tz, -ty   # in-plane normal (points up when the path runs forward)
        if ny < 0: ny, nz = -ny, -nz
        ring = []
        for k in range(n):
            t = k / n * math.tau; c, s = math.cos(t), math.sin(t)
            ex = math.copysign(abs(c) ** (2 / p), c) * w / 2; ey = math.copysign(abs(s) ** (2 / p), s) * h / 2
            ring.append(bm.verts.new(G((xoff + ex, y + ny * ey, z + nz * ey))))
        rings.append(ring)
    for i in range(len(rings) - 1):
        for k in range(n): bm.faces.new((rings[i][k], rings[i][(k + 1) % n], rings[i + 1][(k + 1) % n], rings[i + 1][k]))
    if cap: bm.faces.new(rings[0]); bm.faces.new(rings[-1][::-1])
def tube(bm, p0, p1, r, seg=10):
    a, b = G(p0), G(p1); d = b - a; q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=d.length, matrix=Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4())
def box(bm, c, s, rx=0.0):
    bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation(G(c)) @ Matrix.Rotation(-rx, 4, 'X') @ Matrix.Diagonal((s[0], s[2], s[1], 1)))
def blob(bm, c, s, seg=12):
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=8, radius=1, matrix=Matrix.Translation(G(c)) @ Matrix.Diagonal((s[0], s[2], s[1], 1)))
def disc(bm, x, r, t, seg=24, c=(0, 0, 0)):  # cylinder along the axle (game x)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=t, matrix=Matrix.Translation(G((c[0] + x, c[1], c[2]))) @ Matrix.Rotation(math.pi / 2, 4, 'Y'))
def arc(bm, cy, cz, R, a0, a1, w, h, n=10, xoff=0.0):  # sweep around an axle (angles from forward, counter-clockwise up)
    secs = [(cy + math.sin(a0 + (a1 - a0) * i / n) * R, cz + math.cos(a0 + (a1 - a0) * i / n) * R, w, h) for i in range(n + 1)]
    sweep(bm, secs, 8, 2.2, True, xoff)
def B(): return bmesh.new()
RF, RR, ZF, ZR = .31, .32, .69, -.69
body = empty('Body', (0, 0, 0))
# front cowl + side fairings + tank: one smooth loft (kept above the front wheel, down to the belly behind it)
bm = B(); sweep(bm, [(.83, .99, .04, .04), (.83, .95, .17, .19), (.84, .84, .30, .34), (.85, .66, .35, .40), (.81, .48, .34, .40), (.67, .37, .32, .68),
                     (.62, .16, .31, .62), (.64, -.01, .27, .48), (.66, -.08, .16, .30)], 16, 3.4)
mk('Fairing', bm, 'Paint', body, subsurf=1)
bm = B(); sweep(bm, [(.78, -.03, .26, .2), (.84, -.35, .24, .16), (.93, -.65, .18, .14), (.99, -.88, .1, .08), (1.0, -.95, .04, .04)], 12, 2.4)
mk('Tail', bm, 'Paint', body, subsurf=1)
bm = B(); sweep(bm, [(.86, .14, .18, .05), (.89, .05, .28, .08), (.90, -.18, .27, .08), (.91, -.33, .2, .06), (.92, -.38, .1, .04)], 10, 3.0)
mk('Seat', bm, 'Leather', body, subsurf=1)
bm = B(); sweep(bm, [(.98, .80, .16, .02), (1.05, .70, .28, .02), (1.13, .57, .22, .02)], 10, 3.0, cap=False)
mk('Screen', bm, 'Screen', body, subsurf=1)
bm = B(); arc(bm, RF, ZF, RF + .06, math.radians(20), math.radians(118), .12, .022)   # front mudguard
mk('Guard', bm, 'Paint', body, subsurf=1)
bm = B(); [blob(bm, (sx * .075, .84, .955), (.055, .035, .03)) for sx in (-1, 1)]; mk('Head', bm, 'LightF', body)
bm = B(); box(bm, (0, .985, -.915), (.1, .035, .02)); mk('Rear', bm, 'LightR', body)
bm = B(); box(bm, (0, .70, -.96), (.2, .13, .012), rx=.3); mk('Plate', bm, 'Plate', body)
bm = B()
for sx in (-1, 1):
    tube(bm, (sx * .12, .42, -.08), (sx * .11, RR, ZR), .03)                        # swingarm
    tube(bm, (sx * .085, 1.0, .48), (sx * .085, .66, .62), .032)                    # fork uppers
mk('Arm', bm, 'Alloy', body)
bm = B()
for sx in (-1, 1):
    tube(bm, (sx * .085, .68, .614), (sx * .085, RF, ZF), .04)                       # fork lowers
    tube(bm, (sx * .085, .98, .47), (sx * .3, .96, .42), .017); tube(bm, (sx * .24, .962, .43), (sx * .32, .958, .415), .023)   # clip-ons, grips
    tube(bm, (sx * .17, 1.0, .66), (sx * .25, 1.07, .66), .008); blob(bm, (sx * .27, 1.075, .66), (.055, .032, .015))          # mirrors
    tube(bm, (sx * .13, .45, -.16), (sx * .22, .45, -.16), .014)                     # pegs
    tube(bm, (sx * .13, .45, -.16), (sx * .1, .6, -.26), .012)                       # hangers
box(bm, (0, .25, .2), (.24, .16, .34))                                               # sump / belly bottom
tube(bm, (0, .55, -.1), (0, .78, -.02), .03)                                         # shock
arc(bm, RR, ZR, RR + .06, math.radians(55), math.radians(112), .15, .02)            # hugger
box(bm, (0, .82, -.93), (.04, .16, .05), rx=.5)                                      # plate hanger
mk('Running', bm, 'Black', body)
bm = B(); [tube(bm, p, q, r, 14) for p, q, r in (((.06, .24, .32), (.1, .26, .02), .04), ((.1, .26, .02), (.15, .4, -.22), .042), ((.15, .4, -.22), (.18, .58, -.62), .07))]
blob(bm, (.18, .58, -.62), (.072, .072, .03)); mk('Exhaust', bm, 'Steel', body)
def wheel(name, r, z, front):
    e = empty(name, (0, r, z)); wt = .13 if front else .17; mr = wt * .48
    def torus(bm, R, rm, sx=1.05, nU=28, nV=10):
        vs = [[bm.verts.new(G((rm * math.sin(v / nV * math.tau) * sx, (R + rm * math.cos(v / nV * math.tau)) * math.cos(u / nU * math.tau), (R + rm * math.cos(v / nV * math.tau)) * math.sin(u / nU * math.tau)))) for v in range(nV)] for u in range(nU)]
        for u in range(nU):
            for v in range(nV): bm.faces.new((vs[u][v], vs[(u + 1) % nU][v], vs[(u + 1) % nU][(v + 1) % nV], vs[u][(v + 1) % nV]))
    R = r - mr
    bm = B(); torus(bm, R, mr); mk(name + 'Tyre', bm, 'Tyre', e)
    bm = B(); torus(bm, R - mr * .85, .022, 2.2, 32, 8); disc(bm, 0, .05, wt * .9, 12)
    for k in range(5):
        a = k / 5 * math.tau; bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Rotation(a, 4, 'X') @ Matrix.Translation((0, 0, (R - mr) * .5)) @ Matrix.Diagonal((.028, .03, (R - mr) * 1.0, 1)))
    mk(name + 'Rim', bm, 'Alloy', e)
    bm = B()
    for sx in ((-1, 1) if front else (1,)): disc(bm, sx * (.07 if front else .08), .15 if front else .11, .008, 28)
    mk(name + 'Disc', bm, 'Disc', e)
wheel('WheelF', RF, ZF, True); wheel('WheelR', RR, ZR, False)
bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT, 'assets', 'cars', 'bike.glb'), export_format='GLB', export_yup=True, export_apply=True)
print('exported bike', sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH'))
