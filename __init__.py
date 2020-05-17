bl_info = {
    "name": "MI联动组件",
    "author": "ttrtty5",
    "version": (0, 0, 9),
    "blender": (2, 81, 0),
    "location": "View3D > Create > MI联动组件",
    "warning": "",
    "description": "转换Mine-Imator的数据为blender的模型",
    "wiki_url": "https://jq.qq.com/?_wv=1027&k=5VC6gGA",
    "tracker_url": "https://ttrtty5.github.io/mi2bl/",
    "warning":"测试中",
    "category": "3D View"
}

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
import importlib
#from mi2bl import load_modules


if "load_modules" in locals():
	importlib.reload(load_modules)
else:
	from . import load_modules


class TTR_PT_UI(bpy.types.Panel):
    #bl_idname = 'TTR_UI'
    bl_label = 'MI联动组件'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Create'
    
    def draw(self,context):
        layout = self.layout
        box = layout.box()
        label = box.label(text="单item图:")
        row = box.row()
        row.operator('object.spawn_item_file')

        row = box.row()

        row = layout.row()
        row.label(text='转换功能')
        row = layout.row()
        row.operator('mi2bl.import_miobject')
        row = layout.row()
        row.operator('mi2bl.import_mbmodel')
        row = layout.row()
        row.label(text='未完成功能')
        #row = layout.row()
        #row.operator('object.ttr_do_1')
        row = layout.row()
        row.operator('export_test.rigiddata')
        row = layout.row()
        row.operator('object.ttr_do_2')
        

class TTR_do_1(bpy.types.Operator):
    bl_idname = 'object.ttr_do_1'
    bl_label = '例子'
    
    '''
    @classmethod
    def poll(cls,context):
        return context.active_object.location.x < 0
    '''
    
    def execute(self,context):
        self.report({'INFO'},'0')
        return {'FINISHED'}


def write_some_data(context, filepath, use_some_setting):
    print("running write_some_data...")
    f = open(filepath, 'w', encoding='utf-8')
    f.write("Hello World \n%s" % use_some_setting)
    f.close()

    return {'FINISHED'}

#导出函数
class ExportRigidData(bpy.types.Operator,ExportHelper):
    bl_idname='export_test.rigiddata'
    bl_label='导出关键帧数据'
    #ExportHelper类的属性
    filename_ext='.midata'
    
    filter_glob: StringProperty(
        default="*.midata",
        options={'HIDDEN'},
        maxlen=255,  # 最大内部缓冲区长度，较长的将被钳制
    )

    def execute(self, context):
        return write_some_data(context, self.filepath, '123')

class TTR_do_2(bpy.types.Operator):
    bl_idname = 'object.ttr_do_2'
    bl_label = '缓存清除'
    
    '''
    @classmethod
    def poll(cls,context):
        return context.active_object.location.x < 0
    '''
    
    def execute(self,context):
        for block in bpy.data.meshes:
            if block.users == 0:
                bpy.data.meshes.remove(block)

        for block in bpy.data.materials:
            if block.users == 0:
                bpy.data.materials.remove(block)

        for block in bpy.data.textures:
            if block.users == 0:
                bpy.data.textures.remove(block)

        for block in bpy.data.images:
            if block.users == 0:
                bpy.data.images.remove(block)
        self.report({'INFO'},"缓存已清除")
        return {'FINISHED'}

classes=(
    TTR_do_1,
    TTR_do_2,
    TTR_PT_UI,
    ExportRigidData
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    load_modules.register()

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    load_modules.unregister()

if __name__ == "__main__":
    register()
    #unregister()