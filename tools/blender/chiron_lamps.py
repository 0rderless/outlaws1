"""Quad-LED headlamps for chiron.py (exec'd inside its per-side loop, sharing its globals; sx = -1 or 1).
on_front(x, z, off) ray-casts onto the finished front surface (after the recesses in chiron_recess.py are cut)."""
hc = [(sx * (.495 + .3 * k / 12), .642 + .022 * (k / 12)) for k in range(13)]
for k in range(4):
    x, z = hc[k * 4]
    def led(bm, x=x, z=z):
        p, nrm = on_front(x, z, .012); q = Vector((0, 0, 1)).rotation_difference(nrm)
        bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=.033, radius2=.028, depth=.02, matrix=Matrix.Translation(p) @ q.to_matrix().to_4x4())
    prim('led', 'LightF', led)
    def ring_(bm, x=x, z=z):
        p, nrm = on_front(x, z, .007); q = Vector((0, 0, 1)).rotation_difference(nrm)
        bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=.042, radius2=.042, depth=.008, matrix=Matrix.Translation(p) @ q.to_matrix().to_4x4())
    prim('ledring', 'Chrome', ring_)
