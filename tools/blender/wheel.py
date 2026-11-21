import bpy, bmesh, math, sys
from mathutils import Matrix, Vector
OUT=sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
def hexc(h): h=h.lstrip('#'); c=[int(h[i:i+2],16)/255 for i in (0,2,4)]; return [x/12.92 if x<=0.04045 else ((x+0.055)/1.055)**2.4 for x in c]+[1]
def mat(n,c,r,m):
    M=bpy.data.materials.new(n); M.use_nodes=True; b=M.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=hexc(c); b.inputs['Roughness'].default_value=r; b.inputs['Metallic'].default_value=m; return M
tyre=mat('Tyre','#141414',0.85,0); rim=mat('Rim','#b9bec4',0.25,1); hub=mat('Hub','#4a4d52',0.4,1)
bm=bmesh.new()
# tyre: lathe a rounded profile around X (radius 1, width 0.64)
prof=[(0.62,-0.30),(0.70,-0.33),(0.88,-0.33),(0.97,-0.29),(1.0,-0.2),(1.0,0.2),(0.97,0.29),(0.88,0.33),(0.70,0.33),(0.62,0.30)]
segs=40; rings=[]
for i in range(segs):
    a=i/segs*math.tau; rings.append([bm.verts.new((x,math.cos(a)*r,math.sin(a)*r)) for r,x in prof])
for i in range(segs):
    for k in range(len(prof)-1):
        bm.faces.new((rings[i][k],rings[i][k+1],rings[(i+1)%segs][k+1],rings[(i+1)%segs][k]))
me=bpy.data.meshes.new('tyre'); bm.to_mesh(me); bm.free(); t=bpy.data.objects.new('tyre',me); bpy.context.scene.collection.objects.link(t); me.materials.append(tyre)
for p in me.polygons: p.use_smooth=True
bm=bmesh.new()
bmesh.ops.create_cone(bm,cap_ends=True,segments=36,radius1=0.63,radius2=0.63,depth=0.5,matrix=Matrix.Rotation(math.pi/2,4,'Y'))
me=bpy.data.meshes.new('rim'); bm.to_mesh(me); bm.free(); r=bpy.data.objects.new('rim',me); bpy.context.scene.collection.objects.link(r); me.materials.append(hub)
bm=bmesh.new()
for side in (-1,1):
    bmesh.ops.create_cone(bm,cap_ends=True,segments=36,radius1=0.63,radius2=0.58,depth=0.05,matrix=Matrix.Translation((side*0.27,0,0))@Matrix.Rotation(math.pi/2,4,'Y'))
    for k in range(5):
        a=k/5*math.tau
        bmesh.ops.create_cube(bm,size=1,matrix=Matrix.Translation((side*0.3,math.cos(a)*0.33,math.sin(a)*0.33))@Matrix.Rotation(a,4,'X')@Matrix.Diagonal((0.05,0.5,0.13,1)))
    bmesh.ops.create_cone(bm,cap_ends=True,segments=16,radius1=0.17,radius2=0.12,depth=0.08,matrix=Matrix.Translation((side*0.31,0,0))@Matrix.Rotation(side*math.pi/2,4,'Y'))
me=bpy.data.meshes.new('spokes'); bm.to_mesh(me); bm.free(); sp=bpy.data.objects.new('spokes',me); bpy.context.scene.collection.objects.link(sp); me.materials.append(rim)
for p in me.polygons: p.use_smooth=False
for o in (t,r,sp): o.select_set(True)
bpy.context.view_layer.objects.active=t; bpy.ops.object.join()
bpy.ops.export_scene.gltf(filepath=OUT,export_format='GLB',export_yup=True); print('exported wheel')
