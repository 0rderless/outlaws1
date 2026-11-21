# Vehicle builder: lofted body cage + subdivision surface + boolean wheel arches. python3 -I cars.py <type> <out.glb>
import bpy, bmesh, sys, math
from mathutils import Vector, Matrix
TYPE=sys.argv[-2]; OUT=sys.argv[-1]
def hexc(h,a=1.0):
    h=h.lstrip('#'); c=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return [x/12.92 if x<=0.04045 else ((x+0.055)/1.055)**2.4 for x in c]+[a]
MATS={}
def mat(name,col,rough=.5,metal=0.0,emis=None,es=0.0):
    if name in MATS: return MATS[name]
    m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=hexc(col); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    if emis: b.inputs['Emission Color'].default_value=hexc(emis); b.inputs['Emission Strength'].default_value=es
    MATS[name]=m; return m
P={ # L, W, H, clearance, hood/windshield/roof/rear fractions, rear style
 'saloon': dict(L=4.62,W=1.82,H=1.44,zb=0.18,belt=0.92,hood=0.86,ws=0.30,roof=0.44,rw=0.70,tr=0.84,deck=0.98,rear='sedan',wz=(0.19,0.80),r=0.33),
 'hatch':  dict(L=4.05,W=1.76,H=1.46,zb=0.17,belt=0.90,hood=0.84,ws=0.25,roof=0.42,rw=0.86,tr=0.97,deck=1.0,rear='hatch',wz=(0.17,0.83),r=0.32),
 'suv':    dict(L=4.72,W=1.92,H=1.74,zb=0.26,belt=1.10,hood=1.04,ws=0.24,roof=0.38,rw=0.90,tr=0.98,deck=1.2,rear='hatch',wz=(0.18,0.81),r=0.39),
 'sports': dict(L=4.50,W=1.94,H=1.24,zb=0.14,belt=0.82,hood=0.82,ws=0.36,roof=0.52,rw=0.66,tr=0.90,deck=0.9,rear='fast',wz=(0.2,0.8),r=0.31),
 'cab':    dict(L=4.58,W=1.94,H=1.78,zb=0.2,belt=1.0,hood=0.98,ws=0.25,roof=0.37,rw=0.86,tr=0.95,deck=1.06,rear='hatch',wz=(0.18,0.82),r=0.36),
 'police': dict(L=4.56,W=1.82,H=1.50,zb=0.18,belt=0.93,hood=0.86,ws=0.27,roof=0.42,rw=0.90,tr=0.97,deck=1.02,rear='hatch',wz=(0.18,0.82),r=0.33),
}
def lerp(a,b,t): return a+(b-a)*t
def sm(t): t=max(0,min(1,t)); return t*t*(3-2*t)
def station(p,t):
    """half cross-section at fraction t (0=front, 1=rear): list of (x,z), plus segment kinds"""
    W=p['W']/2; zb=p['zb']; belt=p['belt']; H=p['H']; hood=p['hood']; deck=p['deck']
    # longitudinal top height
    if t<p['ws']: top=lerp(hood-0.12,hood,sm(t/max(0.01,p['ws'])*1.6)); kind='hood'
    elif t<p['roof']: top=lerp(hood,H,sm((t-p['ws'])/(p['roof']-p['ws']))); kind='ws'
    elif t<p['rw']: top=H; kind='roof'
    elif t<p['tr']:
        k=(t-p['rw'])/(p['tr']-p['rw']); top=lerp(H,deck,sm(k) if p['rear']!='fast' else k); kind='rw'
    else: top=lerp(deck,deck-0.12,sm((t-p['tr'])/max(0.01,1-p['tr']))); kind='trunk'
    # plan-view rounding at the ends
    endk=min(1,t/0.06, (1-t)/0.05); wscale=0.8+0.2*sm(endk)
    w=W*wscale
    cab=kind in ('ws','roof','rw')
    if cab:
        wt=w*(0.78 if p['H']>1.6 else 0.74); edge=top-0.04
        pts=[(0,zb),(w*0.86,zb),(w,zb+0.22),(w,belt),(wt,edge),(0,top+0.03)]
    else:
        pts=[(0,zb),(w*0.86,zb),(w,zb+0.22),(w,min(belt,top-0.04)),(w*0.93,top),(0,top+0.035)]
    zfrontlift=0.10*(1-sm(t/0.05))+0.08*(1-sm((1-t)/0.05))   # tuck the bumpers in
    pts=[(x,z+ (zfrontlift if z<=zb+0.01 else 0)) for x,z in pts]
    return pts,kind
def build_body(p):
    N=28; ts=[i/(N-1) for i in range(N)]
    bm=bmesh.new(); rings=[]; kinds=[]
    for t in ts:
        half,kind=station(p,t); y=-p['L']/2+t*p['L']
        ring=[(x,z) for x,z in half]+[(-x,z) for x,z in reversed(half[1:-1])]
        rings.append([bm.verts.new((x,y,z)) for x,z in ring]); kinds.append(kind)
    n=len(rings[0]); faces=[]
    pil_b=int(N*((p['roof']+p['rw'])/2))
    for i in range(N-1):
        for k in range(n):
            a,b,c,d=rings[i][k],rings[i][(k+1)%n],rings[i+1][(k+1)%n],rings[i+1][k]
            f=bm.faces.new((a,b,c,d)); 
            # segment index: 0 bottom,1 lowerside,2 side,3 window/hoodside,4 top ... mirrored
            seg=k if k<5 else (n-1-k)
            ki=kinds[i]; kj=kinds[i+1]; cab=ki in('ws','roof','rw') and kj in('ws','roof','rw')
            m='Paint'
            if seg==0: m='Under'
            elif seg==1: m='Trim'
            elif seg==3 and cab and i!=pil_b and kinds[i]!=kinds[i-1 if i>0 else 0] or (seg==3 and cab and i!=pil_b): m='Glass'
            elif seg==4 and ki=='ws' and kj=='ws': m='Glass'
            elif seg==4 and ki=='rw' and kj=='rw': m='Glass'
            faces.append((f,m,seg,i))
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    cl=bm.edges.layers.float.get('crease_edge') or bm.edges.layers.float.new('crease_edge')
    crease_k={2:0.5,3:0.85,4:0.8,n-2:0.5,n-3:0.85,n-4:0.8}
    for i in range(N-1):
        for k,cv in crease_k.items():
            e=bm.edges.get((rings[i][k],rings[i+1][k]))
            if e: e[cl]=cv
    for ring in (rings[0],rings[-1]):
        for k in range(n):
            e=bm.edges.get((ring[k],ring[(k+1)%n]))
            if e: e[cl]=0.55
    return bm,faces,rings
def finish_object(name,bm,faces,p):
    me=bpy.data.meshes.new(name); 
    names=['Paint','Glass','Trim','Under']
    bm.faces.index_update(); flut={f.index:m for f,m,seg,i in faces}
    bm.to_mesh(me); bm.free()
    ob=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(ob)
    mats={'Paint':mat('Paint','#ffffff',0.3,0.2),'Glass':mat('Glass','#0e1419',0.05,0.0),'Trim':mat('Trim','#1a1b1d',0.6),'Under':mat('Under','#0d0d0e',0.9)}
    order=list(mats); 
    for nm in order: me.materials.append(mats[nm])
    for poly in me.polygons:
        poly.material_index=order.index(flut.get(poly.index,'Paint')); poly.use_smooth=True
    return ob
def apply_mod(ob,mtype,**kw):
    m=ob.modifiers.new(mtype,mtype)
    for k,v in kw.items(): setattr(m,k,v)
    bpy.context.view_layer.objects.active=ob; ob.select_set(True); bpy.ops.object.modifier_apply(modifier=m.name); ob.select_set(False)
def prim(name,matname,build,smooth=True,bevel=0):
    bm=bmesh.new(); build(bm); me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(ob); me.materials.append(MATS[matname])
    for pp in me.polygons: pp.use_smooth=smooth
    if bevel: apply_mod(ob,'BEVEL',width=bevel,segments=2)
    return ob
def cube(bm,c,s,rx=0):
    bmesh.ops.create_cube(bm,size=1,matrix=Matrix.Translation(Vector(c))@Matrix.Rotation(rx,4,'X')@Matrix.Diagonal((s[0],s[1],s[2],1)))
def cyl(bm,c,r,depth,axis='X',seg=20):
    rot={'X':Matrix.Rotation(math.pi/2,4,'Y'),'Y':Matrix.Rotation(math.pi/2,4,'X'),'Z':Matrix.Identity(4)}[axis]
    bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=r,radius2=r,depth=depth,matrix=Matrix.Translation(Vector(c))@rot)
bpy.ops.wm.read_factory_settings(use_empty=True)
mat('Chrome','#d9dde2',0.12,1.0); mat('LightF','#f6f3ea',0.05,0,'#fff6e0',1.5); mat('LightR','#a50d12',0.15,0,'#ff1a1a',1.2); mat('Amber','#d27a0f',0.2,0,'#ff8a00',0.6)
mat('PlateF','#f4f4f0',0.4); mat('PlateR','#f2c200',0.4); mat('Black','#0c0c0d',0.5); mat('Taxi','#ffcc22',0.3,0,'#ffcc22',1.2)
mat('Livery','#ffffff',0.35,0.1); mat('BarBlue','#16308a',0.2,0,'#3b6bff',0.0); mat('BarRed','#8a1616',0.2,0,'#ff3030',0.0)
if TYPE=='bus':
    L=11.0; W=2.52; H=4.38
    bm=bmesh.new(); rings=[]; N=24
    for i in range(N):
        t=i/(N-1); y=-L/2+t*L; endk=min(1,t/0.03,(1-t)/0.03); w=W/2*(0.86+0.14*sm(endk))
        top=H-0.18*(1-sm(t/0.05))-0.14*(1-sm((1-t)/0.05))
        half=[(0,0.36),(w*0.9,0.36),(w,0.55),(w,1.18),(w,2.12),(w,2.74),(w,3.86),(w*0.92,top-0.06),(0,top)]
        ring=half+[(-x,z) for x,z in reversed(half[1:-1])]
        rings.append([bm.verts.new((x,y,z)) for x,z in ring])
    n=len(rings[0]); faces=[]
    for i in range(N-1):
        for k in range(n):
            f=bm.faces.new((rings[i][k],rings[i][(k+1)%n],rings[i+1][(k+1)%n],rings[i+1][k])); seg=k if k<8 else n-1-k
            m='Paint'
            if seg==0: m='Under'
            elif seg in (3,5) and 1<=i<=N-3 and i%3!=0: m='Glass'
            faces.append((f,m,seg,i))
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    body=finish_object('Body',bm,faces,None)
    MATS['Paint'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=hexc('#c8231b')
    MATS['Paint'].name='BusRed'
    apply_mod(body,'SUBSURF',levels=2)
    for wz in (-3.55,3.2):
        cut=prim('cut','Black',lambda bm,wz=wz: cyl(bm,(0,wz,0.5),0.62,3.0,'X',28))
        mo=body.modifiers.new('b','BOOLEAN'); mo.object=cut; mo.operation='DIFFERENCE'
        bpy.context.view_layer.objects.active=body; bpy.ops.object.modifier_apply(modifier=mo.name); bpy.data.objects.remove(cut)
        prim('liner','Black',lambda bm,wz=wz: cyl(bm,(0,wz,0.5),0.6,W-0.1,'X',24))
    prim('ws','Glass',lambda bm: cube(bm,(0,-L/2-0.02,1.75),(W-0.3,0.04,1.15)),bevel=0.03)
    prim('wsu','Glass',lambda bm: cube(bm,(0,-L/2-0.0,3.28),(W-0.25,0.04,0.95),rx=-0.08),bevel=0.03)
    prim('wr','Glass',lambda bm: cube(bm,(0,L/2+0.01,3.3),(W-0.6,0.04,0.7)),bevel=0.02)
    prim('blind','Black',lambda bm: cube(bm,(0,-L/2-0.03,2.48),(1.9,0.04,0.36)),bevel=0.01)
    prim('route','Amber',lambda bm: cube(bm,(-0.3,-L/2-0.055,2.48),(1.1,0.01,0.2)))
    for s in (-1,1):
        prim('hl','LightF',lambda bm,s=s: cube(bm,(s*0.92,-L/2-0.02,0.72),(0.3,0.06,0.18)),bevel=0.02)
        prim('tl','LightR',lambda bm,s=s: cube(bm,(s*0.95,L/2+0.02,0.8),(0.22,0.06,0.32)),bevel=0.02)
        prim('mir','Black',lambda bm,s=s: cube(bm,(s*1.5,-L/2+0.3,2.05),(0.06,0.18,0.3)),bevel=0.02)
    for z in (4.15,0.35,-3.95):
        prim('door','Glass',lambda bm,z=z: cube(bm,(W/2+0.005,z,1.32),(0.02,0.95,1.85)))
    prim('pf','PlateF',lambda bm: cube(bm,(0,-L/2-0.04,0.5),(0.52,0.02,0.12)))
    prim('pr','PlateR',lambda bm: cube(bm,(0,L/2+0.03,0.62),(0.52,0.02,0.12)))
else:
    p=P[TYPE]; L=p['L']; W=p['W']
    bm,faces,rings=build_body(p)
    if TYPE=='police':
        for f,m,seg,i in faces:
            if seg==2 and m=='Paint': pass
    body=finish_object('Body',bm,faces,p)
    if TYPE=='police':   # Battenburg band on the sides
        me=body.data; me.materials.append(MATS['Livery']); li=len(me.materials)-1
        uv=me.uv_layers.new(name='UVMap')
        for poly in me.polygons:
            c=poly.center
            if me.materials[poly.material_index].name=='Paint' and abs(poly.normal.x)>0.7 and p['zb']+0.12<c.z<p['belt']: poly.material_index=li
        for poly in me.polygons:
            for l in poly.loop_indices:
                v=me.vertices[me.loops[l].vertex_index].co; uv.data[l].uv=(v.y/0.5,(v.z-0.3)/0.5)
    apply_mod(body,'SUBSURF',levels=2)
    r=p['r']
    wys=[-L/2+p['wz'][0]*L,-L/2+p['wz'][1]*L]
    for wy in wys:
        cut=prim('cut','Black',lambda bm,wy=wy: cyl(bm,(0,wy,r),r+0.06,W+0.6,'X',28))
        mo=body.modifiers.new('b','BOOLEAN'); mo.object=cut; mo.operation='DIFFERENCE'
        bpy.context.view_layer.objects.active=body; bpy.ops.object.modifier_apply(modifier=mo.name); bpy.data.objects.remove(cut)
        prim('liner','Black',lambda bm,wy=wy: cyl(bm,(0,wy,r+0.02),r+0.04,W-0.08,'X',24))
    zl=p['hood']-0.13
    for s in (-1,1):
        prim('hl','LightF',lambda bm,s=s: cube(bm,(s*(W/2-0.3),-L/2+0.06,zl),(0.36,0.12,0.12)),bevel=0.025)
        prim('tl','LightR',lambda bm,s=s: cube(bm,(s*(W/2-0.25),L/2-0.06,p['deck']-0.16),(0.36,0.12,0.13)),bevel=0.025)
        prim('ind','Amber',lambda bm,s=s: cube(bm,(s*(W/2-0.08),-L/2+0.12,zl-0.02),(0.08,0.1,0.08)),bevel=0.015)
        prim('mir','Paint',lambda bm,s=s: cube(bm,(s*(W/2+0.07),-L/2+p['ws']*L+0.18,p['belt']+0.06),(0.14,0.1,0.1)),bevel=0.03)
        for dy in (0.42,0.42+ (0.95 if p['L']>4.2 else 0)):
            if dy>0.9 and TYPE=='sports': continue
            prim('handle','Chrome',lambda bm,s=s,dy=dy: cube(bm,(s*(W/2+0.005),-L/2+p['roof']*L+dy-0.3,p['belt']-0.09),(0.03,0.16,0.035)),bevel=0.01)
    grille_col='Chrome' if TYPE=='cab' else 'Black'
    prim('grille',grille_col,lambda bm: cube(bm,(0,-L/2+0.04,zl-0.03),(W*0.42,0.1,0.16)),bevel=0.03)
    prim('pf','PlateF',lambda bm: cube(bm,(0,-L/2-0.005,p['zb']+0.2),(0.52,0.03,0.12)))
    prim('pr','PlateR',lambda bm: cube(bm,(0,L/2+0.005,p['deck']-0.34),(0.52,0.03,0.12)))
    if TYPE=='cab':
        prim('taxi','Taxi',lambda bm: cube(bm,(0,-L/2+p['roof']*L+0.15,p['H']+0.09),(0.48,0.16,0.14)),bevel=0.02)
    if TYPE=='police':
        base=prim('bar','Black',lambda bm: cube(bm,(0,-L/2+p['roof']*L+0.45,p['H']+0.05),(1.15,0.28,0.06)),bevel=0.02)
        prim('barL','BarBlue',lambda bm: cube(bm,(-0.32,-L/2+p['roof']*L+0.45,p['H']+0.12),(0.5,0.24,0.1)),bevel=0.02)
        prim('barR','BarRed',lambda bm: cube(bm,(0.32,-L/2+p['roof']*L+0.45,p['H']+0.12),(0.5,0.24,0.1)),bevel=0.02)
    if TYPE=='sports':
        prim('spoiler','Paint',lambda bm: cube(bm,(0,L/2-0.18,p['deck']+0.08),(W-0.3,0.25,0.03)),bevel=0.01)
        for s2 in (-1,1): prim('post','Black',lambda bm,s2=s2: cube(bm,(s2*0.55,L/2-0.18,p['deck']+0.0),(0.05,0.08,0.18)))
    if TYPE=='suv':
        for s in (-1,1): prim('rail','Chrome',lambda bm,s=s: cube(bm,(s*(W/2-0.22),-L/2+0.5*L,p['H']+0.04),(0.04,2.2,0.04)))
# join everything into one object per material for few draw calls
objs=[o for o in bpy.data.objects if o.type=='MESH']
for o in objs: o.select_set(True)
bpy.context.view_layer.objects.active=objs[0]; bpy.ops.object.join()
car=bpy.context.view_layer.objects.active; car.name=TYPE
bpy.ops.export_scene.gltf(filepath=OUT,export_format='GLB',export_apply=True,export_yup=True)
print('exported',OUT,len(car.data.polygons),'faces')
