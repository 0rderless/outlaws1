"""Headlamp recesses for chiron.py (exec'd inside it, sharing its globals).
Runs after the body is subdivided and the wheel arches are cut, before the glass insets.
1. The front of each fender is raised a little over the lamp row (the bodywork must stand above the slot to overhang it
   like an eyebrow); the lift fades out toward the hood valley, the side and the rear.
2. Each front corner gets a long horizontal slot carved with a BOOLEAN DIFFERENCE: a sharp upper edge (the ceiling
   runs straight in, slightly undercut), a softer chamfered lower lip, a flat floor ~.05 m deep for the four lamps,
   a rounded outer end that wraps a little round the corner, and an inner channel tapering to a point under the
   bonnet edge. The cavity faces take the 'Black' material.
Contract with chiron_lamps.py: lamp centres |x| = .52 .605 .69 .775, z = .655; the slot encloses them with >= .015 margin."""
# ------------------------------------------------------------------ 1. raise the fender fronts over the lamps
RC_LIFT = pchip([(.27, 0), (.33, .01), (.36, .03), (.39, .058), (.42, .08), (.45, .084), (.50, .08), (.55, .072), (.60, .056), (.65, .044),
                 (.70, .036), (.76, .033), (.82, .036), (.88, .033), (.93, .015), (1.0, 0)])
for v in me.vertices:
    x, y, z = v.co
    a = RC_LIFT(abs(x))
    if a <= 0 or y > -1.3 or z < .48: continue
    v.co.z = z + a * (1 - sm(-2.12, -1.38, y)) * sm(.48, .62, z)
me.update()
# ------------------------------------------------------------------ 2. the slot outline (front view |x|, z) as columns
RC_TOP, RC_BOT = .707, .603                                # ceiling / lip heights along the lamps
RC_XI, RC_ZI = .385, .638                                  # inner tip, under the bonnet edge
RC_XO = .855                                               # outer extreme (wraps round the corner)
RC_D = .052                                                # floor depth behind the face (at mid height)
RC_ZT = pchip([(RC_XI, RC_ZI), (.41, .658), (.44, .681), (.47, .699), (.50, RC_TOP)])   # inner channel: ceiling sweeps down
RC_ZB = pchip([(RC_XI, RC_ZI), (.41, .622), (.44, .609), (.465, RC_BOT)])              # ... and the lip rises to the tip
def rc_columns():
    cols = []
    xa = .50                                                 # inner channel: tip -> first lamp
    for k in range(14):
        u = k / 14; x = lerp(RC_XI, xa, 1 - (1 - u) ** 1.4)
        cols.append((x, RC_ZT(x), RC_ZB(x), (x - RC_XI) / (xa - RC_XI)))
    xb = RC_XO - .05                                         # straight run under the lamps (lip dips very slightly in the middle)
    for k in range(12):
        u = k / 12; x = lerp(xa, xb, u)
        cols.append((x, RC_TOP + .002 * u, RC_BOT - .003 * math.sin(math.pi * u), 1.0))
    zm = (RC_TOP + .002 + RC_BOT) / 2; hh = (RC_TOP + .002 - RC_BOT) / 2
    for k in range(13):                                      # rounded outer end: elliptical cap, centre (xb, zm)
        th = math.pi / 2 * k / 12
        x = xb + (RC_XO - xb) * math.sin(th); h = hh * math.cos(th) ** .85
        cols.append((x, zm + h, zm - h, 1.0))
    return cols
rc_bm = bmesh.new(); rc_bm.from_mesh(me); rc_bvh = BVHTree.FromBMesh(rc_bm); rc_bm.free()
def rc_hit(x, z):
    loc, nrm, _, _ = rc_bvh.ray_cast(Vector((x, -L / 2 - 1, z)), Vector((0, 1, 0)), 10)
    if loc is None: loc, nrm, _, _ = rc_bvh.find_nearest(Vector((x, -L / 2, z)))
    return loc, nrm
def rc_sections():
    """cross-sections (at +x) of the cutter, one per column: [outside@ceiling, ceiling back, floor bottom, outside@lip]"""
    cols = rc_columns(); dirs = []
    for x, zt, zb, w in cols:                                # into the body: horizontal, between the face normal and +y
        zmid = (zt + zb) / 2; t = rc_hit(x + .02, zmid)[0] - rc_hit(x - .02, zmid)[0]
        dirs.append(Vector((-t.y, t.x, 0)).normalized().lerp(Vector((0, 1, 0)), .45).normalized())
    for _ in range(3): dirs = [(dirs[max(0, i - 1)] + dirs[i] * 2 + dirs[min(len(dirs) - 1, i + 1)]).normalized() for i in range(len(dirs))]
    secs = []
    for i, ((x, zt, zb, w), d) in enumerate(zip(cols, dirs)):
        zmid = (zt + zb) / 2; hgt = zt - zb
        pm = rc_hit(x, zmid)[0]; pt = rc_hit(x, zt)[0]; pb = rc_hit(x, zb)[0]
        if abs(pt.y - pm.y) > .04: print('recess: ceiling misses the face at', round(x, 3)); pt = pm.copy()
        if abs(pb.y - pm.y) > .04: print('recess: lip misses the face at', round(x, 3)); pb = pm.copy()
        D = RC_D * (.45 + .55 * w)                           # the channel gets shallower toward the tip
        if i == 0 or i == len(cols) - 1:                     # the tip / the outer end close on an edge
            secs.append([pm - d * .05, pm + d * D * .5]); continue
        C = pm + d * D; C.z = zt + .07 * hgt                 # ceiling runs straight in, slightly undercut -> sharp eyebrow
        F = pm + d * D; F.z = zb + .30 * hgt                 # flat floor down to the chamfered lip
        St = pt.copy(); St.z = zt; Sb = pb.copy(); Sb.z = zb
        def ext(S, T):                                       # continue the line T -> S outward by .05 m (horizontally)
            u = S - T; hl = Vector((u.x, u.y, 0)).length; return S + u * (.05 / max(hl, 1e-4))
        secs.append([ext(St, C), C, F, ext(Sb, F)])
    return secs
def rc_cutter(bm, sx):
    V = []
    for sec in rc_sections():
        vs = [bm.verts.new(Vector((sx * p.x, p.y, p.z))) for p in sec]
        V.append([vs[0], vs[1], vs[1], vs[0]] if len(vs) == 2 else vs)
    for i in range(len(V) - 1):
        A_, B_ = V[i], V[i + 1]
        for q in range(4):
            vs = []
            for v in (A_[q], A_[(q + 1) % 4], B_[(q + 1) % 4], B_[q]):
                if v not in vs: vs.append(v)
            if len(vs) >= 3: bm.faces.new(vs)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
rc_cut = prim('recesscut', 'Black', lambda bm: [rc_cutter(bm, sx) for sx in (-1, 1)], smooth=True)
mo = body.modifiers.new('recess', 'BOOLEAN'); mo.object = rc_cut; mo.operation = 'DIFFERENCE'; mo.solver = 'EXACT'; mo.material_mode = 'TRANSFER'
bpy.context.view_layer.objects.active = body; bpy.ops.object.modifier_apply(modifier=mo.name); bpy.data.objects.remove(rc_cut)
