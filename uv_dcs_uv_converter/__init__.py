bl_info = {
    "name": "DCS UV Converter",
    "author": "Ettenmure",
    "version": (0, 1, 0),
    "blender": (2, 92, 0),
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

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator


#TODO: Separate it into modules.

class DUCConvertCSV(Operator, ImportHelper):
    """Select the .csv file to convert"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.duccsvimport"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Convert .csv"         # Display name in the interface.
    
    filter_glob: StringProperty(
        default='*.csv', # Restricts the selectable file type to .csv only.
        options={'HIDDEN'}
    )
    def execute(self, context):
        
        # Deletes objects on the scene.
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # Imports the data from the csv file and saves it in "data".
        data = []
        with open(self.filepath) as f:
            reader = csv.reader(f)
            for row in reader:
                data.append(row)
        
        # Saves the size of the image.
        hsize = float(data[1][0]) # Horizontal size of the texture
        vsize = float(data[1][1]) # Vertical size of the texture
        
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
        faces = [(0,0,0)] * facesnumber # Generates and empty list the length of facesnumber.
        j = 0
        k = 0
        while j < facesnumber: # Populates "faces" with consecutive numbers.
            faces[j] = (k,k+1,k+2)
            j +=1
            k +=3
        
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
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        # Stores the index of the last vertex of the merged mesh.
        lastindex = faces[-1][2]
        
        # Adds a plane, used for trimming the excess mesh that falls outside of the texture bounds.
        bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0.5, 0.5, 0), scale=(1, 1, 1))
        
        # Joins the uv map and the plane.
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.join()
        
        # Trims the faces outside the texture bounds defined by the previously created plane.
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.mode_set(mode = 'EDIT')
        
        # Cuts through the texture bounds.
        bpy.ops.mesh.select_all(action='SELECT') #Selects every face
        bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(1, 0, 0), flip=False) #Left edge
        bpy.ops.mesh.select_all(action='SELECT') #Selects every face
        bpy.ops.mesh.bisect(plane_co=(1, 0, 0), plane_no=(1, 0, 0), flip=False) #Right edge
        bpy.ops.mesh.select_all(action='SELECT') #Selects every face
        bpy.ops.mesh.bisect(plane_co=(0, 1, 0), plane_no=(0, 1, 0), flip=False) #Top edge
        bpy.ops.mesh.select_all(action='SELECT') #Selects every face
        bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(0, 1, 0), flip=False) #Bottom edge
        bpy.ops.mesh.select_all(action = 'DESELECT')
        
        # Deletes every vertex outside the texture bounds.
        #Bottom
        bm=bmesh.from_edit_mesh(bpy.context.active_object.data)
        bm.verts.ensure_lookup_table()
        bm.select_history.add(bm.verts[0])
        bpy.ops.mesh.select_axis(orientation='GLOBAL', sign='POS', axis='Y', threshold=0.0001)
        bpy.context.tool_settings.mesh_select_mode = (True, False, False)
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='VERT')
        
        #Top
        #bm=bmesh.from_edit_mesh(bpy.context.active_object.data)
        bm.verts.ensure_lookup_table()
        bm.select_history.add(bm.verts[3])
        bpy.ops.mesh.select_axis(orientation='GLOBAL', sign='NEG', axis='Y', threshold=0.0001)
        bpy.context.tool_settings.mesh_select_mode = (True, False, False)
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='VERT')
        
        #Left
        #bm=bmesh.from_edit_mesh(bpy.context.active_object.data)
        bm.verts.ensure_lookup_table()
        bm.select_history.add(bm.verts[0])
        bpy.ops.mesh.select_axis(orientation='GLOBAL', sign='POS', axis='X', threshold=0.0001)
        bpy.context.tool_settings.mesh_select_mode = (True, False, False)
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='VERT')
        
        #Right
        #bm=bmesh.from_edit_mesh(bpy.context.active_object.data)
        bm.verts.ensure_lookup_table()
        bm.select_history.add(bm.verts[1])
        bpy.ops.mesh.select_axis(orientation='GLOBAL', sign='NEG', axis='X', threshold=0.0001)
        bpy.context.tool_settings.mesh_select_mode = (True, False, False)
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='VERT')
        
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Unwraps the mesh.
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
            
        # Exports the texture on the same folder as the .csv file.
        expfilepath = self.filepath # Gets the filepath of the .csv file.
        expfilepath = expfilepath[:-4] # Removes the last four characters (.csv).
        expfilepath = expfilepath + '_UV' # Adds _UV to the file name.
        bpy.ops.uv.export_layout(filepath=expfilepath, export_all=True, mode='PNG', size=(int(hsize), int(vsize)))
        
        # Deletes the mesh.
        bpy.ops.object.delete(use_global=False)
        
        self.report({'INFO'}, "UV Conversion finished.")
        
        return {'FINISHED'} 
    

class LayoutDUCButtons(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "DCS UV Converter"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        # Convert button.
        layout.label(text="Select the .csv file to convert")
        row = layout.row()
        row.scale_y = 2.0
        row.operator("object.duccsvimport")
        
        
        
def register():
    bpy.utils.register_class(DUCConvertCSV)
    bpy.utils.register_class(LayoutDUCButtons)


def unregister():
    bpy.utils.unregister_class(DUCConvertCSV)
    bpy.utils.unregister_class(LayoutDUCButtons)


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()