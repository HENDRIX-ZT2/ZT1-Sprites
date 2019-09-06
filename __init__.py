bl_info = {	"name": "Render ZT1 Sprites",
			"author": "HENDRIX",
			"blender": (2, 80, 0),
			"location": "Render > ZT1 Sprites",
			"description": "Sets up and renders sprites for all animations, for all angles.",
			"warning": "",
			"wiki_url": "https://github.com/HENDRIX-ZT2/ZT1-Sprites",
			"support": 'COMMUNITY',
			"tracker_url": "https://github.com/HENDRIX-ZT2/ZT1-Sprites/issues/new",
			"category": "Render"}
import bpy
from bpy.props import CollectionProperty

import mathutils
import math
import os
import time
import subprocess

def create_ob(ob_name, ob_data):
	ob = bpy.data.objects.new(ob_name, ob_data)
	bpy.context.scene.collection.objects.link(ob)
	bpy.context.view_layer.objects.active = ob
	return ob
	
def mesh_from_data(name, verts, faces, wireframe = True):
	me = bpy.data.meshes.new(name)
	me.from_pydata(verts, [], faces)
	me.update()
	ob = create_ob(name, me)
	if wireframe:
		ob.display_type = 'WIRE'
	return ob, me
	
def create_empty(parent,name,matrix):
	empty = create_ob(name, None)
	if parent:
		empty.parent = parent
	empty.matrix_local = matrix
	empty.empty_display_type="ARROWS"
	return empty
	
def create_boolean(size):
	#faces with inverted normals for the boolean
	ob, me = mesh_from_data("boolean", 
							[(1.0, 1.0, -2.0),
							 (1.0, -1.0, -2.0),
							 (-1.0, -1.0, -2.0),
							 (-1.0, 1.0, -2.0),
							 (1.0, 1.0, 0.0),
							 (1.0, -1.0, 0.0),
							 (-1.0, -1.0, 0.0),
							 (-1.0, 1.0, 0.0) ],
							 [(0, 3, 2, 1),
							 (4, 5, 6, 7),
							 (0, 1, 5, 4),
							 (1, 2, 6, 5),
							 (2, 3, 7, 6),
							 (4, 7, 3, 0)])
	ob.scale = ((size, size, size))
	return ob
	
def create_shadow(size):
	shadowname = "shadow"
	ob, me = mesh_from_data(shadowname, 
							((1,1,0), (1,-1,0), (-1,1,0), (-1,-1,0)),
							((2,3,1,0),) )
	ob.scale = ((size, size, size))
	if shadowname not in bpy.data.materials:
		mat = bpy.data.materials.new(shadowname)
		ob.cycles.is_shadow_catcher = True
		ob.cycles_visibility.camera = True
		ob.cycles_visibility.glossy = False
		ob.cycles_visibility.scatter = False
		ob.cycles_visibility.diffuse = False
		ob.cycles_visibility.transmission = False
		ob.cycles_visibility.shadow = False
	else: mat = bpy.data.materials[shadowname]
	me.materials.append(mat)
	me.polygons[0].material_index = 0
	return ob
	
def create_camera(matrix):
	camd = bpy.data.cameras.new("CAMERA")
	camd.type = "ORTHO"
	ob = create_ob("CAMERA", camd)
	ob.matrix_local = matrix
	bpy.context.scene.camera = ob
	print("created camera")
	return ob

def create_light(matrix, lamptype="AREA"):
	lampd = bpy.data.lights.new(lamptype, lamptype)
	ob = create_ob(lamptype, lampd)
	ob.matrix_local = matrix
	print("created lamp",lamptype)
	return ob

def clear_scene():
	#set the visible layers for this scene
	# bpy.context.scene.layers = [True for i in range(0,20)]
	bpy.ops.object.select_all(action='SELECT')
	bpy.ops.object.delete(use_global=True)
	for cat in (bpy.data.objects, bpy.data.materials, bpy.data.textures, bpy.data.images, bpy.data.armatures, bpy.data.actions):
		for thing in cat:
			if not "icon" in thing.name:
				thing.user_clear()
				cat.remove(thing)
			
def remap_action_time():
	fac = bpy.context.scene.render.frame_map_new / bpy.context.scene.render.frame_map_old
	for action in bpy.data.actions:
		for group in action.groups:
			for fcurve in group.channels:
				for i in range(0, len(fcurve.keyframe_points)):
					fcurve.keyframe_points[i].co[0] *= fac
	bpy.context.scene.render.fps = bpy.context.scene.render.frame_map_new
	bpy.context.scene.render.frame_map_new = 100
	bpy.context.scene.render.frame_map_old = 100
	
def setup_compositor_nodes():
	# switch on nodes and get reference
	print("Setting up compositing nodes to fix alpha")
	bpy.context.scene.use_nodes = True
	bpy.context.scene.render.use_compositing = True
	tree = bpy.context.scene.node_tree

	# clear default nodes
	for node in tree.nodes:
		tree.nodes.remove(node)

	#create nodes
	CompositorNodeRLayers = tree.nodes.new('CompositorNodeRLayers')
	CompositorNodeMath = tree.nodes.new('CompositorNodeMath')
	CompositorNodeMath.operation = "GREATER_THAN"
	CompositorNodeMath.inputs[1].default_value = 0.5
	CompositorNodeSetAlpha = tree.nodes.new('CompositorNodeSetAlpha')
	CompositorNodeAlphaOver = tree.nodes.new('CompositorNodeAlphaOver')
	CompositorNodeAlphaOver.inputs[1].default_value = [ 0.0, 1.0, 0.0, 1.0]
	CompositorNodeAlphaOver.premul = 0
	CompositorNodeAlphaOver.use_premultiply = True
	CompositorNodeComposite = tree.nodes.new('CompositorNodeComposite')   

	# link nodes
	links = tree.links
	link = links.new(CompositorNodeRLayers.outputs[0], CompositorNodeSetAlpha.inputs[0])
	link = links.new(CompositorNodeRLayers.outputs[1], CompositorNodeMath.inputs[0])
	link = links.new(CompositorNodeMath.outputs[0], CompositorNodeSetAlpha.inputs[1])
	link = links.new(CompositorNodeSetAlpha.outputs[0], CompositorNodeAlphaOver.inputs[2])
	link = links.new(CompositorNodeAlphaOver.outputs[0], CompositorNodeComposite.inputs[0])

	#set position
	x = 0
	for node in tree.nodes:
		node.location = x,0
		x+=200
		
def render_sprites(batch=False):
	t_start = time.clock()
	
	safety = 2
	print("Starting sprite rendering")
	# get the max object dimensions for the camera scale
	#should this be fixed so that tiles are always 256*256?
	obs = []
	xmin,xmax,ymin,ymax,zmin,zmax = 1000,-1000,1000,-1000,1000,-1000
	for ob in bpy.data.objects:
		#test against colliders
		if type(ob.data) == bpy.types.Mesh:
			if "capsule" in ob.name: continue
			if "orientedbox" in ob.name: continue
			if "sphere" in ob.name: continue
			if "shadow" in ob.name: continue
			if "particle" in ob.name: continue
			if "boolean" in ob.name: continue
			
			for v in ob.data.vertices:
				p = ob.matrix_world @ v.co
				xmax = max(xmax, p[0])
				ymax = max(ymax, p[1])
				zmax = max(zmax, p[2])
				xmin = min(xmin, p[0])
				ymin = min(ymin, p[1])
				zmin = min(zmin, p[2])
			obs.append(ob)
	size = max(xmax-xmin, ymax-ymin, zmax-zmin)
	print("Maximum extent:",size)
	#capture twice as much as the dimension to make sure everything is rendered
	size *= safety
	#print(size)
	print("Render Area:",size)
	print("Render Size:",16 * size)
	
	render = bpy.context.scene.render
	#16 pixels correspond to 1 ingame meter
	render.resolution_x = 16 * size
	render.resolution_y = 16 * size
	render.resolution_percentage = 100
	#render.use_file_extension
	render.image_settings.file_format = "PNG"
	render.image_settings.color_mode = "RGB"
	# render.use_antialiasing = False
	render.film_transparent = True
	render.engine = "Cycles"
	
	#alpha handling
	#maybe put it in its own button, if somebody wants to alter the nodes
	if not bpy.context.scene.use_nodes:
		setup_compositor_nodes()
	
	dir_root = render.filepath
	
	matrix = mathutils.Euler((math.radians(45), math.radians(0), math.radians(0))).to_matrix().to_4x4()
	matrix.translation = mathutils.Vector((0, -10, 10))
	
	if "CAMERA" not in bpy.data.cameras:
		camera = create_camera(matrix).data
	else:
		camera = bpy.data.cameras["CAMERA"]
	camera.ortho_scale = size
	
	matrix = mathutils.Matrix()
	matrix.translation = mathutils.Vector((0, 0, 10))
	
	if "AREA" not in bpy.data.lights:
		hemi = create_light(matrix)
		hemi.data.use_shadow = False
	if "SUN" not in bpy.data.lights:
		sun = create_light(matrix, lamptype = "SUN")
		# sun.data.shadow_method = "RAY_SHADOW"
		# sun.data.use_only_shadow = True
		sun.data.shadow_buffer_soft = 0.0
	if "shadow" not in bpy.data.objects:
		shadow = create_shadow(size)
	else:
		shadow = bpy.data.objects["shadow"]
	if "boolean" not in bpy.data.objects:
		boolean = create_boolean(size)
	else:
		boolean = bpy.data.objects["boolean"]
	for ob in obs:
		if "cutout" not in ob.modifiers:
			mod = ob.modifiers.new('cutout', 'BOOLEAN')
			mod.object = boolean
			mod.operation = "DIFFERENCE"
	
	
	#get the reoot object
	roots = get_roots()
	if len(roots)!=1:
		root = create_empty(None, 'Auto Root', mathutils.Matrix())
		for ob in roots:
			ob.parent = root
	else:
		root = roots[0]
	
	render_actions = []
	for armature in bpy.data.objects:
		if type(armature.data) == bpy.types.Armature:
			#render each animation
			if batch:
				render_actions = [action for action in bpy.data.actions]
			#render the current animation
			else:
				render_actions = [armature.animation_data.action, ]
			break
			
	#if it is an object, it doesn't need shadows, and different rotations
	if not render_actions:
		boolean.rotation_euler = mathutils.Euler((0, 0, 0))
		boolean.location[2] = -0.1
		shadow.location[2] = -1000
		
		#for each view, render the sprites
		views = (("SW0000",	-45),
				 ("SE0000", 45),
				 ("NW0000",	-135),
				 ("NE0000", 135),)
				 
		for view, rot in views:
			print(view,rot)
			root.rotation_euler[2] = math.radians(rot)
			render.filepath = os.path.join(dir_root, view)
			ret = bpy.ops.render.render(animation=False, write_still=True)
			
	#animated, different views, render the sprites
	else:
		views = (("S",	0),
				 ("SE", 45),
				 ("E",	90),
				 ("NE", 135),
				 ("N", 180))
		for action in render_actions:
			#set the duration for this animation
			bpy.context.scene.frame_start = action.frame_range[0]
			#skip the last frame, a to avoid looping issues and b because we don't need it anyway
			bpy.context.scene.frame_end = action.frame_range[1]-1
			
			armature.animation_data.action = action
			try:
				for buoy in ("Node_Buoy", "Bip01 Head", "Bip01", "d"):
					if buoy in armature.pose.bones:
						break
			except:
				print("There is no buoy or comparable node!")
				buoy = armature.pose.bones.keys()[0]
			matrix_final = armature.matrix_world @ armature.pose.bones[buoy].matrix
			
			#this means the underside will be drawn
			if "-" in action.name:
				boolean.rotation_euler = mathutils.Euler((0, math.radians(180), 0))
				boolean.location[2] = matrix_final.translation.z
				shadow.location[2] = -1000
				
			#this means the upper side will be drawn
			elif "+" in action.name:
				boolean.rotation_euler = mathutils.Euler((0, 0, 0))
				boolean.location[2] = matrix_final.translation.z
				shadow.location[2] = -1000
			#a subswim, ie. fully underwater MM anim. no shadow, no intersection
			elif "*" in action.name:
				boolean.rotation_euler = mathutils.Euler((0, 0, 0))
				boolean.location[2] = -1000
				shadow.location[2] = -1000
			#not a surface related anim, move boolean just below shadow
			else:
				boolean.rotation_euler = mathutils.Euler((0, 0, 0))
				boolean.location[2] = -0.1
				shadow.location[2] = 0
			
			# #only shadow
			# if "#" in action.name:
				# for ob in obs:
					# ob.data.materials[0].use_cast_shadows_only = True
			# else:
				# for ob in obs:
					# ob.data.materials[0].use_cast_shadows_only = False
				
			for view, rot in views:
				print(view,rot)
				root.rotation_euler[2] = math.radians(rot)
				outname = safename(action.name)
				render.filepath = os.path.join(dir_root, outname, view)
				ret = bpy.ops.render.render(animation=True)
	#reset in the end
	render.filepath = dir_root
	print("Rendered sprites in "+str(time.clock()-t_start)+" seconds.")
	
def safename(action):
	outname = action.replace("+","").replace("-","").replace("#","").replace("*","")
	if len(outname) > 8:
		outname = outname[0:8]
	return outname

def lock_channels(i):
	for action in bpy.data.actions:
		for group in action.groups:
			if group.name == "Bip01":
				translations = [fcurve for fcurve in group.channels if fcurve.data_path.endswith("location")]
				if translations:
					num_keys = min([len(channel.keyframe_points) for channel in translations])
					if num_keys >> 1:
						key1 = mathutils.Vector([fcurve.keyframe_points[0].co[1] for fcurve in translations]).length
						key2 =  mathutils.Vector([fcurve.keyframe_points[num_keys-1].co[1] for fcurve in translations]).length
						#see if difference between first and last frame's position is greater than 5% of first/last
						if not math.isclose(key1, key2, rel_tol=0.05):
							print(action,"moves forward, muting channels")
							for channel in group.channels:
								if "location" in channel.data_path:
									if channel.array_index == i:
										channel.mute = True
									else:
										channel.mute = False
									
def get_roots():
	roots=[]
	for ob in bpy.context.scene.objects:
		if type(ob.data) in (type(None), bpy.types.Armature, bpy.types.Mesh):
			if ob.parent==None:
				roots.append(ob)
	return roots
	
def create_palette(p_ffmpeg, p_in, p_palette):
	if bpy.data.actions:
	
		#use E by default as it shows most in virtually any case
		p_frames = os.path.join(p_in, "E")
	else:
		
		p_frames = os.path.join(p_in, "SE")
	ffmCMD = p_ffmpeg +" -v warning -i "+p_frames+"%04d.png -vf palettegen -y "+p_palette
	#print(ffmCMD)
	subprocess.check_call(ffmCMD)
	print("Saved Palette to",p_palette)
	
def palettize(p_ffmpeg, p_in, p_palette):
	#palette is second input
	for root, dirs, files in os.walk(p_in):
		for dir in dirs:
			for rot in ("E","SE","S","NE","N"):
				file_path = os.path.join(root, dir,rot)
				if os.path.isfile(file_path+"0000.png"):
					ffmCMD = p_ffmpeg + " -v warning -start_number 0 -i "+file_path+"%04d.png -i "+p_palette+" -lavfi paletteuse -start_number 0 -y "+file_path+"%04d.png"
					print("Indexing",file_path)
					subprocess.check_call(ffmCMD)

def find_palette_source(p_in, current_anim):
	#say the user specifies the root folder ie. wants a shared palette, where do we get the images from? -> walk
	
	#we try different ids to find the desired folder, but only return it if it contains png files matchin the id
	for id in ("E0000.png", "SE0000.png"):
		for root, dirs, files in os.walk(p_in):
			for file in files:
				p_file = os.path.join(root, file)
				if current_anim in p_file and id in p_file:
					return os.path.dirname(p_file)
	return "INVALID_PATH"
				
def generate_palette():
	p_ffmpeg = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
	p_in = os.path.normpath(bpy.context.scene.render.filepath)
	print("Processing",p_in)
	if os.path.isfile(p_ffmpeg):
		#could be m, f, y or shared ie. codename of the object/animal, or just 
		palette_key = os.path.basename(p_in)		
		p_palette = os.path.join(p_in, palette_key+".png")
		#print(p_palette)
		current_anim = ""
		for armature in bpy.data.objects:
			if type(armature.data) == bpy.types.Armature:
				current_anim = safename(armature.animation_data.action.name)
				break
		p_pal_gen = find_palette_source(p_in, current_anim)
		print("Going to create palette from",p_pal_gen)
		
		if os.path.isdir(p_pal_gen):
			create_palette(p_ffmpeg, p_pal_gen, p_palette)
			print("Created palette.")
		else:
			print("Could not find a palette source, can not index frames. Fallback to ZT Studio indexing - SLOW!")
	else:
		print("FFMPEG.exe is missing - can not convert sprites to indexed.")

def convert_sprites():

	p_ffmpeg = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
	p_ztstudio = os.path.join(os.path.dirname(__file__), "ZT Studio", "ZT Studio.exe")

	t_start = time.clock()
	#first, build a palette from current anim
	p_in = os.path.normpath(bpy.context.scene.render.filepath)
	print("Processing",p_in)
	if os.path.isfile(p_ffmpeg):
		#could be m, f, y or shared ie. codename of the object/animal, or just 
		palette_key = os.path.basename(p_in)		
		p_palette = os.path.join(p_in, palette_key+".png")
		
		#if there is a current anim, that's the starting point for palette generation
		current_anim = ""
		for armature in bpy.data.objects:
			if type(armature.data) == bpy.types.Armature:
				current_anim = safename(armature.animation_data.action.name)
				break
				
		#this assumes a palette has been created before
		if os.path.isfile(p_palette):
			palettize(p_ffmpeg, p_in, p_palette)
			print("Indexed sprites in "+str(time.clock()-t_start)+" seconds.")
		else:
			print("Could not find a palette source, can not index frames. Fallback to ZT Studio indexing - SLOW!")

		if os.path.isfile(p_ztstudio):
			print("Starting ZT Studio.")
			t_start = time.clock()
			command = p_ztstudio+" /convertfolder:"+str(int(1000/bpy.context.scene.render.fps))
			#command = p_ztstudio+' /editing.animationSpeed:'+str(int(1000/bpy.context.scene.render.fps))+' /paths.root:'+os.path.realpath(bpy.context.scene.render.filepath)+' /action.convertFolder.toZT1:'+os.path.realpath(bpy.context.scene.render.filepath)
			print(command)
			subprocess.check_call(command)
			print("Converted sprites to ZT1 in "+str(time.clock()-t_start)+" seconds.")
		else:
			print("ZT Sudio.exe is missing - can not convert indexed sprites to ZT1 graphic.")
	else:
		print("FFMPEG.exe is missing - can not convert sprites to indexed.")
		
		
'''UI STUFF'''
	
class ZT1RenderPanel(bpy.types.Panel):
	bl_label = "ZT1 Sprite Rendering"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"
 
	def draw(self, context):
		self.layout.operator("render.zt1spritesbatch", text='Render all Sprites', icon='RENDER_ANIMATION')
		self.layout.operator("render.zt1spritescurrent", text='Render Current Anim', icon='RENDER_ANIMATION')
		self.layout.operator("render.zt1generatepalette", text='Generate Color Palette')#, icon='RENDER_ANIMATION')
		self.layout.operator("render.zt1spritesconvert", text='Convert Sprites to ZT1')#, icon='RENDER_ANIMATION')
		self.layout.operator("render.zt1remaptime", text='Remap Action Time')#, icon='RENDER_ANIMATION')
		self.layout.operator("render.zt1blockx", text='Mute Bip01 X Movement')
		self.layout.operator("render.zt1blocky", text='Mute Bip01 Y Movement')
		self.layout.operator("render.zt1blockz", text='Mute Bip01 Z Movement')
		
class OBJECT_OT_ZT1RenderGeneratePalette(bpy.types.Operator):
	bl_idname = "render.zt1generatepalette"
	bl_label = "Generate Color Palette"
	def execute(self, context):
		generate_palette( )
		return{'FINISHED'}
		
class OBJECT_OT_ZT1RenderButtonConvert(bpy.types.Operator):
	bl_idname = "render.zt1spritesconvert"
	bl_label = "Convert Sprites to ZT1 Graphics"
	def execute(self, context):
		convert_sprites( )
		return{'FINISHED'}
		
class OBJECT_OT_ZT1RenderButtonBatch(bpy.types.Operator):
	bl_idname = "render.zt1spritesbatch"
	bl_label = "Render All Sprites"
	def execute(self, context):
		render_sprites(batch=True)
		return{'FINISHED'}
		
class OBJECT_OT_ZT1RenderButtonCurrent(bpy.types.Operator):
	bl_idname = "render.zt1spritescurrent"
	bl_label = "Render Current Anim"
	def execute(self, context):
		render_sprites(batch=False)
		return{'FINISHED'}
		
class OBJECT_OT_ZT1BlockX(bpy.types.Operator):
	bl_idname = "render.zt1blockx"
	bl_label = "Mute X"
	def execute(self, context):
		lock_channels(0)
		return{'FINISHED'}
		
class OBJECT_OT_ZT1BlockY(bpy.types.Operator):
	bl_idname = "render.zt1blocky"
	bl_label = "Mute Y"
	def execute(self, context):
		lock_channels(1)
		return{'FINISHED'}
		
class OBJECT_OT_ZT1BlockZ(bpy.types.Operator):
	bl_idname = "render.zt1blockz"
	bl_label = "Mute Z"
	def execute(self, context):
		lock_channels(2)
		return{'FINISHED'}

class OBJECT_OT_ZT1RemapTime(bpy.types.Operator):
	bl_idname = "render.zt1remaptime"
	bl_label = "Remap Action Time"
	def execute(self, context):
		remap_action_time()
		return{'FINISHED'}

def register():
	bpy.utils.register_class(OBJECT_OT_ZT1RenderButtonBatch)
	bpy.utils.register_class(OBJECT_OT_ZT1RenderButtonCurrent)
	bpy.utils.register_class(OBJECT_OT_ZT1RenderGeneratePalette)
	bpy.utils.register_class(OBJECT_OT_ZT1RenderButtonConvert)
	bpy.utils.register_class(OBJECT_OT_ZT1RemapTime)
	bpy.utils.register_class(OBJECT_OT_ZT1BlockX)
	bpy.utils.register_class(OBJECT_OT_ZT1BlockY)
	bpy.utils.register_class(OBJECT_OT_ZT1BlockZ)
	bpy.utils.register_class(ZT1RenderPanel)

def unregister():
	bpy.utils.unregister_class(OBJECT_OT_ZT1RenderButtonBatch)
	bpy.utils.unregister_class(OBJECT_OT_ZT1RenderButtonCurrent)
	bpy.utils.unregister_class(OBJECT_OT_ZT1RenderGeneratePalette)
	bpy.utils.unregister_class(OBJECT_OT_ZT1RenderButtonConvert)
	bpy.utils.unregister_class(OBJECT_OT_ZT1RemapTime)
	bpy.utils.unregister_class(OBJECT_OT_ZT1BlockX)
	bpy.utils.unregister_class(OBJECT_OT_ZT1BlockY)
	bpy.utils.unregister_class(OBJECT_OT_ZT1BlockZ)
	bpy.utils.unregister_class(ZT1RenderPanel)

if __name__ == "__main__":
	register()