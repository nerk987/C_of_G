bl_info = {
    "name": "C_of_G",
    "author": "Ian Huish",
    "version": (1, 0),
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

handler_key = "C_OF_G_Handler"
handler_ov_key = "C_OF_G_OV_Handler"

# def new_blend_handler():
    # print("C_of_G File Handler")
    # if handler_key not in driver_namespace:
        # scene_update_post.append(frame_handler)
        # driver_namespace[handler_key] = frame_handler
    

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
        COG_Empty.location = COG_loc + Rig_obj.location
    
    if COGF_Empty != None:
        root_bone = Rig_obj.pose.bones.get("root")
        if root_bone != None:
            COG_loc[2] = root_bone.location[2]
        COGF_Empty.location = COG_loc + Rig_obj.location
        
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
    
    def CalcMass(self, def_bone):
        boneMass = 0.0
        boneName = def_bone.name.lower()
        #print("Calcmass name", def_bone.name, boneName)
        if "arm" in boneName:
            boneMass = 0.2
            #print("Adding arm", boneName)
        elif "leg" in boneName:
            boneMass = 0.3
        elif "thigh" in boneName:
            boneMass = 0.3
        elif "shin" in boneName:
            boneMass = 0.25
        elif "spine" in boneName:
            boneMass = 1
        elif "chest" in boneName:
            boneMass = 1
        elif "head" in boneName:
            boneMass = 0.9
        elif "neck" in boneName:
            boneMass = 0.2
        boneMass = boneMass * def_bone.length
        if boneMass > 0.0:
            def_bone["mass"] = boneMass


    def execute(self, context):

        #print("Mass Allocate")
        TargetRig = context.object
        if TargetRig.type != "ARMATURE":
            print("Not an Armature", context.object.type)
            return
        for bone in TargetRig.data.bones:
            if bone.use_deform:
                
                def_bone = TargetRig.pose.bones[bone.name]
                self.CalcMass(def_bone)

        return {'FINISHED'}

   

class ARMATURE_OT_add_COG(Operator):
    """Add the COG handler"""
    bl_idname = "armature.c_of_g"
    bl_label = "Track C_of_G"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # add_object(self, context)
        #print("C_of_G Called")
        
        #Check that an armature is selected
        TargetRig = context.object
        if TargetRig.type != "ARMATURE":
            print("Not an Armature", context.object.type)
            return
       
        if (bpy.data.objects.get("COG_Empty") is None) and (bpy.data.objects.get("COGF_Empty") is None): 
       #Create the COG Empty if it does exist
            if bpy.data.objects.get("COG_Empty") is None:
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
        return context.mode in {'OBJECT', 'POSE'}

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
