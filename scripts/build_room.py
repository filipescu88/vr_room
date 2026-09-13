import bpy, math, os, json
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.materials): bpy.data.materials.remove(d)
def mat(name, color, rough=.65, metallic=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metallic
 return m
wall=mat('Ciepła biel',(.77,.76,.70)); oak=mat('Dąb',(.43,.24,.11)); dark=mat('Grafit',(.035,.045,.052)); fabric=mat('Niebieska tkanina',(.07,.19,.25)); rug=mat('Dywan',(.57,.49,.36)); green=mat('Liście',(.055,.23,.10)); clay=mat('Terakota',(.42,.16,.08)); white=mat('Ceramika',(.88,.85,.76)); gold=mat('Mosiądz',(.46,.31,.10),.3,.65); glass=mat('Widok za oknem',(.48,.72,.85)); art=mat('Obraz ochra',(.68,.33,.09))
def box(name, loc, size, material, bevel=.025):
 bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(material)
 if bevel:
  mod=o.modifiers.new('Miękkie krawędzie','BEVEL'); mod.width=bevel; mod.segments=2; bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
def cyl(name,loc,radius,depth,material):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=radius,depth=depth,location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(material); return o
def sphere(name,loc,scale,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,location=loc); o=bpy.context.object; o.name=name; o.scale=scale; o.data.materials.append(material); return o
# Blender Z-up; glTF export converts to WebXR Y-up. Interior 5 x 4 x 2.7 m.
box('Podłoże',(0,0,-.07),(5.2,4.2,.14),oak,0)
for i in range(20):
 for j in range(4):
  x=-2.375+i*.25; y=-1.5+j
  box('Deska podłogowa',(x,y,-.006),(.245,.995,.016),oak,.002)
box('Ściana tylna',(0,2.08,1.35),(5.2,.16,2.7),wall,0)
box('Ściana prawa',(2.58,0,1.35),(.16,4.2,2.7),wall,0)
box('Ściana przednia',(0,-2.08,1.35),(5.2,.16,2.7),wall,0)
box('Pod oknem',(-2.58,0,.43),(.16,4.2,.86),wall,0)
box('Nad oknem',(-2.58,0,2.48),(.16,4.2,.44),wall,0)
for y in [-1.65,1.65]: box('Bok okna',(-2.58,y,1.56),(.16,.9,1.4),wall,0)
box('Niebo za oknem',(-2.69,0,1.55),(.025,2.4,1.4),glass,0)
for y in [-1.2,0,1.2]: box('Rama okna',(-2.49,y,1.55),(.1,.055,1.43),white,.006)
for z in [.85,2.25]: box('Rama pozioma',(-2.49,0,z),(.1,2.46,.055),white,.006)
box('Parapet',(-2.40,0,.85),(.35,2.6,.06),oak)
box('Sufit',(0,0,2.76),(5.2,4.2,.12),wall,0)
for y in [-1.99,1.99]: box('Listwa',(0,y,.045),(5,.025,.09),white,.003)
for x in [-2.49,2.49]: box('Listwa',(x,0,.045),(.025,4,.09),white,.003)
# Sofa along rear wall, facing front.
for x in [-1.02,1.02]:
 for y in [1.12,1.7]: cyl('Nóżka kanapy',(x,y,.12),.04,.24,oak)
box('Kanapa podstawa',(0,1.43,.29),(2.4,.9,.22),fabric,.08)
box('Kanapa oparcie',(0,1.79,.73),(2.4,.21,.86),fabric,.08)
for x in [-1.12,1.12]: box('Podłokietnik',(x,1.39,.61),(.2,.92,.55),fabric,.07)
for x in [-.51,.51]: box('Siedzisko',(x,1.38,.49),(.98,.7,.2),fabric,.07)
for x in [-.75,.72]:
 o=box('Poduszka',(x,1.59,.79),(.4,.16,.4),rug,.07); o.rotation_euler[0]=-.16
box('Dywan',(0,.1,.016),(2.5,1.9,.025),rug,.04)
box('Stolik blat',(0,.2,.46),(1.05,.62,.065),oak,.08)
for x in [-.4,.4]:
 for y in [-.01,.41]: cyl('Noga stolika',(x,y,.23),.026,.44,dark)
box('Książka na stole',(-.23,.16,.51),(.23,.29,.035),white,.008)
cyl('Filiżanka',(.22,.18,.54),.045,.09,white)
# TV cabinet and screen.
box('Szafka RTV',(0,-1.73,.3),(1.8,.44,.48),oak)
for x in [-.6,0,.6]: box('Front szafki',(x,-1.961,.31),(.58,.025,.38),wall,.005)
box('Telewizor',(0,-1.97,1.22),(1.32,.065,.77),dark,.02)
screen=mat('Ekran',(.012,.03,.045),.2)
box('Szkło ekranu',(0,-1.93,1.22),(1.26,.01,.71),screen,.006)
# Desk on right, chair faces right.
box('Biurko',(2.12,-.68,.76),(.7,1.15,.055),oak)
for x in [1.85,2.38]:
 for y in [-1.15,-.2]: box('Noga biurka',(x,y,.37),(.04,.04,.74),dark,.005)
box('Laptop podstawa',(2.10,-.7,.80),(.31,.37,.018),dark,.006)
box('Laptop ekran',(2.25,-.7,.94),(.025,.37,.28),dark,.006)
box('Krzesło siedzisko',(1.48,-.68,.46),(.46,.46,.07),fabric,.045)
box('Krzesło oparcie',(1.26,-.68,.72),(.065,.46,.5),fabric,.045)
for x in [1.3,1.64]:
 for y in [-.85,-.51]: box('Noga krzesła',(x,y,.23),(.035,.035,.46),oak,.004)
# Bookshelf at right rear.
for y in [.68,1.65]: box('Regał bok',(2.28,y,1.01),(.42,.04,2.02),oak)
for z in [.1,.55,1,1.45,1.95]: box('Półka',(2.28,1.165,z),(.42,1.01,.035),oak,.008)
for i in range(9): box('Książka',(2.25,.79+i*.07,1.2),(.26,.05,.33-(i%3)*.04),[fabric,art,white][i%3],.003)
cyl('Wazon',(2.24,1.21,.70),.10,.27,white)
# Plants, lamp, art and door.
for x,y,r in [(-1.95,1.52,.18),(-2.32,.62,.08)]:
 base=0 if r>.1 else .89
 cyl('Donica',(x,y,base+r),r,2*r,clay)
 for i in range(7):
  a=i*2.4; z=base+2*r+.15+i*.055
  cyl('Łodyga',(x,y,base+2*r+.22),.009,.44,green)
  o=sphere('Liść',(x+math.cos(a)*r,y+math.sin(a)*r,z),(r*.95,r*.35,.055),green); o.rotation_euler[2]=a
cyl('Lampa podstawa',(-1.52,1.58,.035),.21,.06,dark)
cyl('Lampa słupek',(-1.52,1.58,.83),.015,1.6,gold)
bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=.24,radius2=.14,depth=.30,location=(-1.52,1.58,1.7)); bpy.context.object.name='Abażur'; bpy.context.object.data.materials.append(white)
box('Rama obrazu',(0,1.974,1.89),(1.25,.04,.61),oak)
box('Obraz',(0,1.948,1.89),(1.17,.012,.53),white,.003)
box('Kompozycja ochra',(-.23,1.938,1.88),(.43,.008,.40),art,.001)
box('Kompozycja granat',(.25,1.937,1.81),(.39,.008,.25),fabric,.001)
box('Drzwi dekoracyjne',(-1.75,-1.981,1.025),(.82,.035,2.05),oak,.008)
box('Klamka',(-1.45,-1.92,1.0),(.12,.07,.035),gold,.01)
cyl('Lampa sufitowa',(0,0,2.62),.24,.07,white)
scene=bpy.context.scene; scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1
scene.world.color=(.35,.35,.35)
def light(name,loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.shape='DISK'; o.data.size=size
light('Światło sufitowe',(0,0,2.55),180,3)
light('Światło okna',(-2.3,0,2.1),220,2); bpy.context.object.rotation_euler=(Vector((0,0,1))-bpy.context.object.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(-1.9,-1.6,1.7)); cam=bpy.context.object; cam.rotation_euler=(Vector((.3,.8,1))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=20; scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=32; scene.cycles.use_denoising=True
scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.render.filepath=os.path.join(ROOT,'podglad.png')
meshes=[o for o in scene.objects if o.type=='MESH']; triangles=sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons)
with open(os.path.join(ROOT,'model-info.json'),'w',encoding='utf8') as f: json.dump({'meshes':len(meshes),'triangles':triangles,'room_m':[5,4,2.7]},f,indent=2)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'Pokoj_VR.blend'))
bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,'dist','pokoj.glb'),export_format='GLB',export_cameras=False,export_lights=False)
bpy.ops.render.render(write_still=True)
