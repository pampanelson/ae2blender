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



class CreateCameraByAEOperator(bpy.types.Operator):
    bl_idname = "object.createcamerabyae"
    bl_label = "Create Camera By AE"
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.


    def execute(self, context):
        scene = context.scene
        for obj in scene.objects:
            obj.location.x += 1.0

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
        row.operator("object.createcamerabyae",text="Create Camera",icon="CAMERA_DATA")


        layout.label(text=" Hello Pampa!")



def register():
    ...
    print("hello pampa")

    bpy.utils.register_class(CreateCameraByAEOperator)

    bpy.utils.register_class(AE2BlenderPanel)


def unregister():
    ...
    print("bye pampa")

    bpy.utils.unregister_class(CreateCameraByAEOperator)

    bpy.utils.unregister_class(AE2BlenderPanel)



# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()