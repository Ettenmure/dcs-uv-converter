bl_info = {
    "name": "DCS UV Converter",
    "author": "Ettenmure",
    "version": (0, 3, 0),
    "blender": (2, 93, 0),
    "location": "Scene Properties",
    "description": "Converts UV maps generated on ModelViewer 2 to an image format",
    "warning": "",
    "doc_url": "https://github.com/Ettenmure/dcs-uv-converter",
    "category": "UV",
}

import bpy
import os
import csv
import bmesh
import mathutils

import time

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )
from bpy_extras.io_utils import ImportHelper


# Runs the conversion when the button is pressed.
class DUCMain(Operator):
    """Begins the conversion process"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.duc_main"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Convert .csv"         # Display name in the interface.
    
    def execute(self, context):
        
        try: # Sets it to object mode.
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass
        
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        bpy.ops.object.duc_import_csv('INVOKE_DEFAULT') # Moves to the next step, importing.
        
        return {'FINISHED'}


# Imports the data from the .csv file
class DUCImportCSV(Operator, ImportHelper):
    """Imports the data"""
    bl_idname = "object.duc_import_csv"
    bl_label = "Import .csv"
    
    filter_glob: StringProperty(
        default='*.csv', # Restricts the selectable file type to .csv only.
        options={'HIDDEN'}
    )
    
    
    def execute(self, context):
        
        time_start = time.time()
        
        RawData = []
        # Imports the data from the .csv file and saves it in "RawData".
        with open(self.filepath) as f:
            reader = csv.reader(f)
            for row in reader:
                RawData.append(row)
        
        bpy.context.scene["RawData"] = RawData # Saves it to the scene so that the next class can use it.
        bpy.context.scene["DUCFilePath"] = self.filepath
        
        t1 = time.time() - time_start
#        print("---------------START---------------")
#        print("DUCImportCSV finished in %.4f sec" % (t1))
        
        bpy.context.scene["t1"] = t1
        
        bpy.ops.object.duc_treat_csv('INVOKE_DEFAULT') # Moves to the next step, treating the raw data.

        return {'FINISHED'} 


# Generates "vertices" and "faces" (vertex index list) from "RawData".
class DUCTreatCSV(Operator):
    """Treats the data"""
    bl_idname = "object.duc_treat_csv"
    bl_label = "Treat .csv"
    
    def execute(self, context):
        
        time_start = time.time()
        
        data = bpy.context.scene["RawData"]
        # Saves the size of the original image.
        hsize = float(data[1][0]) # Horizontal size of the texture.
        vsize = float(data[1][1]) # Vertical size of the texture.
        
        # Deletes the first two lines, they are no longer needed since they are not geometry.
        del data[0]
        del data[0]
        
        # Stores the length of data, which is the number of faces on the UV map multiplied by three.
        listlength = len(data)
        
        # Converts "data" to float triplets and stores it in "vertices".
        u = 0 # x coordinate.
        v = 0 # y coordinate.
        i = 0 # Counter for while loop.
        vertices = [(0,0,0)] * listlength # Creates and empty list for the while loop below that is the same length as "data".
        
        while i < listlength: # Writes the position of each vertex as a float and positions them properly.
            u = float(data[i][0])
            v = 1-float(data[i][1]) 
            # The 1- is there so the uv map is on the positive of the y and x axis and the proper orientation when looked from 
            # the top down view (Numpad 7).
            vertices[i] = (u,v,0)
            i +=1
        
        # Generates "faces", the vertex index list, that is a companion to "vertices".
        facesnumber = int(listlength/3) # The number of faces on the UV map is a third of the modified "data" list.
        faces = [(0,0,0)] * facesnumber # Generates an empty list the length of facesnumber.
        j = 0
        k = 0
        while j < facesnumber: # Populates "faces" with consecutive numbers.
            faces[j] = (k,k+1,k+2)
            j +=1
            k +=3
        
        bpy.context.scene["GenVertices"] = vertices # Saves it to the scene so that the other classes can use it.
        bpy.context.scene["GenFaces"] = faces
        bpy.context.scene["hsize"] = hsize
        bpy.context.scene["vsize"] = vsize
        
        t2 = time.time() - time_start
#        print("DUCTreatCSV  finished in %.4f sec" % (t2))
        
        bpy.context.scene["t2"] = t2
        
        bpy.ops.object.duc_mesh('INVOKE_DEFAULT') # Moves to the next step, generating the mesh.
        
        return {'FINISHED'}

# Creates a mesh from variables "vertices" and "faces".
class DUCMesh(Operator):
    """Generates the mesh"""
    bl_idname = "object.duc_mesh"
    bl_label = "Convert .csv"
    
    def execute(self, context):
        
        time_start = time.time()
        
        vertices = bpy.context.scene["GenVertices"]
        faces = bpy.context.scene["GenFaces"]
        
        # Creates the mesh from variables "vertices" and "faces".
        edges = []
        new_mesh = bpy.data.meshes.new('UV_Unwrap_PointCloud')
        new_mesh.from_pydata(vertices, edges, faces)
        new_mesh.update()
        new_object = bpy.data.objects.new('UV_Unwrap', new_mesh) # Makes object from mesh.
        new_collection = bpy.data.collections.new('Conversion finished') # Makes a collection.
        bpy.context.scene.collection.children.link(new_collection)
        new_collection.objects.link(new_object) # Adds object to the scene collection.
        
        ob = bpy.context.scene.objects["UV_Unwrap"]  # Gets the object
        bpy.ops.object.select_all(action='DESELECT') # Deselects all objects
        bpy.context.view_layer.objects.active = ob   # Makes "UV_Unwrap" the active object 
        ob.select_set(True)                          # Selects "UV_Unwrap"
        
        # Removes duplicate vertices.
        bpy.ops.object.mode_set(mode = 'EDIT')
        bm=bmesh.from_edit_mesh(bpy.context.active_object.data) 
        bmesh.ops.remove_doubles(bm, verts = bm.verts, dist = 0.00001)
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        # Adds a plane, used for trimming the excess mesh that falls outside of the texture bounds.
        bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0.5, 0.5, 0), scale=(1, 1, 1))
        
        # Joins the uv map and the plane.
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.join()
        
        # Trims the faces outside the texture bounds defined by the previously created plane.
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.mode_set(mode = 'EDIT')
        
        # Cuts through the texture bounds.
        # Each pair of coordinates from the arrays corresponds to one edge. (Left, Right, Top, Bottom)
        pco_array = [(0,0,0),(1,0,0),(0,1,0),(0,0,0)]
        pno_array = [(1,0,0),(1,0,0),(0,1,0),(0,1,0)]
        w = 0
        while w < 4: # Cuts the mesh along all four edges.
            bpy.ops.mesh.select_all(action='SELECT') # Selects every face
            bpy.ops.mesh.bisect(plane_co=pco_array[w], plane_no=pno_array[w], flip=False)  
            w +=1      
        
        bpy.ops.mesh.select_all(action = 'DESELECT')
        
        # Deletes every vertex outside the texture bounds.
        # Each triplet of values from the arrays corresponds to the outside of one edge. (Left, Right, Top, Bottom)
        bmv_array = [0,1,3,0]
        sign_array = ['POS','NEG','NEG','POS']
        axis_array = ['X','X','Y','Y']
        x = 0
        while x < 4:
            bm=bmesh.from_edit_mesh(bpy.context.active_object.data)
            bm.verts.ensure_lookup_table()
            bm.select_history.add(bm.verts[bmv_array[x]])
            bpy.ops.mesh.select_axis(orientation='GLOBAL', sign=sign_array[x], axis=axis_array[x], threshold=0.0001)
            bpy.context.tool_settings.mesh_select_mode = (True, False, False)
            bpy.ops.mesh.select_all(action='INVERT')
            bpy.ops.mesh.delete(type='VERT')
            x +=1
        
        bpy.ops.mesh.select_all(action='SELECT')
        
        t3 = time.time() - time_start
#        print("DUCMesh      finished in %.4f sec" % (t3))
        
        bpy.context.scene["t3"] = t3
        
        bpy.ops.object.duc_unwrap('INVOKE_DEFAULT') # Moves to the next step, unwrapping the mesh.
        
        return {'FINISHED'} 


# Unwraps the mesh.  
class DUCUnwrap(Operator):
    """Unwraps the mesh"""
    bl_idname = "object.duc_unwrap"
    bl_label = "Main"
    
    def execute(self, context):
        
        time_start = time.time()
        
        obj = context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        uv_layer = bm.loops.layers.uv.verify()

        for face in bm.faces: # adjust uv coordinates
            for loop in face.loops:
                loop_uv = loop[uv_layer]
                # use xy position of the vertex as a uv coordinate
                loop_uv.uv = loop.vert.co.xy

        bmesh.update_edit_mesh(me)
        
        # Moves the uv coordinates to align them with the uv map.
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        ob = bpy.context.active_object
        travec = mathutils.Vector((0.5, 0.5))

        for loop in ob.data.loops :
            ob.data.uv_layers.active.data[loop.index].uv = ob.data.uv_layers.active.data[loop.index].uv + travec
        
        t4 = time.time() - time_start
#        print("DUCUnwrap    finished in %.4f sec" % (t4))
        
        bpy.context.scene["t4"] = t4
        
        bpy.ops.object.duc_export('INVOKE_DEFAULT') # Moves to the next step, exporting the UV map.
        
        return {'FINISHED'}

# Exports the UV map.  
class DUCExport(Operator):
    """Exports the UV map"""
    bl_idname = "object.duc_export"
    bl_label = "Main"
    
    def execute(self, context):
        
        time_start = time.time()
        
        hsize = int(bpy.context.scene["hsize"])
        vsize = int(bpy.context.scene["vsize"])
                
        # Exports the texture on the same folder as the .csv file.
        expfilepath = bpy.context.scene["DUCFilePath"] # Gets the filepath of the .csv file.
        expfilepath = expfilepath[:-8] # Removes the last eight characters (.dds.csv).
        expfilepath = expfilepath + '_UV' # Adds _UV to the file name.

        bpy.ops.uv.export_layout(filepath=expfilepath, export_all=True, mode='SVG', size=(hsize, vsize))
        
        # Deletes the object.
        bpy.data.objects.remove(bpy.data.objects['Plane'], do_unlink=True)
        
        # Deletes the meshes.
        bpy.data.meshes.remove(bpy.data.meshes['Plane'], do_unlink=True)
        bpy.data.meshes.remove(bpy.data.meshes['UV_Unwrap_PointCloud'], do_unlink=True)
        
        # Removes data so that the .blend file doesn't balloon in size.
        bpy.context.scene["RawData"] = [(0,0,0)]
        bpy.context.scene["GenVertices"] = [(0,0,0)]
        bpy.context.scene["GenFaces"] = [(0,0,0)]
        bpy.context.scene["DUCFilePath"] = [(0,0,0)]
        bpy.context.scene["hsize"] = [(0,0,0)]
        bpy.context.scene["vsize"] = [(0,0,0)]
        
        t5 = time.time() - time_start
#        print("DUCExport    finished in %.4f sec" % (t5))
#        print("----------------END----------------","\n")
        
        bpy.context.scene["t5"] = t5
        
        ttotal = 0
        t_array = ["t1","t2","t3","t4","t5"]
        y = 0
        while y < 5:
            ttotal = ttotal + bpy.context.scene[t_array[y]]
            y +=1
        
        print()
        print("DCS UV Converter finished in %.1f seconds." % (ttotal))
        print("File saved to: %s" % (expfilepath),"\n")
        
        bpy.context.scene["t5"] = t5
        
        return {'FINISHED'}

# Adds the UI.
class LayoutDUCButtons(Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "DCS UV Converter"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        
        # Convert button.
        layout.label(text="Select the .csv file to convert")
        row = layout.row()
        row.scale_y = 2.0
        row.operator("object.duc_main")
        
# Registers all of the classes.
classes = (
    DUCMain,
    DUCImportCSV,
    DUCTreatCSV,
    DUCMesh,
    DUCUnwrap,
    DUCExport,
    LayoutDUCButtons,
)
        
def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
