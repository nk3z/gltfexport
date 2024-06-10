bl_info = {
    "name": "GLTF Export",
    "author": "n4k3z",
    "version": (1, 0),
    "blender": (2, 93, 0),
    "location": "View3D > Sidebar",
    "description": "Export addon for GLTF",
    "category": "Export",
}

import bpy
from .gltfexport import ExportPanel, SelectExportPathOperator, ExportSelectedObjectsOperator, ExportCollectionsOperator

def register():
    bpy.utils.register_class(SelectExportPathOperator)
    bpy.utils.register_class(ExportSelectedObjectsOperator)
    bpy.utils.register_class(ExportCollectionsOperator)
    bpy.utils.register_class(ExportPanel)

    bpy.types.Scene.export_path = bpy.props.StringProperty(name="Ruta de exportación", default="", subtype='DIR_PATH')
    bpy.types.Scene.export_name = bpy.props.StringProperty(name="Nombre", default="selected_objects")
    bpy.types.Scene.apply_modifiers = bpy.props.BoolProperty(name="Aplicar modificadores", default=False)
    bpy.types.Scene.make_instances_real = bpy.props.BoolProperty(name="Make Instances Real", default=False)
    bpy.types.Scene.export_selected_only = bpy.props.BoolProperty(name="Seleccionados", default=False)
    bpy.types.Scene.export_individual = bpy.props.BoolProperty(name="Individuales", default=False)
    bpy.types.Scene.delete_after_export = bpy.props.BoolProperty(name="Borrar objetos", default=False)
    bpy.types.Scene.export_panel_mode = bpy.props.EnumProperty(
        name="Panel",
        items=[
            ("OBJECTS", "Objetos", ""),
            ("COLLECTIONS", "Colecciones", "")
        ],
        default="OBJECTS"
    )
    bpy.types.Scene.show_object_panel = bpy.props.BoolProperty(name="Mostrar panel de objetos", default=True)

def unregister():
    bpy.utils.unregister_class(SelectExportPathOperator)
    bpy.utils.unregister_class(ExportSelectedObjectsOperator)
    bpy.utils.unregister_class(ExportCollectionsOperator)
    bpy.utils.unregister_class(ExportPanel)

    del bpy.types.Scene.export_path
    del bpy.types.Scene.export_name
    del bpy.types.Scene.apply_modifiers
    del bpy.types.Scene.make_instances_real
    del bpy.types.Scene.export_selected_only
    del bpy.types.Scene.export_individual
    del bpy.types.Scene.delete_after_export
    del bpy.types.Scene.export_panel_mode
    del bpy.types.Scene.show_object_panel

if __name__ == "__main__":
    register()
