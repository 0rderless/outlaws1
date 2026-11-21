"""Light helicopter -> assets/cars/heli.glb.  Nodes: Body, Rotor (main rotor, origin on the mast), TailRotor (fan, origin on its hub).
Blender axes: x side, y length (nose at -y), z up."""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
def hexc(h): h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]; return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c] + [1]
M = {}
def mat(n, c, r=.5, m=0.0, e=None, es=0.0):
    x = bpy.data.materials.new(n); x.use_nodes = True; b = x.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = hexc(c); b.inputs['Roughness'].default_value = r; b.inputs['Metallic'].default_value = m
    if e: b.inputs['Emission Color'].default_value = hexc(e); b.inputs['Emission Strength'].default_value = es
    M[n] = x
bpy.ops.wm.read_factory_settings(use_empty=True)
for a in (('Paint', '#ffffff', .3, .2), ('Glass', '#0e1419', .05), ('Black', '#141516', .55), ('Chrome', '#c9ced4', .2, 1.0), ('Stripe', '#f2c200', .4), ('Blade', '#202224', .5, .3)): mat(*a)
mat('LightF', '#f6f3ea', .05, 0, '#fff6e0', 1.5); mat('LightR', '#a50d12', .15, 0, '#ff1a1a', 1.2); mat('Amber', '#1f9d3a', .2, 0, '#22ff55', .8)
SC = bpy.context.scene.collection
def empty(name, pos): o = bpy.data.objects.new(name, None); o.location = pos; SC.objects.link(o); return o
def mk(name, bm, mats, parent, smooth=True, offset=(0, 0, 0), subsurf=0):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if offset != (0, 0, 0): bmesh.ops.translate(bm, verts=bm.verts[:], vec=-Vector(offset))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in (mats if isinstance(mats, list) else [mats]): me.materials.append(M[m])
    o = bpy.data.objects.new(name, me); SC.objects.link(o); o.parent = parent
    for p in me.polygons: p.use_smooth = smooth
    if subsurf: m = o.modifiers.new('s', 'SUBSURF'); m.levels = m.render_levels = subsurf
    return o
def sweep(bm, secs, n=14, p=2.4):
    rings = []
    for y, zc, w, h in secs:
        rings.append([bm.verts.new((math.copysign(abs(math.cos(k / n * math.tau)) ** (2 / p), math.cos(k / n * math.tau)) * w / 2, y,
                                    zc + math.copysign(abs(math.sin(k / n * math.tau)) ** (2 / p), math.sin(k / n * math.tau)) * h / 2)) for k in range(n)])
    for i in range(len(rings) - 1):
        for k in range(n): bm.faces.new((rings[i][k], rings[i][(k + 1) % n], rings[i + 1][(k + 1) % n], rings[i + 1][k]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
def box(bm, c, s, rx=0.0): bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation(Vector(c)) @ Matrix.Rotation(rx, 4, 'X') @ Matrix.Diagonal((s[0], s[1], s[2], 1)))
def tube(bm, p0, p1, r, seg=10):
    a, b = Vector(p0), Vector(p1); d = b - a; q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=d.length, matrix=Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4())
body = empty('Body', (0, 0, 0))
bm = B = None
bm = bmesh.new()
sweep(bm, [(-2.5, 1.5, .25, .3), (-2.38, 1.52, .95, .95), (-2.05, 1.6, 1.4, 1.45), (-1.5, 1.68, 1.62, 1.72), (-.5, 1.74, 1.68, 1.84), (.6, 1.8, 1.66, 1.8),
           (1.25, 1.96, 1.3, 1.42), (1.85, 2.16, .82, .86), (2.6, 2.3, .52, .52), (5.9, 2.45, .34, .36), (6.3, 2.48, .3, .32)], 16, 2.3)
for f in bm.faces:
    c = f.calc_center_median(); nrm = f.normal; m = 0
    if c.y < -1.15 and c.z > 1.42 and c.y > -2.42: m = 1                                     # wrap-round windscreen and chin windows
    elif c.y < -1.75 and 1.0 < c.z <= 1.42: m = 1
    elif abs(nrm.x) > .55 and -1.25 < c.y < .85 and 1.55 < c.z < 2.4 and not (-.45 < c.y < -.3): m = 1   # cabin side windows
    elif abs(nrm.x) > .55 and -.45 < c.y < -.3 and c.z > 1.0: m = 2                           # door shut line
    elif c.y > 2.7 and abs(nrm.x) > .5 and 2.3 < c.z < 2.55: m = 3                            # stripe along the boom
    f.material_index = m
cab = mk('cabin', bm, ['Paint', 'Glass', 'Black', 'Stripe'], body, subsurf=1)
bm = bmesh.new(); sweep(bm, [(-.4, 2.62, .5, .2), (-.2, 2.72, 1.0, .45), (1.4, 2.72, 1.0, .45), (1.9, 2.6, .5, .25)], 12, 2.6); mk('cowl', bm, 'Paint', body, subsurf=1)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=.12, radius2=.12, depth=.45, matrix=Matrix.Translation((0, .3, 3.15))); mk('mast', bm, 'Black', body)
# fenestron shroud, fin, stabiliser with end plates
bm = bmesh.new()
segs = 20; R0, R1, T = .5, .72, .26
for k in range(segs):
    a0, a1 = k / segs * math.tau, (k + 1) / segs * math.tau
    P = lambda r, a, x: Vector((x, 6.55 + math.cos(a) * r, 2.5 + math.sin(a) * r))
    for q in ((P(R0, a0, -T / 2), P(R0, a1, -T / 2), P(R0, a1, T / 2), P(R0, a0, T / 2)), (P(R1, a1, -T / 2), P(R1, a0, -T / 2), P(R1, a0, T / 2), P(R1, a1, T / 2)),
              (P(R0, a1, -T / 2), P(R0, a0, -T / 2), P(R1, a0, -T / 2), P(R1, a1, -T / 2)), (P(R0, a0, T / 2), P(R0, a1, T / 2), P(R1, a1, T / 2), P(R1, a0, T / 2))):
        bm.faces.new([bm.verts.new(v) for v in q])
box(bm, (0, 6.75, 3.35), (.12, .75, 1.2), rx=-.35); box(bm, (0, 5.45, 2.5), (1.9, .45, .07))
for sx in (-1, 1): box(bm, (sx * .95, 5.5, 2.62), (.05, .5, .5))
mk('tail', bm, 'Paint', body, smooth=False)
bm = bmesh.new()   # skids
for sx in (-1, 1):
    tube(bm, (sx * 1.05, -1.55, .08), (sx * 1.05, 1.6, .08), .045); tube(bm, (sx * 1.05, -1.55, .08), (sx * 1.05, -1.95, .28), .045)
    for y in (-.8, .8): tube(bm, (sx * 1.05, y, .08), (sx * .55, y, .95), .045)
for y in (-.8, .8): tube(bm, (-.6, y, .95), (.6, y, .95), .045)
mk('skids', bm, 'Chrome', body)
bm = bmesh.new(); box(bm, (0, -1.9, .95), (.3, .2, .08)); mk('landing', bm, 'LightF', body)
bm = bmesh.new(); box(bm, (-1.0, 5.5, 2.62), (.06, .12, .08)); box(bm, (0, 6.9, 3.95), (.1, .1, .1)); mk('navR', bm, 'LightR', body)
bm = bmesh.new(); box(bm, (1.0, 5.5, 2.62), (.06, .12, .08)); mk('navG', bm, 'Amber', body)
# main rotor: four drooping blades on a hub
rotor = empty('Rotor', (0, .3, 3.4))
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=.28, radius2=.16, depth=.22, matrix=Matrix.Translation((0, .3, 3.4)))
mk('hub', bm, 'Black', rotor, offset=(0, .3, 3.4))
bm = bmesh.new()
for k in range(4):
    a = k / 4 * math.tau + .3; ca, sa = math.cos(a), math.sin(a)
    for j in range(10):
        r0, r1 = .25 + j * .5, .25 + (j + 1) * .5; d0, d1 = -.004 * r0 * r0, -.004 * r1 * r1
        q = [(r0, -.15, d0), (r1, -.14, d1), (r1, .14, d1), (r0, .15, d0)]
        pts = [Vector((ca * r - sa * w, .3 + sa * r + ca * w, 3.42 + dz)) for r, w, dz in q]
        top = [bm.verts.new(v + Vector((0, 0, .02))) for v in pts]; bot = [bm.verts.new(v - Vector((0, 0, .02))) for v in pts]
        bm.faces.new(top); bm.faces.new(bot[::-1])
        for i in range(4): bm.faces.new((bot[i], bot[(i + 1) % 4], top[(i + 1) % 4], top[i]))
mk('blades', bm, 'Blade', rotor, smooth=False, offset=(0, .3, 3.4))
# fenestron fan
tr = empty('TailRotor', (0, 6.55, 2.5))
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=.12, radius2=.12, depth=.14, matrix=Matrix.Translation((0, 6.55, 2.5)) @ Matrix.Rotation(math.pi / 2, 4, 'Y'))
for k in range(8):
    a = k / 8 * math.tau; box(bm, (0, 6.55 + math.cos(a) * .3, 2.5 + math.sin(a) * .3), (.03, .1, .42)) if False else None
    bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation((0, 6.55, 2.5)) @ Matrix.Rotation(a, 4, 'X') @ Matrix.Translation((0, 0, .3)) @ Matrix.Rotation(.5, 4, 'Z') @ Matrix.Diagonal((.02, .09, .4, 1)))
mk('fan', bm, 'Blade', tr, smooth=False, offset=(0, 6.55, 2.5))
out = os.path.join(ROOT, 'assets', 'cars', 'heli.glb')
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_yup=True, export_apply=True)
print('exported', out, sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH'))
