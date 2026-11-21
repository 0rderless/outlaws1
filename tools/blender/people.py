# Character builder: MakeHuman CC0 body + Mixamo rig, dressed with modelled clothes. Run: python3 -I people.py <variant> <out.glb>
import bpy, bmesh, json, sys, math, random
from mathutils import Vector, Matrix
MH='/tmp/claude-0/-home-user-boty/6b40efdf-8449-5f3a-8e84-e3c800719416/scratchpad/probe/mh/'
VARIANT=sys.argv[-2]; OUT=sys.argv[-1]
SPEC={
 'hero': dict(height=1.80, male=1.0, beard=True, skin='#4a3024', top='tank', topc='#121212', bottom='shorts', botc='#161616', shoes='#f2f2f2', sole='#1c1c1c', socks='#f5f5f5', hat='cap', hatc='#111111', hair='#0d0a08', chain=True),
 'man':  dict(height=1.78, male=1.0, skin='#c99a7a', top='tee', topc='#ffffff', bottom='jeans', botc='#ffffff', shoes='#ffffff', sole='#1c1c1c', socks=None, hat='hair', hatc='#ffffff', hair='#ffffff', chain=False),
 'woman':dict(height=1.66, male=-0.7, skin='#c99a7a', top='tee', topc='#ffffff', bottom='jeans', botc='#ffffff', shoes='#ffffff', sole='#1c1c1c', socks=None, hat='longhair', hatc='#ffffff', hair='#ffffff', chain=False),
 'cop':  dict(height=1.82, male=1.0, skin='#d2a184', top='cop', topc='#141a2a', bottom='trousers', botc='#141a2a', shoes='#0c0c0c', sole='#050505', socks=None, hat='helmet', hatc='#10142a', hair='#2a1d14', chain=False),
}[VARIANT]
GROUPV={}
def hexc(h,a=1.0):
    h=h.lstrip('#'); c=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return [x/12.92 if x<=0.04045 else ((x+0.055)/1.055)**2.4 for x in c]+[a]
def smooth(a,b,x): t=min(1,max(0,(x-a)/(b-a))); return t*t*(3-2*t)
def shape(x,y,z,S):
    # z-up metres; character faces -Y. Masculinise the neutral MakeHuman body.
    m=SPEC['male']
    sh=smooth(1.18,1.42,z)*(0.11 if m>0 else 0.06)*m; x*=1+sh                               # broader shoulders / upper back
    hip=(1-abs(z-0.93)/0.16) if abs(z-0.93)<0.16 else 0; x*=1-(0.09 if m>0 else 0.05)*hip*m   # narrower hips (wider when female)
    if m>0:
        wa=(1-abs(z-1.08)/0.13) if abs(z-1.08)<0.13 else 0; x*=1+0.09*wa*m; y*=1+0.07*wa*m            # thicker waist
        H=SPEC['height']; jz0,jz1=0.855*H,0.912*H
        if jz0<z<jz1 and abs(x)>0.015: k=math.sin((z-jz0)/(jz1-jz0)*math.pi); x*=1+0.09*k*m          # squarer jaw
        if 0.935*H<z<0.952*H and y<0: y-=0.004*m                                                   # brow ridge
    if 1.16<z<1.44 and y<-0.04 and 0.02<abs(x)<0.19:                     # flatten chest into pecs
        k=smooth(1.16,1.27,z)*(1-smooth(1.36,1.44,z))*smooth(0.02,0.07,abs(x))*(1-smooth(0.14,0.19,abs(x)))
        y+=(0.03 if m>0 else 0.02)*k*m
    return x,y,z
def load():
    V=[];VT=[];F=[];cur='none'
    for line in open(MH+'base.obj'):
        if line.startswith('v '): x,y,z=map(float,line.split()[1:4]); V.append([x,-z,y])
        elif line.startswith('vt '): VT.append(tuple(map(float,line.split()[1:3])))
        elif line.startswith('g '): cur=line.split()[1]
        elif line.startswith('f '):
            idx=[p.split('/') for p in line.split()[1:]]; F.append(([int(a[0])-1 for a in idx],[int(a[1])-1 for a in idx],cur))
    zmin=min(v[2] for v in V); zmax=max(v[2] for v in V if True)
    body_z=[V[i][2] for f in F if f[2]=='body' for i in f[0]]; zmin=min(body_z); zmax=max(body_z)
    S=SPEC['height']/(zmax-zmin)
    for v in V:
        v[0]*=S; v[1]*=S; v[2]=(v[2]-zmin)*S
        v[0],v[1],v[2]=shape(v[0],v[1],v[2],S)
    for vs,_,g in F: GROUPV.setdefault(g,set()).update(vs)
    return V,VT,F
def center(g,V):
    vs=GROUPV[g]; return sum((Vector(V[i]) for i in vs),Vector())/len(vs)
def mk_obj(name,me):
    ob=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(ob); return ob
def material(name,col,rough=.8,metal=0.0,vcol=False):
    m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=hexc(col); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    if vcol:
        n=m.node_tree.nodes.new('ShaderNodeVertexColor'); n.layer_name='Col'
        mix=m.node_tree.nodes.new('ShaderNodeMix'); mix.data_type='RGBA'; mix.blend_type='MULTIPLY'; mix.inputs['Factor'].default_value=1.0
        mix.inputs[6].default_value=hexc(col); m.node_tree.links.new(n.outputs['Color'],mix.inputs[7]); m.node_tree.links.new(mix.outputs[2],b.inputs['Base Color'])
    return m
bpy.ops.wm.read_factory_settings(use_empty=True)
V,VT,F=load()
body_faces=[f for f in F if f[2]=='body']
used=sorted({i for f in body_faces for i in f[0]}); remap={o:n for n,o in enumerate(used)}
me=bpy.data.meshes.new('body'); me.from_pydata([V[i] for i in used],[],[[remap[i] for i in f[0]] for f in body_faces]); me.update()
uv=me.uv_layers.new(name='UVMap')
for poly,f in zip(me.polygons,body_faces):
    for li,ti in zip(poly.loop_indices,f[1]): uv.data[li].uv=VT[ti]
body=mk_obj('Body',me)
# --- rig
rig=json.load(open(MH+'rig.mixamo.json'))['bones']
arm=bpy.data.armatures.new('Rig'); ao=mk_obj('Armature',arm)
bpy.context.view_layer.objects.active=ao; bpy.ops.object.mode_set(mode='EDIT')
def P(spec):
    idx=spec['vertex_indices'] if 'vertex_indices' in spec else GROUPV[spec['cube_name']]
    return sum((Vector(V[i]) for i in idx),Vector())/len(idx)
eb={}
for n,b in rig.items():
    e=arm.edit_bones.new(n); e.head=P(b['head']); e.tail=P(b['tail'])
    if (e.tail-e.head).length<1e-4: e.tail=e.head+Vector((0,0,.01))
    e.roll=b.get('roll',0.0); eb[n]=e
for n,b in rig.items():
    if b.get('parent'): eb[n].parent=eb[b['parent']]
J={n:(eb[n].head.copy()) for n in eb}
bpy.ops.object.mode_set(mode='OBJECT')
W=json.load(open(MH+'weights.mixamo.json'))['weights']
dom={}  # new vertex index -> (bone, weight)
for bone,lst in W.items():
    vg=body.vertex_groups.new(name=bone)
    for vi,wt in lst:
        if vi in remap:
            vg.add([remap[vi]],wt,'REPLACE')
            j=remap[vi]
            if wt>dom.get(j,('',0))[1]: dom[j]=(bone,wt)
def bone_of(i): return dom.get(i,('',0))[0].replace('mixamorig:','')
def thicken():
    if SPEC['male']<=0: return
    seg={'LeftArm':('LeftArm','LeftForeArm',1.13),'RightArm':('RightArm','RightForeArm',1.13),'LeftForeArm':('LeftForeArm','LeftHand',1.08),'RightForeArm':('RightForeArm','RightHand',1.08),
         'Neck':('Neck','Head',1.12),'LeftUpLeg':('LeftUpLeg','LeftLeg',1.05),'RightUpLeg':('RightUpLeg','RightLeg',1.05),'LeftLeg':('LeftLeg','LeftFoot',1.06),'RightLeg':('RightLeg','RightFoot',1.06)}
    for v in body.data.vertices:
        b=bone_of(v.index)
        if b not in seg: continue
        a,c,k=seg[b]; A=J['mixamorig:'+a]; B=J['mixamorig:'+c]; d=(B-A).normalized(); t=(v.co-A).dot(d); P=A+d*t
        v.co=P+(v.co-P)*k
thicken()
Z=lambda n: J['mixamorig:'+n].z
armpit=Z('LeftArm')-0.07; neck=Z('Neck'); waist=Z('Hips')+0.035; knee=Z('LeftLeg'); hipz=Z('Hips')
eyeL=center('helper-l-eye',V); eyeR=center('helper-r-eye',V); eyeRad=max((Vector(V[i])-eyeL).length for i in GROUPV['helper-l-eye'])
print('joints armpit %.2f neck %.2f waist %.2f knee %.2f eye %.2f r %.3f'%(armpit,neck,waist,knee,eyeL.z,eyeRad))
# --- region classification per vertex
def region(i): return region_co(body.data.vertices[i].co,bone_of(i))
def region_co(co,b):
    ax=abs(co.x)
    top=SPEC['top']; bot=SPEC['bottom']
    if b in ('LeftFoot','RightFoot','LeftToeBase','RightToeBase'): return 'shoe'
    torso=b in ('Spine','Spine1','Spine2','Hips','LeftShoulder','RightShoulder','Neck') and co.z>waist-0.01
    if b in ('Hips','LeftUpLeg','RightUpLeg','Spine') and co.z<=waist+0.02:
        lim={'shorts':knee+0.07,'jeans':0.07,'trousers':0.08}[bot]
        if co.z>lim: return 'bottom'
    if b in ('LeftLeg','RightLeg'):
        lim={'shorts':knee+0.07,'jeans':0.07,'trousers':0.08}[bot]
        if co.z>lim: return 'bottom'
        if SPEC['socks'] and co.z<0.16: return 'sock'
        return 'skin'
    if top=='tank':
        if b in ('LeftArm','RightArm','LeftForeArm','RightForeArm','LeftHand','RightHand','Head'): return 'skin'
        if b in ('Spine','Spine1','Spine2','Hips','LeftShoulder','RightShoulder','Neck') and waist-0.1<co.z<neck+0.04:
            if co.z>armpit-0.03 and ax>0.128-0.25*max(0,co.z-armpit): return 'skin'   # armholes, narrowing to straps
            if co.y<0 and ax<0.072 and co.z>neck-0.1+ax*0.55: return 'skin'          # scoop neck front
            if co.y>=0 and ax<0.068 and co.z>neck-0.035: return 'skin'               # back neck
            if co.z>neck-0.012 and not (0.066<ax<0.112 and co.z<neck+0.035): return 'skin'
            return 'top'
        return 'skin'
    if top in ('tee','cop'):
        sleeve={'tee':0.22,'cop':0.5}[top]
        if torso and not (b=='Neck' or (co.z>neck-0.02 and ax<0.07 and co.y<0) or co.z>neck+0.01): return 'top'
        if b in ('LeftArm','RightArm') and ax< J['mixamorig:LeftArm'].x+sleeve: return 'top'
        if top=='cop' and b in ('LeftForeArm','RightForeArm') and ax< J['mixamorig:LeftArm'].x+0.47: return 'top'
        return 'skin'
    return 'skin'
reg=[region(i) for i in range(len(body.data.vertices))]
if VARIANT=='hero' and '--dbg' in sys.argv:
    from collections import Counter
    c=Counter(); 
    for i,v in enumerate(body.data.vertices):
        if 0.066<abs(v.co.x)<0.112 and armpit<v.co.z<neck+0.035: c[(bone_of(i),reg[i],round(v.co.z,2))]+=1
    print(sorted(c.items())[:40]); print('armpit',armpit,'neck',neck)
    sys.exit()
# --- skin vertex colours: lips, brows, short hair under the cap
cattr=me.color_attributes.new('Col','FLOAT_COLOR','POINT')
skin=Vector(hexc(SPEC['skin'])[:3]); hair=Vector(hexc(SPEC['hair'])[:3]); HR=Vector((hair.x/skin.x,hair.y/skin.y,hair.z/skin.z))
mouth=Vector((0,min(eyeL.y,eyeR.y)-0.005,eyeL.z-0.088))
for v in me.vertices:
    c=Vector((1,1,1)); co=v.co
    if bone_of(v.index) in ('Head','Neck'):
        front=co.y<eyeL.y+0.02
        d=Vector(((co.x-mouth.x)/0.026,(0),(co.z-mouth.z)/0.011))
        if front and d.length<1 and co.y<mouth.y+0.03: c=Vector((0.55,0.42,0.42))       # lips
        elif SPEC.get('beard') and front and co.z<mouth.z+0.022 and co.z>mouth.z-0.075 and abs(co.x)<0.065 and not d.length<1.25: c=Vector((0.5,0.45,0.43))   # stubble / goatee
        for e in (eyeL,eyeR):
            bx=(co.x-e.x)/0.026; bz=(co.z-(e.z+0.024))/0.0075
            if front and bx*bx+bz*bz<1: c=Vector((0.12,0.1,0.1))                         # eyebrows
        if co.z>eyeL.z+0.045 and not (front and co.z<eyeL.z+0.07): c=HR if SPEC['hat']!='hair' else c
        if co.z>eyeL.z+0.02 and co.y>eyeL.y+0.06 and co.z>eyeL.z-0.04: c=HR if SPEC['hat']!='hair' else c
    cattr.data[v.index].color=(min(c.x,4),min(c.y,4),min(c.z,4),1)
skin_mat=material('Skin',SPEC['skin'],0.6,vcol=True); me.materials.append(skin_mat)
# --- clothing shells: duplicate region faces, push out along normals
def shell(name,regs,off,col,rough,extra=None,solid=0.0,classify=None):
    ob=body.copy(); ob.data=body.data.copy(); ob.name=name; bpy.context.scene.collection.objects.link(ob)
    bm=bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.subdivide_edges(bm,edges=bm.edges[:],cuts=1,use_grid_fill=True)
    bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    dl=bm.verts.layers.deform.active; names=[g.name for g in ob.vertex_groups]
    def bn(v):
        d=v[dl]
        if not d: return ''
        return names[max(d.items(),key=lambda kv:kv[1])[0]].replace('mixamorig:','')
    cls=classify or region_co
    keep={v.index for v in bm.verts if cls(v.co,bn(v)) in regs}
    kill=[f for f in bm.faces if sum(v.index in keep for v in f.verts)<len(f.verts)-1]
    bmesh.ops.delete(bm,geom=kill,context='FACES'); bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
    for it in range(10):
        newp={}
        for v in bm.verts:
            if not v.is_boundary: continue
            nb=[e.other_vert(v) for e in v.link_edges if e.is_boundary]
            if len(nb)==2: newp[v]=v.co*0.5+(nb[0].co+nb[1].co)*0.25
        for v,p in newp.items(): v.co=p
    bm.normal_update()
    for v in bm.verts:
        n=v.normal.copy(); d=off
        if extra: d+=extra(v.co)
        v.co+=n*d
    bm.to_mesh(ob.data); bm.free()
    ob.data.materials.clear(); m=material(name+'Mat',col,rough); m.use_backface_culling=False; ob.data.materials.append(m)
    if ob.data.color_attributes.get('Col'): ob.data.color_attributes.remove(ob.data.color_attributes['Col'])
    if solid:
        s=ob.modifiers.new('sol','SOLIDIFY'); s.thickness=solid; s.offset=1
    return ob
def baggy(co):
    if co.z<waist and co.z>knee: return 0.012*smooth(waist-0.05,knee+0.2,co.z)+0.006
    return 0.004
tb=SPEC['top']
top=shell('Top',{'top'},0.007 if tb=='tank' else 0.012,SPEC['topc'],0.92,solid=0.003)
bot=shell('Bottom',{'bottom'},0.009,SPEC['botc'],0.9,extra=baggy if SPEC['bottom']=='shorts' else None,solid=0.003)
shoe=shell('Shoes',{'shoe'},0.012,SPEC['shoes'],0.45,extra=lambda co:0.008 if co.z<0.035 else 0.0)
parts=[top,bot,shoe]
if SPEC['socks']: parts.append(shell('Socks',{'sock'},0.004,SPEC['socks'],0.9))
def weight_all(ob,bone):
    vg=ob.vertex_groups.new(name='mixamorig:'+bone); vg.add(list(range(len(ob.data.vertices))),1.0,'REPLACE')
def add_prim(name,col,rough,metal,bone,build):
    bm=bmesh.new(); build(bm); me2=bpy.data.meshes.new(name); bm.to_mesh(me2); bm.free()
    ob=mk_obj(name,me2); me2.materials.append(material(name+'Mat',col,rough,metal)); weight_all(ob,bone)
    for p in me2.polygons: p.use_smooth=True
    return ob
# eyes
for e,nm in ((eyeL,'EyeL'),(eyeR,'EyeR')):
    def bw(bm,e=e):
        bmesh.ops.create_uvsphere(bm,u_segments=16,v_segments=12,radius=eyeRad*0.9,matrix=Matrix.Translation(e))
    parts.append(add_prim(nm,'#d9d2c8',0.35,0,'Head',bw))
    def bi(bm,e=e):
        bmesh.ops.create_uvsphere(bm,u_segments=12,v_segments=8,radius=eyeRad*0.42,matrix=Matrix.Translation(e+Vector((0,-eyeRad*0.84,0)))@Matrix.Scale(0.3,4,Vector((0,1,0))))
    parts.append(add_prim(nm+'Iris','#1b0f08',0.1,0,'Head',bi))
# headwear
hv=[body.data.vertices[i].co for i in range(len(reg)) if bone_of(i)=='Head']
hx=max(abs(c.x) for c in hv); htop=max(c.z for c in hv); hy0=min(c.y for c in hv if c.z>eyeL.z); hy1=max(c.y for c in hv if c.z>eyeL.z)
hc=Vector((0,(hy0+hy1)/2,eyeL.z+0.035)); hr=hx*1.08
yc=(hy0+hy1)/2
def capreg(i):
    co=body.data.vertices[i].co
    return bone_of(i) in ('Head',) and co.z>eyeL.z+0.03-0.35*(co.y-yc) and co.z>eyeL.z-0.005
if SPEC['hat']=='cap':
    capo=shell('Cap',{'cap'},0.011,SPEC['hatc'],0.85,solid=0.004,classify=lambda co,b:'cap' if b=='Head' and co.z>eyeL.z+0.03-0.35*(co.y-yc) and co.z>eyeL.z-0.005 else '')
    parts.append(capo)
    edge=[v.co for v in capo.data.vertices if v.co.y>yc+0.05]
    zb=sum(c.z for c in edge)/max(1,len(edge)); yb=max(v.co.y for v in capo.data.vertices)
    def brim(bm):
        r=bmesh.ops.create_circle(bm,cap_ends=True,segments=24,radius=1,matrix=Matrix.Translation(Vector((0,yb-0.035,zb+0.004)))@Matrix.Diagonal((hr*0.8,0.11,1,1)))
        bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.y<yb-0.03],context='VERTS')
        for v in bm.verts: v.co.z-=max(0,v.co.y-yb)*0.12+ (v.co.x/(hr*0.8))**2*0.012
        bmesh.ops.create_uvsphere(bm,u_segments=8,v_segments=6,radius=0.009,matrix=Matrix.Translation(Vector((0,yc+0.01,htop+0.012))))
        bmesh.ops.create_cube(bm,size=1,matrix=Matrix.Translation(Vector((0,hy0+0.003,eyeL.z+0.052)))@Matrix.Diagonal((0.05,0.004,0.007,1)))
    b=add_prim('Brim',SPEC['hatc'],0.85,0,'Head',brim)
    b.data.materials[0].diffuse_color=(0,0,0,1)
    so=b.modifiers.new('sol','SOLIDIFY'); so.thickness=0.006
    parts.append(b)
if False:
    def cap(bm):
        bmesh.ops.create_uvsphere(bm,u_segments=24,v_segments=12,radius=1,matrix=Matrix.Translation(hc)@Matrix.Diagonal((hr,(hy1-hy0)/2*1.07,(htop-hc.z)*1.06,1)))
        bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z<hc.z-0.004],context='VERTS')
        # brim at the back (worn backwards)
        r=bmesh.ops.create_circle(bm,cap_ends=True,segments=20,radius=1,matrix=Matrix.Translation(Vector((0,hy1-0.01,hc.z+0.004)))@Matrix.Diagonal((hr*0.86,0.075,1,1)))
        for v in r['verts']:
            if v.co.y<hy1-0.02: v.co.y=hy1-0.02
            v.co.z-= (v.co.y-hy1)*0.18
        bmesh.ops.create_cube(bm,size=1,matrix=Matrix.Translation(Vector((0,hy0+0.004,hc.z+0.02)))@Matrix.Diagonal((0.045,0.006,0.016,1)))
        bmesh.ops.create_uvsphere(bm,u_segments=8,v_segments=6,radius=0.009,matrix=Matrix.Translation(Vector((0,(hy0+hy1)/2,htop+0.008))))
    parts.append(add_prim('Cap',SPEC['hatc'],0.85,0,'Head',cap))
elif SPEC['hat']=='helmet':
    def helm(bm):
        bmesh.ops.create_uvsphere(bm,u_segments=24,v_segments=14,radius=1,matrix=Matrix.Translation(hc+Vector((0,0,0.0)))@Matrix.Diagonal((hr*1.03,(hy1-hy0)/2*1.12,0.2,1)))
        bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z<hc.z-0.01],context='VERTS')
        for v in bm.verts:
            t=max(0,(v.co.z-hc.z)/0.2); v.co.x*=1-0.12*t*t; v.co.y=hc.y+(v.co.y-hc.y)*(1-0.08*t*t)
        r=bmesh.ops.create_circle(bm,cap_ends=True,segments=24,radius=1,matrix=Matrix.Translation(hc+Vector((0,0,-0.008)))@Matrix.Diagonal((hr*1.12,(hy1-hy0)/2*1.2,1,1)))
        bmesh.ops.create_uvsphere(bm,u_segments=8,v_segments=6,radius=0.018,matrix=Matrix.Translation(hc+Vector((0,0,0.205))))
    parts.append(add_prim('Helmet',SPEC['hatc'],0.35,0,'Head',helm))
    def badge(bm): bmesh.ops.create_cube(bm,size=1,matrix=Matrix.Translation(hc+Vector((0,hy0-hc.y-0.012,0.07)))@Matrix.Diagonal((0.035,0.006,0.045,1)))
    parts.append(add_prim('Badge','#d9dce0',0.25,1,'Head',badge))
elif SPEC['hat']=='longhair':
    def hairmesh(bm):
        bmesh.ops.create_uvsphere(bm,u_segments=22,v_segments=14,radius=1,matrix=Matrix.Translation(hc+Vector((0,0.008,-0.005)))@Matrix.Diagonal((hx*1.1,(hy1-hy0)/2*1.1,(htop-hc.z)*1.12,1)))
        bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.y<hc.y-0.035 and v.co.z<hc.z+0.03],context='VERTS')
        for v in bm.verts:
            if v.co.z<hc.z and v.co.y>hc.y-0.03: v.co.z=hc.z-(hc.z-v.co.z)*2.6; v.co.x*=1.05
    parts.append(add_prim('Hair',SPEC['hair'],0.7,0,'Head',hairmesh))
else:
    def hairmesh(bm):
        bmesh.ops.create_uvsphere(bm,u_segments=22,v_segments=12,radius=1,matrix=Matrix.Translation(hc+Vector((0,0.006,-0.005)))@Matrix.Diagonal((hx*1.05,(hy1-hy0)/2*1.07,(htop-hc.z)*1.1,1)))
        bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z<hc.z-0.03 or (v.co.y<hc.y-0.04 and v.co.z<hc.z+0.03)],context='VERTS')
    parts.append(add_prim('Hair',SPEC['hair'],0.7,0,'Head',hairmesh))
if SPEC['chain']:
    def ch(bm):
        bmesh.ops.create_cone(bm,cap_ends=False,segments=24,radius1=1,radius2=1,depth=0.01)
        # convert to a torus-like ring via a thin rotated circle path
    def chain(bm):
        n=28; c=Vector((0,J['mixamorig:Neck'].y-0.005,neck-0.035))
        for k in range(n):
            a=k/n*math.tau; p=c+Vector((math.cos(a)*0.068,math.sin(a)*0.06-0.012*(1+math.sin(a)),-0.05*max(0,-math.sin(a))))
            bmesh.ops.create_uvsphere(bm,u_segments=6,v_segments=4,radius=0.0065,matrix=Matrix.Translation(p))
    parts.append(add_prim('Chain','#d4af37',0.25,1.0,'Spine2',chain))
if VARIANT=='cop':
    vest=shell('Vest',{'vest'},0.022,'#d6f21a',0.6,solid=0.004,classify=lambda co,b:'vest' if b in ('Spine','Spine1','Spine2','Hips','LeftShoulder','RightShoulder') and waist-0.05<co.z<armpit+0.06 and abs(co.x)<J['mixamorig:LeftArm'].x-0.025 else '')
    parts.append(vest)
for ob in [body]+parts:
    ob.parent=ao
    if not ob.modifiers.get('Armature'):
        m=ob.modifiers.new('Armature','ARMATURE'); m.object=ao
    for p in ob.data.polygons: p.use_smooth=True
for ob in parts:
    for m in list(ob.modifiers):
        if m.type=='SOLIDIFY':
            bpy.context.view_layer.objects.active=ob; bpy.ops.object.modifier_apply(modifier=m.name)
print('regions',{r:reg.count(r) for r in set(reg)})
bpy.ops.export_scene.gltf(filepath=OUT,export_format='GLB',export_skins=True,export_animations=False,export_vertex_color='ACTIVE',export_apply=False,export_yup=True)
print('exported',OUT)
