"""Main battle tank -> assets/cars/tank.glb.  Nodes: Hull (origin 0), Turret (origin on the turret ring, yaws), Gun (origin at the trunnion, pitches).
Blender axes: x side, y length (front at -y), z up."""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
def hexc(h): h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]; return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c] + [1]
M = {}
def mat(n, c, r=.6, m=0.0, e=None, es=0.0):
    x = bpy.data.materials.new(n); x.use_nodes = True; b = x.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = hexc(c); b.inputs['Roughness'].default_value = r; b.inputs['Metallic'].default_value = m
    if e: b.inputs['Emission Color'].default_value = hexc(e); b.inputs['Emission Strength'].default_value = es
    M[n] = x
bpy.ops.wm.read_factory_settings(use_empty=True)
for a in (('Paint', '#ffffff', .75, .05), ('Black', '#141516', .6), ('Track', '#1b1c1d', .85, .2), ('Metal', '#4b4f52', .45, .6), ('Glass', '#0e1419', .05)): mat(*a)
mat('LightF', '#f6f3ea', .05, 0, '#fff6e0', 1.5); mat('LightR', '#a50d12', .15, 0, '#ff1a1a', 1.2)
SC = bpy.context.scene.collection
def empty(name, pos, parent=None):
    o = bpy.data.objects.new(name, None); o.location = pos; SC.objects.link(o); o.parent = parent; return o
def mk(name, bm, mname, parent, smooth=False, offset=(0, 0, 0)):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if offset != (0, 0, 0): bmesh.ops.translate(bm, verts=bm.verts[:], vec=Vector(offset) * -1)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(M[mname])
    for p in me.polygons: p.use_smooth = smooth
    o = bpy.data.objects.new(name, me); SC.objects.link(o); o.parent = parent; return o
def hull_poly(bm, pts, x0, x1):
    """prism: polygon pts [(y, z)] extruded from x0 to x1"""
    a = [bm.verts.new((x0, y, z)) for y, z in pts]; b = [bm.verts.new((x1, y, z)) for y, z in pts]; n = len(pts)
    bm.faces.new(a[::-1]); bm.faces.new(b)
    for i in range(n): bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
def box(bm, c, s, rx=0.0, rz=0.0): bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation(Vector(c)) @ Matrix.Rotation(rz, 4, 'Z') @ Matrix.Rotation(rx, 4, 'X') @ Matrix.Diagonal((s[0], s[1], s[2], 1)))
def cyl(bm, c, r, d, axis='X', seg=16, r2=None):
    rot = {'X': Matrix.Rotation(math.pi / 2, 4, 'Y'), 'Y': Matrix.Rotation(math.pi / 2, 4, 'X'), 'Z': Matrix.Identity(4)}[axis]
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=d, matrix=Matrix.Translation(Vector(c)) @ rot)
B = bmesh.new
hull = empty('Hull', (0, 0, 0))
# hull: sloped glacis, raised engine deck at the rear
bm = B(); hull_poly(bm, [(-3.75, .95), (-2.9, 1.72), (2.2, 1.72), (2.45, 1.95), (3.7, 1.95), (3.75, .75), (3.2, .48), (-3.2, .48)], -1.5, 1.5); mk('hullbody', bm, 'Paint', hull)
bm = B(); box(bm, (0, -2.0, 1.75), (2.2, .9, .08)); mk('driverhatch', bm, 'Metal', hull)
bm = B()
for sx in (-1, 1):
    hull_poly(bm, [(-3.9, 1.32), (3.85, 1.32), (3.85, 1.38), (-3.9, 1.38)], sx * 1.5, sx * 1.86)               # track guards
    hull_poly(bm, [(-3.55, .62), (-3.85, 1.0), (-3.85, 1.32), (3.6, 1.32), (3.6, .62)], sx * 1.86, sx * 1.92)   # side skirts
mk('skirts', bm, 'Paint', hull)
def track(bm, sx):   # belt: rounded loop in the y-z plane
    pts = []
    for k in range(12): a = math.pi / 2 + k / 11 * math.pi; pts.append((-3.3 + math.cos(a) * .45, .5 + math.sin(a) * .45))
    for k in range(12): a = -math.pi / 2 + k / 11 * math.pi; pts.append((3.3 + math.cos(a) * .48, .52 + math.sin(a) * .48))
    xo, xi = sx * 1.88, sx * 1.22
    o = [bm.verts.new((xo, y, z)) for y, z in pts]; i_ = [bm.verts.new((xi, y, z)) for y, z in pts]; n = len(pts)
    for k in range(n): bm.faces.new((o[k], o[(k + 1) % n], i_[(k + 1) % n], i_[k]))
    for k in range(n): bm.faces.new((o[(k + 1) % n], o[k], bm.verts.new((xo * .995, pts[k][0] * .97, .5 + (pts[k][1] - .5) * .82)), bm.verts.new((xo * .995, pts[(k + 1) % n][0] * .97, .5 + (pts[(k + 1) % n][1] - .5) * .82)))) if False else None
bm = B()
for sx in (-1, 1): track(bm, sx)
mk('tracks', bm, 'Track', hull)
bm = B()
for sx in (-1, 1):
    for k in range(7): cyl(bm, (sx * 1.55, -2.55 + k * .85, .42), .37, .55, 'X', 16)
    cyl(bm, (sx * 1.55, 3.3, .55), .38, .5, 'X', 12); cyl(bm, (sx * 1.55, -3.3, .5), .34, .5, 'X', 12)
mk('wheels', bm, 'Black', hull)
bm = B()
for sx in (-1, 1): box(bm, (sx * 1.2, -3.6, 1.55), (.22, .08, .14))
mk('headlights', bm, 'LightF', hull)
bm = B()
for sx in (-1, 1): box(bm, (sx * 1.25, 3.76, 1.6), (.2, .06, .12))
mk('taillights', bm, 'LightR', hull)
bm = B()
for k in range(4): box(bm, (-.6 + k * .4, 3.2, 2.0), (.3, .5, .1))   # engine grilles
box(bm, (1.1, 3.0, 2.05), (.5, .7, .2)); cyl(bm, (-1.1, 3.4, 2.1), .18, .4, 'Z', 12)   # stowage, exhaust
mk('deck', bm, 'Metal', hull)
# turret: angular armour box on the ring, hatches, sights, smoke dischargers, roof machine gun
TY = .35; TZ = 1.72
turret = empty('Turret', (0, TY, TZ), hull)
bm = B(); hull_poly(bm, [(-2.05, .1), (-1.55, .78), (1.85, .78), (2.2, .55), (2.2, 0), (-1.3, 0), (-2.05, .1)][:-1], -1.6, 1.6)
for v in bm.verts: v.co.y += TY; v.co.z += TZ
for v in bm.verts:   # taper the cheeks in plan
    f = max(0.0, (-(v.co.y - TY) - .6) / 1.5); v.co.x *= 1 - .22 * f
mk('turretbody', bm, 'Paint', turret, offset=(0, TY, TZ))
bm = B()
box(bm, (.55, TY + .5, TZ + .9), (.55, .55, .18)); cyl(bm, (-.6, TY + .3, TZ + .88), .38, .14, 'Z', 16)   # commander sight, loader hatch
box(bm, (-.6, TY - .6, TZ + 1.0), (.4, .35, .32))
for sx in (-1, 1):
    for k in range(5): cyl(bm, (sx * 1.38, TY - 1.2 + k * .1, TZ + .62 + (k % 2) * .1), .07, .28, 'Y', 8)
box(bm, (0, TY + 2.25, TZ + .42), (2.6, .4, .5))   # bustle rack
mk('turretkit', bm, 'Metal', turret, offset=(0, TY, TZ))
bm = B(); cyl(bm, (.75, TY - .35, TZ + 1.06), .035, 1.1, 'Y', 8); box(bm, (.75, TY + .1, TZ + 1.0), (.18, .45, .16)); box(bm, (.75, TY + .25, TZ + .9), (.08, .08, .2))
mk('mg', bm, 'Black', turret, offset=(0, TY, TZ))
bm = B(); box(bm, (.55, TY + .5, TZ + 1.0), (.4, .05, .1)); mk('sightglass', bm, 'Glass', turret, offset=(0, TY, TZ))
# gun: mantlet + long barrel with thermal sleeve and fume extractor, pivoting at the trunnion
GY, GZ = TY - 1.75, TZ + .45
gun = empty('Gun', (0, GY - TY, GZ - TZ), turret)
bm = B(); box(bm, (0, GY - .15, GZ), (1.05, .55, .62))
cyl(bm, (0, GY - 2.8, GZ), .11, 5.3, 'Y', 16); cyl(bm, (0, GY - 2.3, GZ), .17, 1.0, 'Y', 16); cyl(bm, (0, GY - 3.7, GZ), .14, 1.8, 'Y', 16); cyl(bm, (0, GY - 5.35, GZ), .13, .25, 'Y', 16)
mk('gunbody', bm, 'Paint', gun, offset=(0, GY, GZ))
for o in bpy.data.objects:
    if o.type == 'MESH' and o.parent and o.parent.name in ('Turret', 'Gun'): pass
out = os.path.join(ROOT, 'assets', 'cars', 'tank.glb')
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_yup=True)
print('exported', out, sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH'))
