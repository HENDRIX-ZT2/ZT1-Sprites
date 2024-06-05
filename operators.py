import bpy

from core import *


class OBJECT_OT_ZT1RenderGeneratePalette(bpy.types.Operator):
	bl_idname = "render.zt1generatepalette"
	bl_label = "Generate Color Palette"

	def execute(self, context):
		generate_palette()
		return {'FINISHED'}


class OBJECT_OT_ZT1RenderButtonConvert(bpy.types.Operator):
	bl_idname = "render.zt1spritesconvert"
	bl_label = "Convert Sprites to ZT1 Graphics"

	def execute(self, context):
		convert_sprites()
		return {'FINISHED'}


class OBJECT_OT_ZT1RenderButtonBatch(bpy.types.Operator):
	bl_idname = "render.zt1spritesbatch"
	bl_label = "Render All Sprites"

	def execute(self, context):
		render_sprites(batch=True)
		return {'FINISHED'}


class OBJECT_OT_ZT1RenderButtonCurrent(bpy.types.Operator):
	bl_idname = "render.zt1spritescurrent"
	bl_label = "Render Current Anim"

	def execute(self, context):
		render_sprites(batch=False)
		return {'FINISHED'}


class OBJECT_OT_ZT1BlockX(bpy.types.Operator):
	bl_idname = "render.zt1blockx"
	bl_label = "Mute X"

	def execute(self, context):
		lock_channels(0)
		return {'FINISHED'}


class OBJECT_OT_ZT1BlockY(bpy.types.Operator):
	bl_idname = "render.zt1blocky"
	bl_label = "Mute Y"

	def execute(self, context):
		lock_channels(1)
		return {'FINISHED'}


class OBJECT_OT_ZT1BlockZ(bpy.types.Operator):
	bl_idname = "render.zt1blockz"
	bl_label = "Mute Z"

	def execute(self, context):
		lock_channels(2)
		return {'FINISHED'}


class OBJECT_OT_ZT1RemapTime(bpy.types.Operator):
	bl_idname = "render.zt1remaptime"
	bl_label = "Remap Action Time"

	def execute(self, context):
		remap_action_time()
		return {'FINISHED'}
