######################################################################################################
# datestamps the last saved version of a project, and saves it into a zip file                       #
# License: GPL v3                                                                                    #
######################################################################################################

############# Add-on description (used by Blender)
bl_info = {
    "name": "Save-n-Zip",
    "description": 'Save your file with incremental archived backups',
    "author": "stib, thanks to Lapineige for the bare bones",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "File > Save-n-Zip",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "https://blob.pureandapplied.com.au/save-n-Zip",
    "category": "System"}

##############
import bpy, os, zipfile, subprocess, re
from datetime import datetime

# the temp file that gets zipped
tempFileName = "saveNzipTemp.blend"

class FileSaveAndZip(bpy.types.Operator):
    bl_idname = "file.save_n_zip"
    bl_label = "Save N Zip"
   
    def execute(self, context):\
        # full path to current project, if it has been saved
        fileFullPath = bpy.data.filepath
        if fileFullPath:
            dirPath,fileName = os.path.split(fileFullPath.split('.blend')[0])
            #slice off the numerical suffix: "foo_123.blend", "foo 12345.blend" "foo-1234.blend" or "foo12.blend" => "foo"
            # the . at the start of the regex is to match at least one char for files named like 1.blend
            suffixSearch = re.compile(r'.[\s_-]*\d*$', re.IGNORECASE).search(fileName)
            suffixStart = suffixSearch.start()
            baseName = None
            if suffixSearch:
                #offset the stat to account for the first matched wildcard
                baseName = fileName[:suffixStart + 1] 
            if not baseName:
                baseName = fileName #this really shouldn't happen, but ugh, regex
            dateStamp = datetime.fromtimestamp(os.path.getmtime(fileFullPath)).strftime('_%d-%m-%Y_%H%M%S.blend')
            dateStampedFile = fileName + dateStamp
            tempFileFullPath = os.path.join(dirPath, tempFileName)
            #deal with old temp files
            if os.path.isfile(tempFileFullPath):
                os.remove(tempFileFullPath)
            #move our current blend file to the temp file
            os.rename(fileFullPath, tempFileFullPath)
            zipFilePath = os.path.join(dirPath, (baseName + ".zip"))
            if os.path.isfile(zipFilePath):
                # zip file exists, append new version
                zipMode = "a"
            else:
                # create a new zip
                zipMode = "w"
            command = (
                bpy.app.binary_path_python,
                "-c", "import zipfile, os\nwith zipfile.ZipFile('{0}', '{1}') as zipArchive:\n  zipArchive.write('{2}', '{3}', zipfile.ZIP_LZMA)\nos.remove('{2}')".format(
                    zipFilePath.replace("\\", "/"), 
                    zipMode.replace("\\", "/"), 
                    tempFileFullPath.replace("\\", "/"), 
                    dateStampedFile.replace("\\", "/")),
                )
            # zips the file in a subprocess, because zipping large .blend files takes a while.
            # with zipfile.ZipFile(zipFilePath, 'a') as zipArchive:
                # zipArchive.write(fileFullPath, dateStampedFile, zipfile.ZIP_LZMA)
                # report = "Zip {0} updated. ".format(zipFilePath)

            proc = subprocess.Popen(command)
            if (proc):
                report = "Zipping old file to {0}. ".format(baseName + ".zip")
            
            bpy.ops.wm.save_mainfile()
            self.report({'INFO'}, "{0}Current File saved successfully".format(report))
         
            ##self.report({'INFO'}, "File: {0} - Created at: {1}".format(output[len(bpy.path.abspath(d_sep)):], output[:len(bpy.path.abspath(d_sep))]))
        else:
            # file has yet to be saved
            bpy.ops.wm.save_mainfile('INVOKE_AREA')
        return {'FINISHED'}
 
def draw_into_file_menu(self,context):
    self.layout.separator()
    self.layout.operator('file.save_n_zip')
  

class SaveNZipPreferences(bpy.types.AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    category: bpy.props.StringProperty(
            name = "Zip method",
            description = "Choose the zip compression method",
            default = "Edit",
            # update = update_panel()
            )

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        col = row.column()
        col.label(text = "Compression method:")
        col.prop(self, "category", text = "")
            
def register():
    bpy.utils.register_class(FileSaveAndZip)
    bpy.types.TOPBAR_MT_file.append(draw_into_file_menu)
    
def unregister():
    bpy.utils.unregister_class(FileSaveAndZip)
    bpy.types.TOPBAR_MT_file.remove(draw_into_file_menu)
    
if __name__ == "__main__":
    register()
