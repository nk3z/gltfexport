import bpy
import os
from bpy.props import StringProperty, BoolProperty, EnumProperty

# Function to export collections
def export_collections(context):
    export_path = context.scene.export_path

    def checkAndExport(parentCollection):
        for child in parentCollection.children:
            if child.collection and not child.exclude:
                collection = child.collection
                if len(collection.objects) > 0:
                    exportMeshes(collection)
                checkAndExport(child)

    def exportMeshes(collection):
        for obj in bpy.data.objects:
            obj.select_set(False)

        if export_path:
            fullPath = os.path.join(export_path, f"{collection.name}.glb")
        else:
            fullPath = os.path.join(directoryPath, f"{collection.name}.glb")

        visibilityState = []

        for obj in collection.objects:
            visibilityState.append(obj.hide_get())
            obj.hide_set(False)
            obj.select_set(True)

        bpy.ops.export_scene.gltf(
            filepath=fullPath,
            export_format='GLB',
            use_selection=True,
            export_apply=context.scene.apply_modifiers,
            export_cameras=False,
            export_lights=False,
            export_materials="NONE",
            export_colors=False,
            export_animations=False,
            export_frame_range=False,
            export_force_sampling=False,
            export_nla_strips=False,
            export_anim_single_armature=False,
            export_reset_pose_bones=False,
            export_skins=False,
            export_morph=False,
            export_morph_normal=False,
        )

        for obj in collection.objects:
            obj.hide_set(visibilityState.pop(0))

    if context.scene.export_all_linked:
        export_linked_collections(context)
    else:
        checkAndExport(context.view_layer.layer_collection)

# Function to export linked collections
def export_linked_collections(context):
    export_path = context.scene.export_path
    linked_collections = [coll for coll in bpy.data.collections if coll.library]

    for collection in linked_collections:
        if len(collection.objects) > 0:
            exportLinkedMeshes(collection, context)

def exportLinkedMeshes(collection, context):
    # Create a new temporary collection in the current scene
    temp_collection = bpy.data.collections.new(name=f"Temp_{collection.name}")
    context.scene.collection.children.link(temp_collection)

    # Copy objects from the linked collection to the temporary collection
    for obj in collection.objects:
        temp_obj = obj.copy()
        temp_obj.data = obj.data.copy()
        context.scene.collection.objects.link(temp_obj)
        temp_collection.objects.link(temp_obj)

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # Select only the objects in the temporary collection
    for obj in temp_collection.objects:
        obj.select_set(True)

    # Generate the export path
    if context.scene.export_path:
        fullPath = os.path.join(context.scene.export_path, f"{collection.name}.glb")
    else:
        fullPath = os.path.join(directoryPath, f"{collection.name}.glb")

    # Export the temporary collection
    bpy.ops.export_scene.gltf(
        filepath=fullPath,
        export_format='GLB',
        use_selection=True,
        export_apply=context.scene.apply_modifiers,
        export_cameras=False,
        export_lights=False,
        export_materials="NONE",
        export_colors=False,
        export_animations=False,
        export_frame_range=False,
        export_force_sampling=False,
        export_nla_strips=False,
        export_anim_single_armature=False,
        export_reset_pose_bones=False,
        export_skins=False,
        export_morph=False,
        export_morph_normal=False,
    )

    # Remove the temporary collection and its objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in temp_collection.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(temp_collection)

# Export panel
class ExportPanel(bpy.types.Panel):
    bl_label = "Export Addon"
    bl_idname = "OBJECT_PT_export_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Export GLTF'

    def draw(self, context):
        layout = self.layout

        layout.prop(context.scene, "export_path", text="", icon='FILE_FOLDER')
        layout.prop(context.scene, "export_panel_mode", text="Mode")

        mode = context.scene.export_panel_mode

        if mode == "OBJECTS":
            box = layout.box()
            box.prop(context.scene, "export_name")
            box.prop(context.scene, "apply_modifiers", text="Apply Modifiers")
            box.prop(context.scene, "export_selected_only", text="Selected Only")
            box.prop(context.scene, "export_individual", text="Export Individually")
            box.prop(context.scene, "make_instances_real", text="Make Instances Real")
            box.prop(context.scene, "delete_after_export", text="Delete After Export")
            box.operator("object.export_selected_objects", text="Export")

        elif mode == "COLLECTIONS":
            box = layout.box()
            box.prop(context.scene, "apply_modifiers", text="Apply Modifiers")
            box.prop(context.scene, "export_all_linked", text="All Linked")
            box.operator("object.export_collections", text="Export")

# Operator to export selected objects
class ExportSelectedObjectsOperator(bpy.types.Operator):
    bl_idname = "object.export_selected_objects"
    bl_label = "Export"

    def execute(self, context):
        export_path = bpy.context.scene.export_path
        export_name = bpy.context.scene.export_name

        if bpy.context.scene.export_selected_only:
            selected_objects = bpy.context.selected_objects
        else:
            selected_objects = bpy.context.scene.objects

        bpy.ops.object.select_all(action='DESELECT')

        if bpy.context.scene.make_instances_real:
            bpy.ops.object.duplicates_make_real()

        if bpy.context.scene.export_individual:
            for obj in selected_objects:
                obj.select_set(True)
                if export_path:
                    fullPath = os.path.join(export_path, f"{obj.name}.glb")
                else:
                    fullPath = os.path.join(directoryPath, f"{obj.name}.glb")

                bpy.ops.export_scene.gltf(
                    filepath=fullPath,
                    export_format='GLB',
                    use_selection=True,
                    export_apply=context.scene.apply_modifiers,
                    export_materials='EXPORT',
                    export_cameras=False,
                    export_lights=False,
                )
                obj.select_set(False)

            if bpy.context.scene.delete_after_export:
                bpy.ops.object.select_all(action='DESELECT')
                for obj in selected_objects:
                    obj.select_set(True)
                bpy.ops.object.delete()
        else:
            for obj in selected_objects:
                obj.select_set(True)

            if export_path:
                fullPath = os.path.join(export_path, f"{export_name}.glb")
            else:
                fullPath = os.path.join(directoryPath, f"{export_name}.glb")

            bpy.ops.export_scene.gltf(
                filepath=fullPath,
                export_format='GLB',
                use_selection=True,
                export_apply=context.scene.apply_modifiers,
                export_materials='EXPORT',
                export_cameras=False,
                export_lights=False,
            )

            if bpy.context.scene.delete_after_export:
                bpy.ops.object.select_all(action='DESELECT')
                for obj in selected_objects:
                    obj.select_set(True)
                bpy.ops.object.delete()

        bpy.ops.object.select_all(action='DESELECT')

        return {'FINISHED'}

# Operator to export collections
class ExportCollectionsOperator(bpy.types.Operator):
    bl_idname = "object.export_collections"
    bl_label = "Export"

    def execute(self, context):
        export_collections(context)
        return {'FINISHED'}

# Operator to select export path
class SelectExportPathOperator(bpy.types.Operator):
    bl_idname = "object.select_export_path"
    bl_label = "Select Export Path"

    def execute(self, context):
        bpy.ops.wm.path_open(filepath=context.scene.export_path)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# Register classes and properties
def register():
    bpy.utils.register_class(ExportPanel)
    bpy.utils.register_class(ExportSelectedObjectsOperator)
    bpy.utils.register_class(ExportCollectionsOperator)
    bpy.utils.register_class(SelectExportPathOperator)
    
    bpy.types.Scene.export_path = StringProperty(
        name="Export Path",
        default="/select/path",
        subtype='DIR_PATH'
    )
    bpy.types.Scene.export_name = StringProperty(name="Name", default="")
    bpy.types.Scene.apply_modifiers = BoolProperty(name="Apply Modifiers", default=False)
    bpy.types.Scene.make_instances_real = BoolProperty(name="Make Instances Real", default=False)
    bpy.types.Scene.export_selected_only = BoolProperty(name="Selected Only", default=False)
    bpy.types.Scene.export_individual = BoolProperty(name="Export Individually", default=False)
    bpy.types.Scene.delete_after_export = BoolProperty(name="Delete After Export", default=False)
    bpy.types.Scene.export_panel_mode = EnumProperty(
        name="Mode",
        items=[
            ("OBJECTS", "Objects", ""),
            ("COLLECTIONS", "Collections", ""),
        ],
        default="OBJECTS"
    )
    bpy.types.Scene.export_all_linked = BoolProperty(name="All Linked", default=False)
    bpy.types.Scene.show_object_panel = BoolProperty(name="Show Object Panel", default=True)

# Unregister classes and properties
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
    del bpy.types.Scene.export_all_linked
    del bpy.types.Scene.show_object_panel

if __name__ == "__main__":
    register()
