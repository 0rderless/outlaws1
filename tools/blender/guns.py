import bpy, bmesh, math, sys
from mathutils import Matrix, Vector
OUT=sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
def hexc(h): h=h.lstrip('#'); c=[int(h[i:i+2],16)/255 for i in (0,2,4)]; return [x/12.92 if x<=0.04045 else ((x+0.055)/1.055)**2.4 for x in c]+[1]
M={}
def mat(n,c,r,m):
    X=bpy.data.materials.new(n); X.use_nodes=True; b=X.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=hexc(c); b.inputs['Roughness'].default_value=r; b.inputs['Metallic'].default_value=m; M[n]=X
mat('GunMetal','#1c1d20',0.35,0.9); mat('Polymer','#121314',0.6,0); mat('Wood','#5a3519',0.55,0); mat('Steel','#5d6066',0.3,1)
def part(gun,matn,build,bev=0.004):
    bm=bmesh.new(); build(bm); me=bpy.data.meshes.new('p'); bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new(gun+'_p',me); bpy.context.scene.collection.objects.link(o); me.materials.append(M[matn])
    if bev:
        m=o.modifiers.new('b','BEVEL'); m.width=bev; m.segments=2; bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=m.name)
    o['gun']=gun; return o
def box(c,s,rx=0):
    return lambda bm: bmesh.ops.create_cube(bm,size=1,matrix=Matrix.Translation(Vector(c))@Matrix.Rotation(rx,4,'X')@Matrix.Diagonal((s[0],s[1],s[2],1)))
def cyl(c,r,d,seg=16):  # along Y (barrel axis); -Y is the muzzle direction
    return lambda bm: bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=r,radius2=r,depth=d,matrix=Matrix.Translation(Vector(c))@Matrix.Rotation(math.pi/2,4,'X'))
# Pistol (origin at grip, muzzle toward -Y)
part('pistol','GunMetal',box((0,-0.07,0.045),(0.03,0.2,0.032)))
part('pistol','Polymer',box((0,-0.065,0.017),(0.027,0.17,0.026)))
part('pistol','Polymer',box((0,0.0,-0.035),(0.029,0.05,0.11),rx=-0.28))
part('pistol','Polymer',box((0,-0.045,-0.012),(0.008,0.05,0.004)))
part('pistol','Steel',cyl((0,-0.172,0.045),0.007,0.01,10),0)
for k in range(5): part('pistol','Steel',box((0,-0.0+0.012*k-0.01,0.062),(0.031,0.004,0.004)),0)
# SMG
part('smg','GunMetal',box((0,-0.11,0.04),(0.045,0.3,0.06)))
part('smg','Steel',cyl((0,-0.3,0.045),0.011,0.1,12),0)
part('smg','Polymer',box((0,-0.14,-0.07),(0.028,0.045,0.16),rx=0.12))
part('smg','Polymer',box((0,0.0,-0.035),(0.03,0.045,0.1),rx=-0.25))
part('smg','Steel',box((0.022,0.13,0.035),(0.008,0.24,0.012)),0); part('smg','Steel',box((-0.022,0.13,0.035),(0.008,0.24,0.012)),0)
part('smg','Polymer',box((0,0.25,0.02),(0.05,0.02,0.07)))
part('smg','Steel',box((0,-0.05,0.085),(0.012,0.04,0.02)),0)
# Shotgun (pump)
part('shotgun','Steel',cyl((0,-0.33,0.05),0.016,0.62,16),0)
part('shotgun','Steel',cyl((0,-0.28,0.022),0.014,0.5,12),0)
part('shotgun','Wood',cyl((0,-0.3,0.024),0.028,0.2,14))
part('shotgun','GunMetal',box((0,-0.0,0.035),(0.045,0.2,0.07)))
part('shotgun','Wood',box((0,0.24,-0.005),(0.04,0.34,0.09),rx=0.1))
part('shotgun','Wood',box((0,0.09,-0.04),(0.034,0.05,0.09),rx=-0.3))
part('shotgun','Polymer',box((0,0.41,-0.02),(0.042,0.02,0.11),rx=0.1))
for g in ('pistol','smg','shotgun'):
    objs=[o for o in bpy.data.objects if o.get('gun')==g]
    for o in bpy.data.objects: o.select_set(False)
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]; bpy.ops.object.join(); bpy.context.view_layer.objects.active.name=g
bpy.ops.export_scene.gltf(filepath=OUT,export_format='GLB',export_yup=True); print('exported guns')
