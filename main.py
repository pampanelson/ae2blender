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



# PASTE AE KEYFRAME DATA TO ALL SELECTED OBJECTS

def pasteKeyframesAE(self):
    if checkClipboard(self):
        for target in bpy.context.scene.objects:
            if target.select == 1:
                applyTransformData(target)


# CREATE AN EMPTY OBJECT WITH AE KEYFRAME DATA

def createEmptyAE(self):
    if checkClipboard(self):
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        target = bpy.context.object
        
        applyTransformData(target)

# CREATE A PLANE OBJECT WITH AE KEYFRAME DATA

def createPlaneAE(self):
    if checkClipboard(self):

        # **** add an empty and a plane , then set empty as parent of plane *****
        # add a plane
        planeName = "planeByAE"
        bpy.ops.mesh.primitive_plane_add()
        bpy.context.active_object.name = planeName

        # set properties for plane
        plane = bpy.data.objects[planeName]
        t_rot = (math.radians(-90), math.radians(180), math.radians(0))
        plane.rotation_mode = 'XYZ'
        plane.rotation_euler = (t_rot)
        width = 1
        height = 1
        # Find Width and Hieght from Clipbard
        clipboard = bpy.context.window_manager.clipboard
        if clipboard != "":
            keyFrameData = clipboard.split()
            wordNum = 0
            scale = bpy.context.scene.AEScale_property
            while wordNum < 30:
                if keyFrameData[wordNum] == "Width":
                    width = float(keyFrameData[wordNum + 1]) / scale
                if keyFrameData[wordNum] == "Height":
                    height = float(keyFrameData[wordNum + 1]) / scale
                wordNum += 1
        plane.scale.x = width / 2
        plane.scale.y = height / 2


        # add an empty
        emptyName = "planeByAE_Transform"            
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        bpy.context.active_object.name = emptyName
        bpy.data.objects[emptyName].select_set(True)

        # set parent for plane 
        plane.select_set(True)

        bpy.ops.object.parent_set(type='OBJECT')


        # deselect plane
        bpy.data.objects[planeName].select_set(False)

        # get empty to set after effects data  
        target = bpy.data.objects[emptyName]
        applyTransformData(target)



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



# SCALE CALCULATOR FUNCTIONS

def setMarker1AE(self):
    if checkClipboard(self):
        # Load string from Clipboard
        clipboard = bpy.context.window_manager.clipboard
        
        if clipboard != "":
            # Parse Keyframe Data into new Variable, change capitalize e's for proper float parsing
            keyFrameData = clipboard.replace('e','E').split()
            
            # Set common variables
            wordNum = 0
            maxWords = len(keyFrameData)
            isLoop = 0
            
            # Go through each word in keyFrame Data
            while wordNum < maxWords:
                
                if "Transform" in keyFrameData[wordNum]:
                    wordNum += 1
                    
                    if "Position" in keyFrameData[wordNum]:
                        wordNum += 8
                        if keyFrameData[wordNum + 3].replace('.','',1).isdigit():
                            bpy.context.scene.AEm1x_property = float(keyFrameData[wordNum + 1])
                            bpy.context.scene.AEm1y_property = float(keyFrameData[wordNum + 3])
                            bpy.context.scene.AEm1z_property = float(keyFrameData[wordNum + 2])
                        else:
                            bpy.context.scene.AEm1x_property = float(keyFrameData[wordNum])
                            bpy.context.scene.AEm1y_property = float(keyFrameData[wordNum + 2])
                            bpy.context.scene.AEm1z_property = float(keyFrameData[wordNum + 1])
                        
                wordNum += 1

def setMarker2AE(self):
    if checkClipboard(self):
        # Load string from Clipboard
        clipboard = bpy.context.window_manager.clipboard
        
        if clipboard != "":
            # Parse Keyframe Data into new Variable, change capitalize e's for proper float parsing
            keyFrameData = clipboard.replace('e','E').split()
            
            # Set common variables
            wordNum = 0
            maxWords = len(keyFrameData)
            isLoop = 0
            
            # Go through each word in keyFrame Data
            while wordNum < maxWords:
                
                if "Transform" in keyFrameData[wordNum]:
                    wordNum += 1
                    
                    if "Position" in keyFrameData[wordNum]:
                        wordNum += 8
                        if keyFrameData[wordNum + 3].replace('.','',1).isdigit():
                            bpy.context.scene.AEm2x_property = float(keyFrameData[wordNum + 1])
                            bpy.context.scene.AEm2y_property = float(keyFrameData[wordNum + 3])
                            bpy.context.scene.AEm2z_property = float(keyFrameData[wordNum + 2])
                        else:
                            bpy.context.scene.AEm2x_property = float(keyFrameData[wordNum])
                            bpy.context.scene.AEm2y_property = float(keyFrameData[wordNum + 2])
                            bpy.context.scene.AEm2z_property = float(keyFrameData[wordNum + 1])
                        
                wordNum += 1

def calculateScaleAE(self):
    m1x = bpy.context.scene.AEm1x_property
    m1y = bpy.context.scene.AEm1y_property
    m1z = bpy.context.scene.AEm1z_property
    m2x = bpy.context.scene.AEm2x_property
    m2y = bpy.context.scene.AEm2y_property
    m2z = bpy.context.scene.AEm2z_property
    
    x = 0
    y = 0
    z = 0
    
    if m1x > m2x:
        x = m1x - m2x
    else:
        x = m2x - m1x
    
    if m1y > m2y:
        y = m1y - m2y
    else:
        y = m2y - m1y
    
    if m1z > m2z:
        z = m1z - m2z
    else:
        z = m2z - m1z
    
    w = math.sqrt(x * x + y * y)
    distance = math.sqrt(w * w + z * z)
    
    bpy.context.scene.AEScale_property = distance / bpy.context.scene.AEDist_property



# ==========================================  Operators ==================
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
        createPlaneAE(self)
        return {'FINISHED'}


class CreateEmptyByAEOperator(bpy.types.Operator):
    bl_idname = "object.create_empty_by_ae"
    bl_label = "Create Empty"
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.


    def execute(self, context):

        return {'FINISHED'}


class A2BPasteAEFrameOperator(bpy.types.Operator):
    """Paste Keyframe Data to Selected Objects"""
    bl_idname = "object.ae_pastekeys_operator"
    bl_label = "AE Paste Keyframes Operator"

    def execute(self, context):
        pasteKeyframesAE(self)
        return {'FINISHED'}



class A2BSetMarker1Operator(bpy.types.Operator):
    """Set Values for Marker 1"""
    bl_idname = "object.ae_marker1_operator"
    bl_label = "AE Set Marker 1 Operator"

    def execute(self, context):
        setMarker1AE(self)
        return {'FINISHED'}

class A2BSetMarker2Operator(bpy.types.Operator):
    """Set Values for Marker 2"""
    bl_idname = "object.ae_marker2_operator"
    bl_label = "AE Set Marker 2 Operator"

    def execute(self, context):
        setMarker2AE(self)
        return {'FINISHED'}

class A2BSetScaleOperator(bpy.types.Operator):
    """Set Scale based on distance between Markers"""
    bl_idname = "object.ae_setscale_operator"
    bl_label = "AE Calculate Scale Operator"

    def execute(self, context):
        calculateScaleAE(self)
        return {'FINISHED'}


# ----------------------------------------------------------------------------


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

        # properties 
        row = layout.row()
        row.prop(context.scene, "AEScale_property", text = "Scale")
        
        row = layout.column(align=True)
        col = row.split(align=True)
        col.operator("object.ae_marker1_operator", text = "Marker 1")
        col.operator("object.ae_marker2_operator", text = "Marker 2")
        row.prop(context.scene, "AEDist_property", text = "Distance")
        row.operator("object.ae_setscale_operator", text = "Calculate Scale", icon = "DRIVER_DISTANCE")
        
        row = layout.row()
        row.label(text="Delta Rotation:")
        
        row = layout.row()
        row.prop(context.scene, "AERotation_property", expand=True)
        
        row = layout.row()
        row.label(text="Starting Position:")
        
        row = layout.row()
        row.prop(context.scene, "AEPosition_property", expand=True)
        
        row = layout.row()
        row.label(text="Starting Frame:")
        
        row = layout.row()
        row.prop(context.scene, "AEFrame_property", expand=True)
        
        row = layout.row()



        # buttons 
        row = layout.column(align=True)
        row.operator("object.create_camera_by_ae",text="Create Camera",icon="CAMERA_DATA")
        row.operator("object.create_empty_by_ae",text="Create Empty",icon="EMPTY_DATA")
        row.operator("object.create_plane_by_ae",text="Create Plane",icon="MESH_PLANE")

        if _Debug:
            row.operator("object.ae2blender_debug",text="Debug",icon="FUND")

        
        layout.label(text=" Hello Pampa!")



def register():
    ...
    print("hello pampa")

    bpy.utils.register_class(CreateCameraByAEOperator)
    bpy.utils.register_class(CreateEmptyByAEOperator)
    bpy.utils.register_class(CreatePlaneByAEOperator)

    bpy.utils.register_class(A2BPasteAEFrameOperator)
    bpy.utils.register_class(A2BSetMarker1Operator)
    bpy.utils.register_class(A2BSetMarker2Operator)
    bpy.utils.register_class(A2BSetScaleOperator)


    if _Debug:
        bpy.utils.register_class(DebugOperator)

    bpy.utils.register_class(AE2BlenderPanel)


def unregister():
    ...
    print("bye pampa")

    bpy.utils.unregister_class(CreateCameraByAEOperator)
    bpy.utils.unregister_class(CreateEmptyByAEOperator)
    bpy.utils.unregister_class(CreatePlaneByAEOperator)


    bpy.utils.unregister_class(A2BPasteAEFrameOperator)
    bpy.utils.unregister_class(A2BSetMarker1Operator)
    bpy.utils.unregister_class(A2BSetMarker2Operator)
    bpy.utils.unregister_class(A2BSetScaleOperator)



    if _Debug:
        bpy.utils.unregister_class(DebugOperator)

    bpy.utils.unregister_class(AE2BlenderPanel)



# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()