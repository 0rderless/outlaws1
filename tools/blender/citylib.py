"""Shared mesh-building helpers for the Blender city/prop scripts.
Geometry is authored in game space (x east, y up, z south) and converted to Blender space (x, -z, y) on output."""
import bpy, bmesh, math, json, os
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
LAYERS = [l['name'] for l in json.load(open(os.path.join(ROOT, 'assets', 'city', 'layers.json')))['layers']]
LI = {n: i for i, n in enumerate(LAYERS)}
UVS = {'brick': 2.4, 'stone': 3, 'paint': 2.5, 'slate': 2, 'asphalt': 6, 'road': 14, 'roadring': 18, 'pavement': 2.4, 'kerb': 2, 'grass': 5, 'gravel': 3, 'bark': 1.2, 'leaves': 2.2, 'metal': 1.5,
       'concrete': 4, 'wood': 1.2, 'zebra': 2.4, 'gold': 1, 'steel': 1.5, 'redasphalt': 6, 'clock': 1, 'ads': 1, 'sandstone': 4.5, 'lampglass': 1, 'signal': 1, 'leather': 1}
def hexc(h):
    if not isinstance(h, str): return h
    h = h.lstrip('#')
    if len(h) == 3: h = ''.join(ch * 2 for ch in h)
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)
WHITE = (1, 1, 1)
class Acc:
    """Accumulates quads/tris with per-face layer, per-loop uv and colour."""
    def __init__(self): self.V = []; self.F = []; self.UV = []; self.C = []; self.M = []
    def face(self, pts, layer, tint=WHITE, uvs=None, ao=True, scale=None):
        layer_i = LI[layer] if isinstance(layer, str) else layer
        col = hexc(tint)
        if uvs is None:
            a, b, c = Vector(pts[0]), Vector(pts[1]), Vector(pts[2]); n = (b - a).cross(c - a)
            sc = scale or UVS.get(LAYERS[layer_i], 2)
            if n.length < 1e-12: n = Vector((0, 1, 0))
            n.normalize()
            if abs(n.y) > .7: uvs = [(p[0] / sc, -p[2] / sc) for p in pts]
            elif abs(n.x) > abs(n.z): uvs = [((-p[2] if n.x > 0 else p[2]) / sc, p[1] / sc) for p in pts]
            else: uvs = [((p[0] if n.z > 0 else -p[0]) / sc, p[1] / sc) for p in pts]
        base = len(self.V); self.V.extend(tuple(p) for p in pts); self.F.append(tuple(range(base, base + len(pts)))); self.M.append(layer_i)
        self.UV.extend(uvs)
        for p in pts:
            k = (.7 + .3 * min(1, max(0, p[1]) / 3.5)) if ao else 1
            self.C.append((col[0] * k, col[1] * k, col[2] * k, 1))
    def quad(self, a, b, c, d, layer, tint=WHITE, uvs=None, ao=True, scale=None): self.face([a, b, c, d], layer, tint, uvs, ao, scale)
    def box(self, x0, x1, y0, y1, z0, z1, layer, tint=WHITE, bottom=False, top=True, sides=(1, 1, 1, 1), ao=True, toplayer=None, scale=None):
        if sides[0]: self.quad((x1, y0, z1), (x1, y0, z0), (x1, y1, z0), (x1, y1, z1), layer, tint, ao=ao, scale=scale)   # +x
        if sides[1]: self.quad((x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0), layer, tint, ao=ao, scale=scale)   # -x
        if sides[2]: self.quad((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1), layer, tint, ao=ao, scale=scale)   # +z
        if sides[3]: self.quad((x1, y0, z0), (x0, y0, z0), (x0, y1, z0), (x1, y1, z0), layer, tint, ao=ao, scale=scale)   # -z
        if top: self.quad((x0, y1, z1), (x1, y1, z1), (x1, y1, z0), (x0, y1, z0), toplayer or layer, tint, ao=False, scale=scale)
        if bottom: self.quad((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1), layer, tint, ao=False, scale=scale)
    def cbox(self, cx, y0, cz, w, h, d, layer, tint=WHITE, **k): self.box(cx - w / 2, cx + w / 2, y0, y0 + h, cz - d / 2, cz + d / 2, layer, tint, **k)
    def cyl(self, cx, cz, r0, r1, y0, y1, seg, layer, tint=WHITE, cap=True, ry=0, scale=None):
        for i in range(seg):
            a0 = ry + i / seg * math.tau; a1 = ry + (i + 1) / seg * math.tau
            p = lambda a, r, y: (cx + math.sin(a) * r, y, cz + math.cos(a) * r)
            u0 = i / seg * (2 * math.pi * max(r0, r1)) / (scale or UVS.get(layer, 2)); u1 = (i + 1) / seg * (2 * math.pi * max(r0, r1)) / (scale or UVS.get(layer, 2))
            vs = (scale or UVS.get(layer, 2))
            self.quad(p(a0, r0, y0), p(a1, r0, y0), p(a1, r1, y1), p(a0, r1, y1), layer, tint, uvs=[(u0, y0 / vs), (u1, y0 / vs), (u1, y1 / vs), (u0, y1 / vs)])
        if cap and r1 > 1e-3:
            pts = [(cx + math.sin(ry - i / seg * math.tau) * r1, y1, cz + math.cos(ry - i / seg * math.tau) * r1) for i in range(seg)]
            self.face(pts, layer, tint, ao=False)
    def cone(self, cx, cz, r, y0, y1, seg, layer, tint=WHITE, ry=0):
        for i in range(seg):
            a0 = ry + i / seg * math.tau; a1 = ry + (i + 1) / seg * math.tau
            self.face([(cx + math.sin(a0) * r, y0, cz + math.cos(a0) * r), (cx + math.sin(a1) * r, y0, cz + math.cos(a1) * r), (cx, y1, cz)], layer, tint)
    def beam(self, p0, p1, w, layer, tint=WHITE, w2=None):
        p0, p1 = Vector(p0), Vector(p1); d = p1 - p0; L = d.length
        if L < 1e-6: return
        q = Vector((0, 1, 0)).rotation_difference(d.normalized()); M = Matrix.Translation((p0 + p1) / 2) @ q.to_matrix().to_4x4()
        hw, hd, hl = w / 2, (w2 or w) / 2, L / 2
        c = [M @ Vector((sx * hw, sy * hl, sz * hd)) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
        # indices: (sx,sy,sz) -> idx = (sx>0)*4+(sy>0)*2+(sz>0)
        f = [(4, 6, 7, 5), (0, 1, 3, 2), (1, 5, 7, 3), (0, 2, 6, 4), (2, 3, 7, 6), (0, 4, 5, 1)]
        for a, b, cc, dd in f: self.quad(tuple(c[a]), tuple(c[b]), tuple(c[cc]), tuple(c[dd]), layer, tint)
    def sphere(self, cx, cy, cz, r, layer, tint=WHITE, seg=10, rings=6, sy=1.0, half=False):
        pts = []
        for j in range(rings + 1):
            t = j / rings * (math.pi / 2 if half else math.pi); y = math.cos(t) * r * sy; rr = math.sin(t) * r
            pts.append([(cx + math.sin(i / seg * math.tau) * rr, cy + y, cz + math.cos(i / seg * math.tau) * rr) for i in range(seg)])
        for j in range(rings):
            for i in range(seg):
                a, b = pts[j][i], pts[j][(i + 1) % seg]; c, d = pts[j + 1][(i + 1) % seg], pts[j + 1][i]
                if j == 0: self.face([a, d, c], layer, tint)
                else: self.quad(a, d, c, b, layer, tint)
    def add_bm(self, bm, M, layer, tint=WHITE):
        for f in bm.faces:
            pts = [tuple(M @ v.co) for v in f.verts]; self.face(pts, layer, tint)
    def to_object(self, name, collection=None, glass=False):
        if not self.F: return None
        me = bpy.data.meshes.new(name)
        verts = [(v[0], -v[2], v[1]) for v in self.V]
        me.from_pydata(verts, [], self.F); me.update()
        uvl = me.uv_layers.new(name='UVMap'); ca = me.color_attributes.new('Col', 'FLOAT_COLOR', 'CORNER')
        # every face owns its own vertices, so loop i corresponds to vertex i
        uvl.data.foreach_set('uv', [c for uv in self.UV for c in uv])
        ca.data.foreach_set('color', [c for col in self.C for c in col])
        if glass:
            me.materials.append(get_mat('Glass'))
        else:
            used = sorted(set(self.M)); slot = {m: i for i, m in enumerate(used)}
            for m in used: me.materials.append(get_mat('L%d' % m))
            me.polygons.foreach_set('material_index', [slot[m] for m in self.M])
        ob = bpy.data.objects.new(name, me); (collection or bpy.context.scene.collection).objects.link(ob)
        return ob
MATS = {}
def get_mat(n):
    if n not in MATS:
        m = bpy.data.materials.new(n); m.use_nodes = True; MATS[n] = m
    return MATS[n]
def reset(): bpy.ops.wm.read_factory_settings(use_empty=True); MATS.clear()
def export(path, objs=None):
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', export_yup=True, export_vertex_color='ACTIVE', export_all_vertex_colors=False, export_materials='EXPORT', export_image_format='NONE')
