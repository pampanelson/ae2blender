# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "ae2blender",
    "author" : "pampa nelson",
    "description" : "import data from after effects into blender",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    # "location" : "View3D",
    "warning" : "",
    "category" : "Generic"
}

import bpy
_Debug = not True


class DebugOperator(bpy.types.Operator):
    bl_idname = "object.ae2blender_debug"
    bl_label = "Debug"
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.


    def execute(self, context):
        scene = context.scene
        for obj in scene.objects:
            obj.location.x += 1.0

        return {'FINISHED'}


class CreateCameraByAEOperator(bpy.types.Operator):
    bl_idname = "object.create_camera_by_ae"
    bl_label = "Create Camera"
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.


    def execute(self, context):
        ...
        return {'FINISHED'}

class CreatePlaneByAEOperator(bpy.types.Operator):
    bl_idname = "object.create_plane_by_ae"
    bl_label = "Create Plane"
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.


    def execute(self, context):
        ...
        return {'FINISHED'}


class CreateEmptyByAEOperator(bpy.types.Operator):
    bl_idname = "object.create_empty_by_ae"
    bl_label = "Create Empty"
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.


    def execute(self, context):
        ...
        return {'FINISHED'}



class AE2BlenderPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "AE 2 Blender"
    bl_idname = "SCENE_AE2BL_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self,context):
        layout = self.layout
        scene = context.scene


        row = layout.column(align=True)
        row.operator("object.create_camera_by_ae",text="Create Camera",icon="CAMERA_DATA")
        row.operator("object.create_empty_by_ae",text="Create Empty",icon="EMPTY_DATA")
        row.operator("object.create_plane_by_ae",text="Create Plane",icon="MESH_PLANE")

        if _Debug:
            row.operator("object.ae2blender_debug",text="Debug",icon="MESH_PLANE")

        
        layout.label(text=" Hello Pampa!")



def register():
    ...
    print("hello pampa")

    bpy.utils.register_class(CreateCameraByAEOperator)
    bpy.utils.register_class(CreateEmptyByAEOperator)
    bpy.utils.register_class(CreatePlaneByAEOperator)
    if _Debug:
        bpy.utils.register_class(DebugOperator)

    bpy.utils.register_class(AE2BlenderPanel)


def unregister():
    ...
    print("bye pampa")

    bpy.utils.unregister_class(CreateCameraByAEOperator)
    bpy.utils.unregister_class(CreateEmptyByAEOperator)
    bpy.utils.unregister_class(CreatePlaneByAEOperator)
    if _Debug:
        bpy.utils.unregister_class(DebugOperator)

    bpy.utils.unregister_class(AE2BlenderPanel)



# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()