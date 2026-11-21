import bpy, sys
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=sys.argv[-2])
for o in list(bpy.data.objects):
    if o.type=='MESH': bpy.data.objects.remove(o)
for a in list(bpy.data.actions):
    if not any(k in a.name for k in ('idle','walk','run')): bpy.data.actions.remove(a)
print([a.name for a in bpy.data.actions])
bpy.ops.export_scene.gltf(filepath=sys.argv[-1],export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_yup=True)
