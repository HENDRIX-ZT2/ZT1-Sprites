bl_info = {
	"name": "Render ZT1 Sprites",
	"author": "HENDRIX",
	"blender": (2, 78, 0),
	"location": "Render > ZT1 Sprites",
	"description": "Sets up and renders sprites for all animations, for all angles.",
	"warning": "",
	"category": "Render"}

import bpy
from .operators import OBJECT_OT_ZT1RenderGeneratePalette, OBJECT_OT_ZT1RenderButtonConvert, \
	OBJECT_OT_ZT1RenderButtonBatch, OBJECT_OT_ZT1RenderButtonCurrent, OBJECT_OT_ZT1BlockX, OBJECT_OT_ZT1BlockY, \
	OBJECT_OT_ZT1BlockZ, OBJECT_OT_ZT1RemapTime
from .panels import ZT1RenderPanel


classes = (
	OBJECT_OT_ZT1RenderButtonBatch,
	OBJECT_OT_ZT1RenderButtonCurrent,
	OBJECT_OT_ZT1RenderGeneratePalette,
	OBJECT_OT_ZT1RenderButtonConvert,
	OBJECT_OT_ZT1RemapTime,
	OBJECT_OT_ZT1BlockX,
	OBJECT_OT_ZT1BlockY,
	OBJECT_OT_ZT1BlockZ,
	ZT1RenderPanel
)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)


if __name__ == "__main__":
	register()
