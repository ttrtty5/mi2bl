bl_info = {
    "name": "MI联动组件",
    "author": "ttrtty5",
    "version": (0, 2, 0),
    "blender": (2, 91, 0),
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

# 以下是拿来当吉祥物的函数,有用的全扔extra文件里了
class TTR_do_1(bpy.types.Operator):
    '''It's just an example, 哈哈哈'''
    bl_idname = 'object.ttr_do_1'
    bl_label = '例子'
    
    '''
    @classmethod
    def poll(cls,context):
        return context.active_object.location.x < 0
    '''
    
    def execute(self,context):
        self.report({'INFO'},'hhh')
        return {'FINISHED'}


def write_some_data(context, filepath, use_some_setting):
    f = open(filepath, 'w', encoding='utf-8')
    f.write("你不会看见缓存清理能用, 以为我这个做完了吧 \n%s" % use_some_setting)
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
        return write_some_data(context, self.filepath, '那你是真的憨批.jpg')



classes=(
    TTR_do_1,
    ExportRigidData
)
'''
    # 批量加载包模块,但不知道为什么reload并没有什么效果
    if "bpy" in locals():
        print('cs0')
        importlib.reload(load_modules)
    else:
        print('cs1')
        from . import load_modules
'''
# 解决办法,加载两次,因为在init里无法靠"bpy" in locals()来判断是否是重载行为
from . import load_modules

def register():
    importlib.reload(load_modules)
        
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