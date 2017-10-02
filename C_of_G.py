bl_info = {
    "name": "C_of_G",
    "author": "Ian Huish",
    "version": (1, 1),
    "blender": (2, 78, 0),
    "location": "Toolshelf>Tools Tab",
    "description": "Tracks an armature's centre of gravity",
    "warning": "",
    "wiki_url": "",
    "category": "Armature",
    }


import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
import math
from bpy.app import driver_namespace
from bpy.app.handlers import frame_change_post
from bpy.app.handlers import scene_update_post
from bpy.app.handlers import load_post
from bpy.app.handlers import persistent
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty, StringProperty    

handler_key = "C_OF_G_Handler"
handler_ov_key = "C_OF_G_OV_Handler"

    

@persistent
def frame_handler(scene):
    #print("C_of_G Update", scene.frame_current)
    COG_Empty = bpy.data.objects.get("COG_Empty")
    COGF_Empty = bpy.data.objects.get("COGF_Empty")
    if (COG_Empty == None) and (COGF_Empty == None):
        return
    if COG_Empty != None:
        Rig_obj = bpy.data.objects.get(COG_Empty["RigName"])
    elif COGF_Empty != None:
        Rig_obj = bpy.data.objects.get(COGF_Empty["RigName"])
    
    if Rig_obj == None:
        return
        
    if Rig_obj.type != "ARMATURE":
        #print("Not an Armature", Rig_obj.type)
        return
    TotalMass = 0.0
    
    offset = Vector((0,0,0))
    
    for bone in Rig_obj.pose.bones:
        #print(bone.name)
        if bone.get("mass") is not None:
            if TotalMass == 0.0:
                COG_loc = bone.tail + (bone.head-bone.tail)/2.0
                TotalMass = bone["mass"]
            else:
                TotalMass = TotalMass + bone["mass"]
                COG_loc = COG_loc + ((bone.tail + (bone.head-bone.tail)/2.0)-COG_loc)*bone["mass"]/TotalMass
    
    if COG_Empty != None:
        if 'Offset' in COG_Empty:
            offset = Vector(COG_Empty["Offset"])
        COG_Empty.location = COG_loc + Rig_obj.location + offset
    
    if COGF_Empty != None:
        root_bone = Rig_obj.pose.bones.get("root")
        if root_bone != None:
            COG_loc[2] = root_bone.location[2]
        COGF_Empty.location = COG_loc + Rig_obj.location + offset
        
def RemoveHandler():
    #Scene upate handler
    if handler_key in driver_namespace:
        if driver_namespace[handler_key] in frame_change_post:
            frame_change_post.remove(driver_namespace[handler_key])
            #print("Handler Removed")
        if driver_namespace[handler_key] in scene_update_post:
            scene_update_post.remove(driver_namespace[handler_key])
            #print("Handler Removed")
        del driver_namespace[handler_key]
        

        
def AddHandler():
    RemoveHandler()
    #load the scene update handler
    scene_update_post.append(frame_handler)
    driver_namespace[handler_key] = frame_handler
    
        

class ARMATURE_OT_add_mass(Operator):
    """Allocate mass to deform bones"""
    bl_idname = "armature.add_mass"
    bl_label = "Add mass for C of G"
    bl_options = {'REGISTER', 'UNDO'}
    
    pArm = FloatProperty(name="Arm", description="Arm Mass", default=0.2)
    pLeg = FloatProperty(name="Leg", description="Leg Mass", default=0.3)
    pThigh = FloatProperty(name="Thigh", description="Thigh Mass", default=0.3)
    pShin = FloatProperty(name="Shin", description="Shin Mass", default=0.25)
    pSpine = FloatProperty(name="Spine", description="Spine Mass", default=1.0)
    pChest = FloatProperty(name="Chest", description="Chest Mass", default=1.0)
    pHead = FloatProperty(name="Head", description="Head Mass", default=0.92)
    pNeck = FloatProperty(name="Neck", description="Neck Mass", default=0.2)
    pHips = FloatProperty(name="Hips", description="Hips Mass", default=1.0)
    pPelvis = FloatProperty(name="Pelvis", description="Pelvis Mass", default=0.1)

    pTotal = FloatProperty(name="TotalMass", description="Total Mass Added", default=0.0)

    def draw(self, context):
        layout = self.layout
        layout.operator('screen.repeat_last', text="Repeat", icon='FILE_REFRESH' )
        
        layout.prop(self, "pArm")
        layout.prop(self, "pLeg")
        layout.prop(self, "pThigh")
        layout.prop(self, "pShin")
        layout.prop(self, "pSpine")
        layout.prop(self, "pChest")
        layout.prop(self, "pHead")
        layout.prop(self, "pNeck")
        layout.prop(self, "pHips")
        layout.prop(self, "pPelvis")
        row = layout.row()
        row.prop(self, "pTotal")

    def CalcMass(self, def_bone):
        boneMass = 0.0
        boneName = def_bone.name.lower()
        added = 0.0
        #print("Calcmass name", def_bone.name, boneName)
        if "arm" in boneName:
            boneMass = self.pArm
        elif "leg" in boneName:
            boneMass = self.pLeg
        elif "thigh" in boneName:
            boneMass = self.pThigh
        elif "shin" in boneName:
            boneMass = self.pShin
        elif "spine" in boneName:
            boneMass = self.pSpine
        elif "chest" in boneName:
            boneMass = self.pChest
        elif "head" in boneName:
            boneMass = self.pHead
        elif "neck" in boneName:
            boneMass = self.pNeck
        elif "hips" in boneName:
            boneMass = self.pHips
        elif "pelvis" in boneName:
            boneMass = self.pPelvis
        boneMass = boneMass * def_bone.length
        if boneMass > 0.0:
            def_bone["mass"] = boneMass
            added = boneMass
        return boneMass


    def execute(self, context):

        TargetRig = context.object
        if TargetRig.type != "ARMATURE":
            print("Not an Armature", context.object.type)
            return
        self.pTotal = 0.0
        for bone in TargetRig.data.bones:
            if bone.use_deform:
                def_bone = TargetRig.pose.bones[bone.name]
                self.pTotal += self.CalcMass(def_bone)
        return {'FINISHED'}

   

class ARMATURE_OT_add_COG(Operator):
    """Add the COG handler"""
    bl_idname = "armature.c_of_g"
    bl_label = "Track C_of_G"
    bl_options = {'REGISTER', 'UNDO'}

    #Property declaration
    pX_Offset = FloatProperty(name="X Offset", description="Offset in the X direction", default=0.0)
    pY_Offset = FloatProperty(name="Y Offset", description="Offset in the Y direction", default=0.0)
    pZ_Offset = FloatProperty(name="Z Offset", description="Offset in the Z direction", default=0.0)

    def draw(self, context):
        layout = self.layout
        layout.operator('screen.repeat_last', text="Repeat", icon='FILE_REFRESH' )

        layout.prop(self, "pX_Offset")
        layout.prop(self, "pY_Offset")
        layout.prop(self, "pZ_Offset")

    def execute(self, context):

        # add_object(self, context)
        
        #Check that an armature is selected
        TargetRig = context.object
        if TargetRig.type != "ARMATURE":
            print("Not an Armature", context.object.type)
            return
       
        #if (bpy.data.objects.get("COG_Empty") is None) and (bpy.data.objects.get("COGF_Empty") is None): 
       #Create the COG Empty if it does exist
        COG_Empty = bpy.data.objects.get("COG_Empty")
        if COG_Empty is None:
            COG_Empty = bpy.data.objects.new("COG_Empty", None)
            COG_Empty.empty_draw_type = "CONE"
            COG_Empty.empty_draw_size = 0.1
            COG_Empty.show_x_ray = 1
            COG_Empty.rotation_euler[0] = math.radians(-90.0)
            scene = bpy.context.scene
            scene.objects.link(COG_Empty)
            scene.update()
            #Add Custom property
            COG_Empty["RigName"] = TargetRig.name
        COG_Empty["Offset"] = [self.pX_Offset, self.pY_Offset, self.pZ_Offset]
                
       #Create the COGF Empty if it does exist and there is a root bone (The one on the floor!)
        if bpy.data.objects.get("COGF_Empty") is None:
            root_bone = TargetRig.data.bones.get("root")
            if root_bone != None:
                COGF_Empty = bpy.data.objects.new("COGF_Empty", None)
                COGF_Empty.empty_draw_type = "CONE"
                COGF_Empty.empty_draw_size = 0.1
                COGF_Empty.show_x_ray = 1
                COGF_Empty.rotation_euler[0] = math.radians(90.0)
                scene = bpy.context.scene
                scene.objects.link(COGF_Empty)
                scene.update()
                #Add Custom property
                COGF_Empty["RigName"] = TargetRig.name
                COG_Empty["Offset"] = [self.pX_Offset, self.pY_Offset, self.pZ_Offset]

             
        return {'FINISHED'}
        


        
#UI Panels

class ARMATURE_PT_add_COG(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "C_of_G"
    bl_idname = "ARMATURE_PT_add_COG"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Tools"
    #bl_context = "objectmode"
    @classmethod
    def poll(cls, context):
        return (context.mode in {'OBJECT', 'POSE'}) and (context.object.type == "ARMATURE")

    def draw(self, context):
        layout = self.layout

        obj1 = context.object

        # row = layout.row()
        # row.label(text="Active object is: " + obj1.name)
        row = layout.row()
        row.prop(obj1, "name")

        row = layout.row()
        row.operator("armature.add_mass")
        row = layout.row()
        row.operator("armature.c_of_g")
        


def register():
    bpy.utils.register_class(ARMATURE_OT_add_COG)
    bpy.utils.register_class(ARMATURE_OT_add_mass)
    bpy.utils.register_class(ARMATURE_PT_add_COG)
    AddHandler()


def unregister():
    RemoveHandler()
    bpy.utils.unregister_class(ARMATURE_OT_add_COG)
    bpy.utils.unregister_class(ARMATURE_OT_add_mass)
    bpy.utils.unregister_class(ARMATURE_PT_add_COG)


if __name__ == "__main__":
    register()
