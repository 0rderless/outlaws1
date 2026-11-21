"""London Routemaster (long version) -> assets/cars/bus.glb.   python3 -I bus.py
Body = horizontal slices of rounded rectangles lofted together (domed roof), so every window, the cream band and the
destination blind are bands of faces; glass is recessed with insets. The open rear platform is a boolean cut.
Blender axes: x side (offside/driver = -x), y length (front at -y), z up."""
import bpy, bmesh, math, os, sys
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
for a in (('BusRed', '#ffffff', .32, .15), ('Glass', '#0e1419', .05), ('Cream', '#efe2c0', .45), ('Black', '#121314', .55), ('Under', '#0b0b0c', .9),
          ('Chrome', '#d9dde2', .12, 1.0), ('Interior', '#3a3530', .8), ('Seat', '#5a2026', .9), ('Grille', '#0c0d0e', .6), ('PlateF', '#f4f4f0', .4),
          ('PlateR', '#f2c200', .4), ('Blind', '#0a0a0a', .6), ('Floor', '#4a4038', .9)): mat(*a)
mat('LightF', '#f6f3ea', .05, 0, '#fff6e0', 1.5); mat('LightR', '#a50d12', .15, 0, '#ff1a1a', 1.2); mat('Amber', '#d27a0f', .2, 0, '#ff8a00', .6); mat('BlindText', '#f4f1e6', .4, 0, '#fff4d8', 1.0)
L, W, H = 9.1, 2.44, 4.38; Lh, Wh = L / 2, W / 2; R = .5
YF, YR = -Lh + 1.0, -Lh + 1.0 + 5.49          # axles: front -3.55, rear +1.94
# ------------------------------------------------------------------ slices: (z, half length, half width, front corner r, rear corner r)
SL = [(.40, Lh - .04, Wh - .03, .30, .50), (.52, Lh, Wh, .30, .55), (1.05, Lh, Wh, .30, .58), (1.08, Lh, Wh, .30, .58), (1.92, Lh, Wh, .30, .58), (1.96, Lh, Wh, .30, .58),
      (2.12, Lh, Wh, .32, .60), (2.40, Lh, Wh, .32, .60), (2.62, Lh - .01, Wh - .005, .34, .62), (3.50, Lh - .03, Wh - .02, .38, .66),
      (3.62, Lh - .05, Wh - .035, .42, .70), (3.86, Lh - .12, Wh - .08, .55, .80), (4.06, Lh - .26, Wh - .17, .75, .95), (4.22, Lh - .50, Wh - .34, 1.0, 1.1),
      (4.33, Lh - .85, Wh - .62, 1.0, 1.0), (4.38, Lh - 1.3, Wh - .95, .2, .2)]
# straight-side stations (fractions of the straight run) chosen so window/pillar edges fall on vertices
UP = [-4.20 + k * (8.35 / 6) for k in range(7)]                         # upper deck bays
LO = [-2.75 + k * (5.40 / 5) for k in range(6)] + [4.25]                 # lower deck bays (+ offside staircase window)
side_y = sorted(set([round(v, 3) for v in UP + LO + [u + d for u in UP + LO for d in (-.07, .07)] + [-4.2, -3.0, 2.8, 4.2] + [-4.1 + i * .35 for i in range(25)]]))
front_x = sorted(set([-1.1, -.95, -.2, -.05, .05, .6, .8, 1.06, -1.06, .3, -.3, -.6, -.8, 0.0, .95]))
def perim(Lh_, Wh_, rf, rr):
    """points around a rounded rectangle, starting at the front centre, going toward +x (nearside), fixed count"""
    pts = []
    xs = [x for x in front_x if x >= 0]                                  # front edge, centre -> nearside corner start
    for x in xs: pts.append((min(x, Wh_ - rf) if x < Wh_ - rf else Wh_ - rf - .001, -Lh_))
    for k in range(1, 8): a = -math.pi / 2 + k / 8 * math.pi / 2; pts.append((Wh_ - rf + math.cos(a) * rf, -Lh_ + rf + math.sin(a) * rf))
    y0, y1 = -Lh_ + rf, Lh_ - rr
    for y in side_y: pts.append((Wh_, y0 + (y1 - y0) * ((y - side_y[0]) / (side_y[-1] - side_y[0]))))
    for k in range(1, 8): a = k / 8 * math.pi / 2; pts.append((Wh_ - rr + math.cos(a) * rr, Lh_ - rr + math.sin(a) * rr))
    for x in sorted([x for x in front_x if x >= 0], reverse=True): pts.append((min(x, Wh_ - rr - .001), Lh_))
    half = pts
    mirror = [(-x, y) for x, y in reversed(half[1:-1])]
    return half + mirror
bm = bmesh.new(); rings = []
for z, lh, wh, rf, rr in SL:
    rings.append([bm.verts.new((x, y, z)) for x, y in perim(lh, wh, rf, rr)])
n = len(rings[0])
for i in range(len(rings) - 1):
    for k in range(n): bm.faces.new((rings[i][k], rings[i][(k + 1) % n], rings[i + 1][(k + 1) % n], rings[i + 1][k]))
bm.faces.new(rings[-1]); bm.faces.new(rings[0][::-1])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
# ------------------------------------------------------------------ classify faces
def bays(y, edges, pil=.07): return any(edges[k] + pil < y < edges[k + 1] - pil for k in range(len(edges) - 1))
ORDER = ['BusRed', 'Glass', 'Cream', 'Black', 'Under', 'Blind', 'BlindText', 'Interior']
for f in bm.faces:
    c = f.calc_center_median(); nr = f.normal; m = 'BusRed'
    side, front, rear = abs(nr.x) > .65, nr.y < -.65, nr.y > .65
    if c.z < .45 and abs(nr.z) > .6: m = 'Under'
    elif 2.12 < c.z < 2.40:
        m = 'Blind' if (front and abs(c.x) < .82) or (side and c.x > 0 and 2.9 < c.y < 4.1) else 'Cream'
    elif side and 2.62 < c.z < 3.50 and bays(c.y, UP): m = 'Glass'
    elif side and 1.08 < c.z < 1.92 and (bays(c.y, LO[:6]) or (c.x < 0 and 2.82 < c.y < 4.18)): m = 'Glass'
    elif side and c.x < 0 and 1.08 < c.z < 1.92 and -4.15 < c.y < -3.07: m = 'Glass'                       # cab door window (driver on the offside)
    elif front and 2.62 < c.z < 3.50 and .05 < abs(c.x) < 1.04: m = 'Glass'
    elif front and 1.08 < c.z < 1.92 and -1.06 < c.x < -.22: m = 'Glass'                                       # driver's windscreen
    elif rear and 2.70 < c.z < 3.45 and abs(c.x) < .62: m = 'Glass'
    elif rear and 1.08 < c.z < 1.92 and c.x < -.1 and abs(c.x) < .8: m = 'Glass'
    f.material_index = ORDER.index(m)
# recessed glass and blind
for names, th, dp, rim in ((('Glass',), .02, -.03, 'Black'), (('Blind',), .015, -.04, 'Black')):
    fs = [f for f in bm.faces if ORDER[f.material_index] in names]
    r = bmesh.ops.inset_region(bm, faces=fs, thickness=th, depth=dp, use_even_offset=True)
    for f in r['faces']: f.material_index = ORDER.index(rim)
me = bpy.data.meshes.new('Body'); bm.to_mesh(me); bm.free()
body = bpy.data.objects.new('Body', me); bpy.context.scene.collection.objects.link(body)
for nm in ORDER: me.materials.append(M[nm])
for p in me.polygons: p.use_smooth = True
def prim(name, mname, build, smooth=True):
    bm = bmesh.new(); build(bm); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); me.materials.append(M[mname])
    for p in me.polygons: p.use_smooth = smooth
    return o
def cube(bm, c, s, rx=0.0, bev=0.0):
    r = bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation(Vector(c)) @ Matrix.Rotation(rx, 4, 'X') @ Matrix.Diagonal((s[0], s[1], s[2], 1)))
    if bev: bmesh.ops.bevel(bm, geom=[e for e in bm.edges if all(v in r['verts'] for v in e.verts)], offset=bev, segments=2, affect='EDGES', profile=.5)
def cyl(bm, c, r, depth, axis='X', seg=20):
    rot = {'X': Matrix.Rotation(math.pi / 2, 4, 'Y'), 'Y': Matrix.Rotation(math.pi / 2, 4, 'X'), 'Z': Matrix.Identity(4)}[axis]
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=depth, matrix=Matrix.Translation(Vector(c)) @ rot)
def boolean(cutter):
    mo = body.modifiers.new('b', 'BOOLEAN'); mo.object = cutter; mo.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = body; bpy.ops.object.modifier_apply(modifier=mo.name); bpy.data.objects.remove(cutter)
for wy in (YF, YR): boolean(prim('cut', 'Under', lambda bm, wy=wy: cyl(bm, (0, wy, R), R + .1, W + .6, 'X', 36)))
boolean(prim('platform', 'Interior', lambda bm: cube(bm, (.78, 3.7, 1.18), (1.0, 1.9, 1.56))))           # open rear platform, nearside
# ------------------------------------------------------------------ interior: floors, seats, stairs
prim('floors', 'Floor', lambda bm: (cube(bm, (0, 0, .5), (W - .12, L - .3, .06)), cube(bm, (0, 0, 2.3), (W - .1, L - .25, .14))))
def seats(bm):
    for y in [-2.55 + i * .76 for i in range(7)]:
        for sx in (-1, 1): cube(bm, (sx * .68, y, .78), (.86, .44, .12), bev=.03); cube(bm, (sx * .68, y + .22, 1.05), (.86, .08, .5), bev=.03)
    for y in [-4.0 + i * .74 for i in range(11)]:
        for sx in (-1, 1): cube(bm, (sx * .68, y, 2.6), (.86, .44, .12), bev=.03); cube(bm, (sx * .68, y + .22, 2.86), (.86, .08, .48), bev=.03)
prim('seats', 'Seat', seats)
def stairs(bm):
    for k in range(9): cube(bm, (-.25, 3.0 + k * .16, .55 + k * .2), (.8, .3, .06))
prim('stairs', 'Interior', stairs)
prim('pole', 'Chrome', lambda bm: cyl(bm, (1.12, 4.45, 1.2), .025, 1.6, 'Z', 12))
prim('cab', 'Interior', lambda bm: cube(bm, (-.62, -3.75, 1.3), (1.0, .8, .06)))   # cab bulkhead shelf
# ------------------------------------------------------------------ front: grille, lamps, bumper, plate, mirrors
fy = -Lh
prim('grillef', 'Chrome', lambda bm: cube(bm, (.12, fy - .03, 1.02), (.64, .06, .74), bev=.04))
def slats(bm):
    for k in range(11): cube(bm, (.12 - .26 + k * .052, fy - .07, 1.02), (.022, .03, .64))
prim('slats', 'Grille', slats)
for sx in (-1, 1):
    prim('bezel', 'Chrome', lambda bm, sx=sx: cyl(bm, (sx * .94, fy - .05, .98), .13, .08, 'Y', 28))
    prim('lamp', 'LightF', lambda bm, sx=sx: cyl(bm, (sx * .94, fy - .09, .98), .11, .02, 'Y', 28))
    prim('side', 'LightF', lambda bm, sx=sx: cyl(bm, (sx * .94, fy - .03, 1.32), .05, .05, 'Y', 16))
    prim('ind', 'Amber', lambda bm, sx=sx: cube(bm, (sx * 1.1, fy - .02, 1.32), (.08, .04, .08), bev=.015))
    prim('arm', 'Black', lambda bm, sx=sx: cube(bm, (sx * (Wh + .18), fy + .25, 1.95), (.36, .03, .03)))
    prim('mirror', 'Black', lambda bm, sx=sx: cube(bm, (sx * (Wh + .36), fy + .25, 1.8), (.06, .16, .3), bev=.02))
    prim('tail', 'LightR', lambda bm, sx=sx: cube(bm, (sx * 1.08, Lh + .01, .95), (.1, .04, .32), bev=.02))
prim('bumper', 'Black', lambda bm: cube(bm, (0, fy - .06, .55), (W - .06, .1, .12), bev=.03))
prim('plateF', 'PlateF', lambda bm: cube(bm, (.12, fy - .12, .55), (.52, .02, .11)))
prim('plateR', 'PlateR', lambda bm: cube(bm, (-.55, Lh + .03, .78), (.52, .02, .11)))
prim('bumperR', 'Black', lambda bm: cube(bm, (-.55, Lh + .0, .5), (1.2, .1, .1), bev=.03))
# destination blinds (white lettering suggested by lit strips)
def blind(bm):
    cube(bm, (-.18, fy - .012, 2.30), (1.05, .01, .1)); cube(bm, (.55, fy - .012, 2.30), (.22, .01, .12))
    cube(bm, (Wh + .002, 3.5, 2.30), (.01, .9, .09))
prim('blindtext', 'BlindText', blind)
# mudguards over the wheels
for wy in (YF, YR):
    def guard(bm, wy=wy):
        for sx in (-1, 1):
            segs = 16; vs = []
            for j in range(segs + 1):
                a = math.radians(-5) + math.radians(190) * j / segs; ca, sa = math.cos(a), math.sin(a)
                vs.append([bm.verts.new((sx * Wh + sx * dx, wy + ca * (R + .1 + dr), R + sa * (R + .1 + dr))) for dx, dr in ((-.01, 0), (.03, 0), (.03, .05), (-.01, .05))])
            for j in range(segs):
                for q in range(4): bm.faces.new((vs[j][q], vs[j][(q + 1) % 4], vs[j + 1][(q + 1) % 4], vs[j + 1][q]))
    prim('guard', 'Black', guard)
    prim('liner', 'Under', lambda bm, wy=wy: cyl(bm, (0, wy, R + .05), R + .09, W - .14, 'X', 28))
for k in range(3): prim('vent', 'BusRed', lambda bm, k=k: cube(bm, (0, -2.5 + k * 2.4, 4.37), (.5, .3, .05), bev=.02))
objs = [o for o in bpy.data.objects if o.type == 'MESH']
for o in objs: o.select_set(True)
bpy.context.view_layer.objects.active = body; bpy.ops.object.join()
bus = bpy.context.view_layer.objects.active; bus.name = 'bus'
try: bus.data.set_sharp_from_angle(angle=math.radians(40))
except Exception: pass
out = os.path.join(ROOT, 'assets', 'cars', 'bus.glb')
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_apply=True, export_yup=True)
print('exported', out, sum(len(pl.vertices) - 2 for pl in bus.data.polygons), 'tris')
