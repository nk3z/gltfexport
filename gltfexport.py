import bpy
import os
from bpy.props import StringProperty, BoolProperty, EnumProperty

# Función para exportar colecciones
def export_collections(context):
    # Obtener la ruta de exportación ingresada en el campo de texto
    export_path = context.scene.export_path

    # Crear la función checkAndExport y llamarla con la colección principal
    def checkAndExport(parentCollection):
        for child in parentCollection.children:
            if child.collection and not child.exclude:
                collection = child.collection
                if len(collection.objects) > 0:
                    exportMeshes(collection)
                checkAndExport(child)

    # Crear la función exportMeshes para exportar objetos en una colección
    def exportMeshes(collection):
        # Deseleccionar todos los objetos
        for obj in bpy.data.objects:
            obj.select_set(False)

        # Generar la ruta completa del archivo GLB con el nombre de la colección
        if export_path:
            fullPath = os.path.join(export_path, f"{collection.name}.glb")
        else:
            fullPath = os.path.join(directoryPath, f"{collection.name}.glb")

        visiblityState = []

        # Loop a través de todos los objetos de la colección
        for obj in collection.objects:
            # Almacenar la visibilidad
            visiblityState.append(obj.hide_get())
            # Mostrar el objeto
            obj.hide_set(False)
            # Seleccionar el objeto
            obj.select_set(True)

        # Exportar objetos seleccionados como archivo GLB
        bpy.ops.export_scene.gltf(
            filepath=fullPath,
            export_format='GLB',
            use_selection=True,
            export_apply=context.scene.apply_modifiers,  # Aplicar o no los modificadores
            export_cameras=False,
            export_lights=False,
            export_materials = "NONE",
            export_colors = False,
            export_animations = False,
            export_frame_range = False,
            export_force_sampling = False,
            export_nla_strips = False,
            export_anim_single_armature = False,
            export_reset_pose_bones = False,
            export_skins = False,
            export_morph = False,
            export_morph_normal = False,
        )

        # Restaurar la visibilidad de los objetos
        for obj in collection.objects:
            obj.hide_set(visiblityState.pop(0))

    # Llamar a checkAndExport con la colección principal
    checkAndExport(context.view_layer.layer_collection)

# Panel de exportación
class ExportPanel(bpy.types.Panel):
    bl_label = "Export addon"
    bl_idname = "OBJECT_PT_export_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Export GLTF'

    def draw(self, context):
        layout = self.layout

        # Botón de selección de ruta
        layout.prop(context.scene, "export_path", text="", icon='FILE_FOLDER')

        layout.prop(context.scene, "apply_modifiers", text="Aplicar modificadores")

        # Agregar campo enumeración para seleccionar entre "Objetos" y "Colecciones"
        layout.prop(context.scene, "export_panel_mode", text="Panel")

        # Obtener el modo seleccionado
        mode = context.scene.export_panel_mode

        # Panel de Objetos
        if mode == "OBJECTS":
            box = layout.box()
            box.prop(context.scene, "export_name")
            box.prop(context.scene, "export_selected_only", text="Seleccionados")
            box.prop(context.scene, "export_individual", text="Individuales")
            box.prop(context.scene, "make_instances_real", text="Make Instances Real")
            box.prop(context.scene, "delete_after_export", text="Borrar objetos")
            box.operator("object.export_selected_objects", text="Exportar")

        # Panel de Colecciones
        elif mode == "COLLECTIONS":
            layout.operator("object.export_collections", text="Exportar")

# Operador para exportar objetos seleccionados
class ExportSelectedObjectsOperator(bpy.types.Operator):
    bl_idname = "object.export_selected_objects"
    bl_label = "Exportar"

    def execute(self, context):
        # Obtener la ruta de exportación ingresada en el campo de texto
        export_path = bpy.context.scene.export_path

        # Obtener el nombre de exportación ingresado en el campo de texto
        export_name = bpy.context.scene.export_name

        # Obtener la lista de objetos seleccionados según la opción elegida
        if bpy.context.scene.export_selected_only:
            selected_objects = bpy.context.selected_objects
        else:
            selected_objects = bpy.context.scene.objects

        # Deseleccionar todos los objetos
        bpy.ops.object.select_all(action='DESELECT')

        # Realizar "Make Instances Real" si está seleccionado
        if bpy.context.scene.make_instances_real:
            bpy.ops.object.duplicates_make_real()

        # Verificar si la casilla "Individuales" está activada
        if bpy.context.scene.export_individual:
            # Exportar objetos individualmente
            for obj in selected_objects:
                obj.select_set(True)  # Seleccionar un objeto a la vez
                # Generar la ruta completa del archivo GLB con el nombre del objeto
                if export_path:
                    fullPath = os.path.join(export_path, f"{obj.name}.glb")
                else:
                    fullPath = os.path.join(directoryPath, f"{obj.name}.glb")

                # Exportar el objeto actual como un archivo GLB
                bpy.ops.export_scene.gltf(
                    filepath=fullPath,
                    export_format='GLB',
                    use_selection=True,
                    export_apply=context.scene.apply_modifiers,
                    export_materials='EXPORT',
                    export_cameras=False,
                    export_lights=False,
                )
                obj.select_set(False)  # Deseleccionar el objeto

            # Borrar los objetos seleccionados si está seleccionado
            if bpy.context.scene.delete_after_export:
                bpy.ops.object.select_all(action='DESELECT')
                for obj in selected_objects:
                    obj.select_set(True)
                bpy.ops.object.delete()
        else:
            # Caso no individual: seleccionar todos los objetos a la vez
            for obj in selected_objects:
                obj.select_set(True)

            # Generar la ruta completa del archivo GLB con el nombre de exportación
            if export_path:
                fullPath = os.path.join(export_path, f"{export_name}.glb")
            else:
                fullPath = os.path.join(directoryPath, f"{export_name}.glb")

            # Exportar los objetos seleccionados como un archivo GLB
            bpy.ops.export_scene.gltf(
                filepath=fullPath,
                export_format='GLB',
                use_selection=True,
                export_apply=context.scene.apply_modifiers,  # Aplicar o no los modificadores
                export_materials='EXPORT',
                export_cameras=False,
                export_lights=False,
            )

            # Borrar los objetos seleccionados si está seleccionado
            if bpy.context.scene.delete_after_export:
                bpy.ops.object.select_all(action='DESELECT')
                for obj in selected_objects:
                    obj.select_set(True)
                bpy.ops.object.delete()

        # Deseleccionar todos los objetos después de la exportación
        bpy.ops.object.select_all(action='DESELECT')

        return {'FINISHED'}

# Operador para exportar colecciones
class ExportCollectionsOperator(bpy.types.Operator):
    bl_idname = "object.export_collections"
    bl_label = "Exportar"

    def execute(self, context):
        # Llamar a la función de exportación de colecciones
        export_collections(context)

        return {'FINISHED'}

# Operador para seleccionar la ruta de exportación
class SelectExportPathOperator(bpy.types.Operator):
    bl_idname = "object.select_export_path"
    bl_label = "Seleccionar ruta de exportación"

    def execute(self, context):
        bpy.ops.wm.path_open(filepath=context.scene.export_path)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# Registrar las clases y propiedades
def register():
    bpy.utils.register_class(ExportPanel)
    bpy.utils.register_class(ExportSelectedObjectsOperator)
    bpy.utils.register_class(ExportCollectionsOperator)
    bpy.utils.register_class(SelectExportPathOperator)
    
    # Establecer una ruta por defecto (por ejemplo, "/ruta/por/defecto")
    bpy.types.Scene.export_path = bpy.props.StringProperty(
        name="Ruta de exportación",
        default="/seleccionar/ruta",  # Aquí puedes definir la ruta por defecto que desees
        subtype='DIR_PATH'
    )
    
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

# Desregistrar las clases y propiedades
def unregister():
    bpy.utils.unregister_class(ExportPanel)
    bpy.utils.unregister_class(ExportSelectedObjectsOperator)
    bpy.utils.unregister_class(ExportCollectionsOperator)
    bpy.utils.unregister_class(SelectExportPathOperator)
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