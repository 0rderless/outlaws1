"""Wheels -> assets/cars/wheel.glb (car alloy, unit radius) and assets/cars/buswheel.glb (steel bus wheel, unit radius).
Axle along X, tyre outer radius 1."""
import bpy, bmesh, math, sys, os
from mathutils import Matrix, Vector
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
def hexc(h): h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]; return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c] + [1]
def mat(n, c, r, m):
    M = bpy.data.materials.new(n); M.use_nodes = True; b = M.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = hexc(c); b.inputs['Roughness'].default_value = r; b.inputs['Metallic'].default_value = m; return M
def obj(name, bm, m, smooth=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); me.materials.append(m)
    for p in me.polygons: p.use_smooth = smooth
    return o
def lathe(bm, prof, segs, close=False):  # prof: [(radius, x)] around the X axis
    rings = [[bm.verts.new((x, math.cos(i / segs * math.tau) * r, math.sin(i / segs * math.tau) * r)) for r, x in prof] for i in range(segs)]
    for i in range(segs):
        for k in range(len(prof) - 1): bm.faces.new((rings[i][k], rings[i][k + 1], rings[(i + 1) % segs][k + 1], rings[(i + 1) % segs][k]))
    if close:
        for k in (0, len(prof) - 1):
            pass
    return rings
def disc(bm, x, r, t, seg=32): bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=t, matrix=Matrix.Translation((x, 0, 0)) @ Matrix.Rotation(math.pi / 2, 4, 'Y'))
def export(path):
    objs = [o for o in bpy.data.objects if o.type == 'MESH']
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join()
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', export_yup=True); print('exported', path, len(bpy.context.view_layer.objects.active.data.polygons))
# ------------------------------------------------------------------ car alloy (tyre 1.0 radius, 0.64 wide)
bpy.ops.wm.read_factory_settings(use_empty=True)
tyre = mat('Tyre', '#151515', .88, 0); rim = mat('Rim', '#c3c8cd', .22, 1); dark = mat('Hub', '#2c2e31', .45, .6); dsc = mat('Disc', '#7c8186', .45, .8)
bm = bmesh.new()  # tyre with bulging sidewalls and a rounded shoulder
lathe(bm, [(.64, -.29), (.70, -.315), (.80, -.33), (.90, -.325), (.965, -.29), (.995, -.22), (1.0, -.1), (1.0, .1), (.995, .22), (.965, .29), (.90, .325), (.80, .33), (.70, .315), (.64, .29)], 44)
obj('tyre', bm, tyre)
bm = bmesh.new(); lathe(bm, [(.645, .3), (.63, .2), (.6, -.25), (.2, -.27), (.0, -.27)], 36); obj('barrel', bm, dark)   # inner barrel (dark)
bm = bmesh.new(); lathe(bm, [(.0, .19), (.14, .2), (.18, .17), (.6, .245), (.655, .27), (.67, .29), (.655, .305), (.62, .30)], 40); obj('face', bm, dark)  # concave face behind the spokes
bm = bmesh.new()
for k in range(10):   # ten concave spokes, paired
    a = (k // 2) / 5 * math.tau + (k % 2 - .5) * .17
    for (r0, x0), (r1, x1) in [((.17, .27), (.62, .285))]:
        n = 4; pts = []
        for j in range(n + 1):
            f = j / n; rr = r0 + (r1 - r0) * f; xx = x0 + (x1 - x0) * f - math.sin(f * math.pi) * .05; w = .055 - .02 * f
            pts.append((rr, xx, w))
        verts = []
        for rr, xx, w in pts:
            ca, sa = math.cos(a), math.sin(a); tx, ty = -sa, ca
            verts.append([bm.verts.new((xx + dx, ca * rr + tx * w * sw, sa * rr + ty * w * sw)) for dx, sw in ((.03, -1), (.03, 1), (-.03, 1), (-.03, -1))])
        for j in range(len(verts) - 1):
            for q in range(4): bm.faces.new((verts[j][q], verts[j][(q + 1) % 4], verts[j + 1][(q + 1) % 4], verts[j + 1][q]))
        bm.faces.new(verts[0][::-1]); bm.faces.new(verts[-1])
lathe(bm, [(.62, .31), (.66, .315), (.675, .3), (.665, .28)], 40)       # polished lip
lathe(bm, [(.0, .33), (.08, .33), (.12, .315), (.16, .29), (.18, .27)], 24)   # centre cap
for k in range(5):
    a = k / 5 * math.tau + .3; bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=.025, radius2=.02, depth=.04, matrix=Matrix.Translation((.3, math.cos(a) * .12, math.sin(a) * .12)) @ Matrix.Rotation(math.pi / 2, 4, 'Y'))
obj('spokes', bm, rim, smooth=False)
bm = bmesh.new(); disc(bm, -.02, .52, .05, 36); obj('disc', bm, dsc)
export(os.path.join(ROOT, 'assets', 'cars', 'wheel.glb'))
# ------------------------------------------------------------------ bus: dark steel wheel with chrome hub ring and nuts
bpy.ops.wm.read_factory_settings(use_empty=True)
tyre = mat('Tyre', '#151515', .9, 0); steel = mat('BusRim', '#5a1418', .45, .3); chrome = mat('Chrome', '#d4d8dc', .15, 1)
bm = bmesh.new(); lathe(bm, [(.58, -.3), (.66, -.33), (.82, -.335), (.95, -.3), (1.0, -.15), (1.0, .15), (.95, .3), (.82, .335), (.66, .33), (.58, .3)], 40); obj('tyre', bm, tyre)
bm = bmesh.new(); lathe(bm, [(.0, .2), (.3, .2), (.42, .24), (.56, .24), (.6, .3), (.58, .32)], 32); obj('rim', bm, steel)
for k in range(8):
    a = k / 8 * math.tau; bm = bmesh.new(); disc(bm, .25, .08, .02, 12); obj('hole', bm, tyre) if False else None
bm = bmesh.new(); lathe(bm, [(.0, .34), (.14, .34), (.2, .3), (.24, .26)], 24)
for k in range(10):
    a = k / 10 * math.tau; bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=.03, radius2=.025, depth=.05, matrix=Matrix.Translation((.26, math.cos(a) * .3, math.sin(a) * .3)) @ Matrix.Rotation(math.pi / 2, 4, 'Y'))
obj('hub', bm, chrome)
export(os.path.join(ROOT, 'assets', 'cars', 'buswheel.glb'))
