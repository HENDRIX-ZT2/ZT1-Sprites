import bpy


class ZT1RenderPanel(bpy.types.Panel):
	bl_label = "ZT1 Sprite Rendering"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"

	def draw(self, context):
		self.layout.operator("render.zt1spritesbatch", text='Render all Sprites', icon='RENDER_ANIMATION')
		self.layout.operator("render.zt1spritescurrent", text='Render Current Anim', icon='RENDER_ANIMATION')
		self.layout.operator("render.zt1generatepalette", text='Generate Color Palette')  # , icon='RENDER_ANIMATION')
		self.layout.operator("render.zt1spritesconvert", text='Convert Sprites to ZT1')  # , icon='RENDER_ANIMATION')
		self.layout.operator("render.zt1remaptime", text='Remap Action Time')  # , icon='RENDER_ANIMATION')
		self.layout.operator("render.zt1blockx", text='Mute Bip01 X Movement')
		self.layout.operator("render.zt1blocky", text='Mute Bip01 Y Movement')
		self.layout.operator("render.zt1blockz", text='Mute Bip01 Z Movement')