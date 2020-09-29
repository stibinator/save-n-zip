######################################################################################################
# An operator to save your file with an incremental suffix                                          #
# Actualy partly uncommented - if you do not understand some parts of the code,                      #
# please see further version or contact me.                                                          #
# Author: Lapineige                                                                                  #
# License: GPL v3                                                                                    #
######################################################################################################

############# Add-on description (used by Blender)

bl_info = {
    "name": "Save Incremental",
    "description": 'Save your file with an incremental suffix',
    "author": "Lapineige",
    "version": (1, 7),
    "blender": (2, 72, 0),
    "location": "File > Save Incremental",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "http://blenderlounge.fr/forum/viewtopic.php?f=18&t=736",
    "category": "System"}

##############
import bpy, os, datetime
from zipfile import ZipFile

class FileSaveAndZip(bpy.types.Operator):
    bl_idname = "file.save_n_zip"
    bl_label = "Save N zip"
   
    def execute(self, context):
        if bpy.data.filepath:
            dirPath,fileName = os.path.split(bpy.data.filepath.split('.blend')[0])
            dateStamp = datetime.datetime.fromtimestamp(os.path.getmtime(bpy.data.filepath)).strftime('_%d-%m-%Y_%H%M%S.blend')
            dateStampedFile = os.path.join(dirPath, fileName + dateStamp)

            if os.path.isfile(dateStampedFile):
                self.report({'WARNING'}, "Internal Error: trying to save over an existing file. Cancelled")
                print('Tested Output: ', output)
                return {'CANCELLED'}
            os.rename(bpy.data.filepath, dateStampedFile)
            zipFilePath = bpy.data.filepath + '.zip'
            if os.path.isfile(zipFilePath):
                with ZipFile(zipFilePath, 'a') as zipArchive:
                    zipArchive.write(dateStampedFile)
                    self.report({'INFO'}, "Zip: {0} - updated".format(zipFilePath))
            else:
                with ZipFile(zipFilePath, 'w') as zipArchive:
                    zipArchive.write(dateStampedFile)
                    self.report({'INFO'}, "Zip: {0} - created".format(zipFilePath))
            bpy.ops.wm.save_mainfile()
            
            ##self.report({'INFO'}, "File: {0} - Created at: {1}".format(output[len(bpy.path.abspath(d_sep)):], output[:len(bpy.path.abspath(d_sep))]))
        else:
            self.report({'WARNING'}, "Please save the file before incrementally saving")
        return {'FINISHED'}
        ###### PENSER A TESTER AUTRES FICHIERS DU DOSSIER, VOIR SI TROU DANS NUMEROTATION==> WARNING


def draw_into_file_menu(self,context):
    self.layout.separator()
    self.layout.operator('file.save_n_zip')
    
def register():
    bpy.utils.register_class(FileSaveAndZip)
    bpy.types.TOPBAR_MT_file.append(draw_into_file_menu)
def unregister():
    bpy.utils.unregister_class(FileSaveAndZip)
    bpy.types.TOPBAR_MT_file.remove(draw_into_file_menu)
    
if __name__ == "__main__":
    register()
