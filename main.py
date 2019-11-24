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
import math
_Debug = True


# SET PROPERTIES

bpy.types.Scene.AEScale_property = bpy.props.FloatProperty(name = "AEScale", description = "Scale Value (higher scale = smaller values)", default = 100)
bpy.types.Scene.AEDist_property = bpy.props.FloatProperty(name = "AEDist", description = "Target Distance between positions", default = 1)
bpy.types.Scene.AERotation_property = bpy.props.EnumProperty(items = [('Orientation', 'Orientation', 'Set Orientation as Delta Rotation'), ('XYZ', 'XYZ', 'Set XYZ as Delta Rotation')], name = 'AERotation', default = 'Orientation')
bpy.types.Scene.AEPosition_property = bpy.props.EnumProperty(items = [('Match', 'Match', 'Match Position from Source'), ('Cursor', 'Cursor', 'Start Position from Cursor')], name = 'AEPosition', default = 'Match')
bpy.types.Scene.AEFrame_property = bpy.props.EnumProperty(items = [('Match', 'Match', 'Match Frame from Source'), ('Playhead', 'Playhead', 'Start Frame from Playhead')], name = 'AEFrame', default = 'Match')

bpy.types.Scene.AEm1x_property = bpy.props.FloatProperty(name = "AEm1x", description = "Marker 1 X position", default = 0)
bpy.types.Scene.AEm1y_property = bpy.props.FloatProperty(name = "AEm1y", description = "Marker 1 Y position", default = 0)
bpy.types.Scene.AEm1z_property = bpy.props.FloatProperty(name = "AEm1z", description = "Marker 1 Z position", default = 0)
bpy.types.Scene.AEm2x_property = bpy.props.FloatProperty(name = "AEm2x", description = "Marker 2 X position", default = 100)
bpy.types.Scene.AEm2y_property = bpy.props.FloatProperty(name = "AEm2y", description = "Marker 2 Y position", default = 0)
bpy.types.Scene.AEm2z_property = bpy.props.FloatProperty(name = "AEm2z", description = "Marker 2 Z position", default = 0)



def checkClipboard(self):
    clipboard = bpy.context.window_manager.clipboard
    if "Adobe After Effects" in clipboard and "End of Keyframe Data" in clipboard:
        return True
    else:
        self.report({'ERROR'}, "ERROR : Copy AfterEffects transform data into Clipboard first")





def applyTransformData(target):
    # Load string from Clipboard
    clipboard = bpy.context.window_manager.clipboard
    
    # Check if Keyframes should be offset by Playhead
    frameOffset = 0

    if bpy.context.scene.AEFrame_property == "Playhead":
        frameOffset = bpy.context.scene.frame_current
    
    if clipboard != "":
        # Parse Keyframe Data into new Variable, change capitalize e's for proper float parsing
        keyFrameData = clipboard.replace('e','E').split()
        
        # Set common variables
        wordNum = 0
        maxWords = len(keyFrameData)
        isLoop = 0

        scale = bpy.context.scene.AEScale_property 


        # Go through each word in keyFrame Data
        while wordNum < maxWords:
            
            if "Transform" in keyFrameData[wordNum]:
                wordNum += 1
                
                # Apply Rotation Keys (AfterEffect's 2D rotaiton/Z Axis)
                if "Rotation" in keyFrameData[wordNum]:
                    wordNum += 3
                    target.rotation_mode = 'YZX'
                    if keyFrameData[wordNum + 2].replace('.','',1).isdigit():
                        isLoop = 1
                        while isLoop == 1:
                            if keyFrameData[wordNum].replace('.','',1).isdigit():
                                t_rot = (target.rotation_euler.x, math.radians(-float(keyFrameData[wordNum + 1])), target.rotation_euler.z)
                                if bpy.context.scene.AERotation_property == "XYZ":
                                    target.delta_rotation_euler = (t_rot)
                                    target.keyframe_insert(data_path='delta_rotation_euler', frame = float(keyFrameData[wordNum]) + frameOffset, index = 1)
                                else:
                                    target.rotation_euler = (t_rot)
                                    target.keyframe_insert(data_path='rotation_euler', frame = float(keyFrameData[wordNum]) + frameOffset, index = 1)
                                    wordNum += 2
                            else:
                                isLoop = 0
                                wordNum -= 1
                    else:
                        t_rot = (target.rotation_euler.x, math.radians(-float(keyFrameData[wordNum])), target.rotation_euler.z)
                        if bpy.context.scene.AERotation_property == "XYZ":
                            target.delta_rotation_euler = (t_rot)
                        else:
                            target.rotation_euler = (t_rot)
                
                # Apply X Axis Rotation Keys
                if "X" in keyFrameData[wordNum] and "Rotation" in keyFrameData[wordNum + 1]:
                    wordNum += 4
                    target.rotation_mode = 'YZX'
                    if keyFrameData[wordNum + 2].replace('.','',1).isdigit():
                        isLoop = 1
                        while isLoop == 1:
                            if keyFrameData[wordNum].replace('.','',1).isdigit():
                                t_rot = (math.radians(-float(keyFrameData[wordNum + 1])), target.rotation_euler.y, target.rotation_euler.z)
                                if bpy.context.scene.AERotation_property == "XYZ":
                                    target.delta_rotation_euler = (t_rot)
                                    target.keyframe_insert(data_path='delta_rotation_euler', frame = float(keyFrameData[wordNum]) + frameOffset, index = 0)
                                else:
                                    target.rotation_euler = (t_rot)
                                    target.keyframe_insert(data_path='rotation_euler', frame = float(keyFrameData[wordNum]) + frameOffset, index = 0)
                                wordNum += 2
                            else:
                                isLoop = 0
                                wordNum -= 1
                    else:
                        t_rot = (math.radians(-float(keyFrameData[wordNum])), target.rotation_euler.y, target.rotation_euler.z)
                        if bpy.context.scene.AERotation_property == "XYZ":
                            target.delta_rotation_euler = (t_rot)
                        else:
                            target.rotation_euler = (t_rot)
                
                # Apply Scale Keys
                if "ScalE" in keyFrameData[wordNum]:
                    wordNum += 8
                    if keyFrameData[wordNum + 4].replace('.','',1).isdigit():
                        isLoop = 1
                        while isLoop == 1:
                            if keyFrameData[wordNum].replace('.','',1).isdigit():
                                target.scale.x = float(keyFrameData[wordNum + 1]) / scale
                                target.scale.y = float(keyFrameData[wordNum + 3]) / scale
                                target.scale.z = float(keyFrameData[wordNum + 2]) / scale
                                target.keyframe_insert(data_path='scale', frame = float(keyFrameData[wordNum]) + frameOffset)
                                wordNum += 4
                            else:
                                isLoop = 0
                                wordNum -= 1
                    else:
                        target.scale.x = float(keyFrameData[wordNum]) / scale
                        target.scale.y = float(keyFrameData[wordNum + 2]) / scale
                        target.scale.z = float(keyFrameData[wordNum + 1]) / scale
                        
                # Apply Position Keys
                if "Position" in keyFrameData[wordNum]:
                    wordNum += 8
                    if keyFrameData[wordNum + 4].replace('.','',1).isdigit():
                        isLoop = 1
                        x_o = 0
                        y_o = 0
                        z_o = 0
                        if bpy.context.scene.AEPosition_property == "Cursor":
                            x_o = bpy.context.scene.cursor_location.x - -float(keyFrameData[wordNum + 1]) / scale
                            y_o = bpy.context.scene.cursor_location.y - -float(keyFrameData[wordNum + 3]) / scale
                            z_o = bpy.context.scene.cursor_location.z - -float(keyFrameData[wordNum + 2]) / scale
                        while isLoop == 1:
                            if keyFrameData[wordNum].replace('.','',1).isdigit():
                                target.location.x = -float(keyFrameData[wordNum + 1]) / scale + x_o
                                target.location.y = -float(keyFrameData[wordNum + 3]) / scale + y_o
                                target.location.z = -float(keyFrameData[wordNum + 2]) / scale + z_o
                                target.keyframe_insert(data_path='location', frame = float(keyFrameData[wordNum]) + frameOffset)
                                wordNum += 4
                            else:
                                isLoop = 0
                                wordNum -= 1
                    else:
                        target.location.x = -float(keyFrameData[wordNum]) / scale
                        target.location.y = -float(keyFrameData[wordNum + 2]) / scale
                        target.location.z = -float(keyFrameData[wordNum + 1]) / scale
                
                # Apply Orientation Keys
                if "OriEntation" in keyFrameData[wordNum]:
                    wordNum += 4
                    target.rotation_mode = 'YZX'
                    x_p = 0
                    y_p = 0
                    z_p = 0
                    x_o = 0
                    y_o = 0
                    z_o = 0
                    if keyFrameData[wordNum + 3].replace('.','',1).isdigit():
                        isLoop = 1
                        while isLoop == 1:
                            if keyFrameData[wordNum].replace('.','',1).isdigit():
                                x_a = float(keyFrameData[wordNum + 1]) + x_o
                                y_a = float(keyFrameData[wordNum + 3]) + y_o
                                z_a = float(keyFrameData[wordNum + 2]) + z_o
                                if math.fabs(x_a - x_p) > 180:
                                    if x_a > x_p:
                                        x_a -= 360
                                        x_o -= 360
                                    else:
                                        x_a += 360
                                        x_o += 360
                                if math.fabs(y_a - y_p) > 180:
                                    if y_a > y_p:
                                        y_a -= 360
                                        y_o -= 360
                                    else:
                                        y_a += 360
                                        y_o += 360
                                if math.fabs(z_a - z_p) > 180:
                                    if z_a > z_p:
                                        z_a -= 360
                                        z_o -= 360
                                    else:
                                        z_a += 360
                                        z_o += 360
                                x_p = x_a
                                y_p = y_a
                                z_p = z_a
                                t_rot = (math.radians(-x_a), math.radians(-y_a), math.radians(-z_a))
                                if bpy.context.scene.AERotation_property == "Orientation":
                                    target.delta_rotation_euler = (t_rot)
                                    target.keyframe_insert(data_path='delta_rotation_euler', frame = float(keyFrameData[wordNum]) + frameOffset)
                                else:
                                    target.rotation_euler = (t_rot)
                                    target.keyframe_insert(data_path='rotation_euler', frame = float(keyFrameData[wordNum]) + frameOffset)
                                wordNum += 4
                            else:
                                isLoop = 0
                                wordNum -= 1
                    else:
                        t_rot = (math.radians(-float(keyFrameData[wordNum])), math.radians(-float(keyFrameData[wordNum + 2])), math.radians(-float(keyFrameData[wordNum + 1])))
                        if bpy.context.scene.AERotation_property == "Orientation":
                            target.delta_rotation_euler = (t_rot)
                        else:
                            target.rotation_euler = (t_rot)
                
                # Apply Y Rotation Keys
                if "Y" in keyFrameData[wordNum] and "Rotation" in keyFrameData[wordNum + 1]:
                    wordNum += 4
                    target.rotation_mode = 'YZX'
                    if keyFrameData[wordNum + 2].replace('.','',1).isdigit():
                        isLoop = 1
                        while isLoop == 1:
                            if keyFrameData[wordNum].replace('.','',1).isdigit():
                                t_rot = (target.rotation_euler.x, target.rotation_euler.y, math.radians(-float(keyFrameData[wordNum + 1])))
                                if bpy.context.scene.AERotation_property == "XYZ":
                                    target.delta_rotation_euler = (t_rot)
                                    target.keyframe_insert(data_path='delta_rotation_euler', frame = float(keyFrameData[wordNum]) + frameOffset, index = 2)
                                else:
                                    target.rotation_euler = (t_rot)
                                    target.keyframe_insert(data_path='rotation_euler', frame = float(keyFrameData[wordNum]) + frameOffset, index = 2)
                                wordNum += 2
                            else:
                                isLoop = 0
                                wordNum -= 1
                    else:
                        t_rot = (target.rotation_euler.x, target.rotation_euler.y, math.radians(-float(keyFrameData[wordNum])))
                        if bpy.context.scene.AERotation_property == "XYZ":
                            target.delta_rotation_euler = (t_rot)
                        else:
                            target.rotation_euler = (t_rot)
                
            wordNum += 1





class DebugOperator(bpy.types.Operator):
    bl_idname = "object.ae2blender_debug"
    bl_label = "Debug"
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.


    def execute(self, context):

        if checkClipboard(self):
            scene = context.scene
            for obj in scene.objects:
                obj.location.x += 1.0

        return {'FINISHED'}

class CreateCameraByAEOperator(bpy.types.Operator):
    bl_idname = "object.create_camera_by_ae"
    bl_label = "Create Camera"
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.


    def execute(self, context):
        if checkClipboard(self):
            # # Create Transform Object
            # bpy.ops.object.empty_add(type='PLAIN_AXES')

            # # not work for 2.81 ?? ----------------------   TODO
            # # target = bpy.context.object 
            # target = bpy.context.active_object
            # target.name = "Camera_Transform"
            
            # # Create Camera Object
            # bpy.ops.object.camera_add()
            # # camera = bpy.context.object
            # camera = bpy.context.active_object
            # t_rot = (math.radians(-90), math.radians(180), math.radians(0))
            # camera.rotation_mode = 'XYZ'
            # camera.rotation_euler = (t_rot)
            
            # # Parent Camera to Transform Object
            # # target.select = True
            # # camera.select = True
            # camera.select_set(state=True)

            # target.select_set(state=True)


            # # bpy.context.scene.objects.active = target
            # bpy.ops.object.parent_set()
            # # camera.select = False
            # camera.select_set(state=False)
            


            # **** add an empty and a camera , then set empty as parent of camera *****
            # add a camera
            cameraName = "CameraByAE"
            bpy.ops.object.camera_add()
            bpy.context.active_object.name = cameraName

            # set properties for camera
            camera = bpy.data.objects[cameraName]
            t_rot = (math.radians(-90), math.radians(180), math.radians(0))
            camera.rotation_mode = 'XYZ'
            camera.rotation_euler = (t_rot)


            # add an empty
            emptyName = "CameraByAE_Transform"            
            bpy.ops.object.empty_add(type='PLAIN_AXES')
            bpy.context.active_object.name = emptyName
            bpy.data.objects[emptyName].select_set(True)

            # set parent for camera 
            camera.select_set(True)

            bpy.ops.object.parent_set(type='OBJECT')


            # deselect camera
            bpy.data.objects[cameraName].select_set(False)

            # get empty to set after effects data  
            target = bpy.data.objects[emptyName]
            applyTransformData(target)

        return {'FINISHED'}

class CreatePlaneByAEOperator(bpy.types.Operator):
    bl_idname = "object.create_plane_by_ae"
    bl_label = "Create Plane"
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.


    def execute(self, context):


        return {'FINISHED'}


class CreateEmptyByAEOperator(bpy.types.Operator):
    bl_idname = "object.create_empty_by_ae"
    bl_label = "Create Empty"
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.


    def execute(self, context):

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
        # scene = context.scene


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