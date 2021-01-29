'''载入示范
    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row = row.row()
        row1 = row.prop(context.window_manager.mi2bl,"active_image",text="",icon='VIEWZOOM')
        row.operator('mi2bl.item_cut_button')
        row = layout.row()
        box = row.box()
        box.template_icon_view(context.window_manager.mi2bl, 
            "assets_files",show_labels=True, 
            scale_popup=2)
'''
import bpy
from bpy.props import StringProperty, IntProperty, PointerProperty, EnumProperty, BoolProperty
from bpy.types import PropertyGroup
from os.path import split
from bpy_extras.io_utils import ImportHelper
from . import imagecrop
class 载入图片进行分割(bpy.types.Operator,ImportHelper):
    '''载入图片,将其分割成item'''
    bl_idname = 'mi2bl.item_cut_button'
    bl_label = '载入图片'
    bl_options = {'INTERNAL'}
    outside_item=[]#当前窗口内的icon集合
    image_list=[]#大图对象集合
    image_dict={}#通过大图名字获取索引
    item_info={}#图片对象，x刀，y刀

    #过滤其他文件，只选择*.png
    filter_glob: bpy.props.StringProperty(
        default="*.png",
        options={'HIDDEN'})

    x_cut_num: bpy.props.IntProperty(
        name="水平切刀数",
        default=2,
        min=1,
        description="该数值决定了图片在水平方向被分割后的数量")

    Y_cut_num: bpy.props.IntProperty(
        name="竖直切刀数",
        default=2,
        min=1,
        description="该数值决定了图片在竖直方向被分割后的数量")

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self,context):
        if self.filepath:
            #image列表插入部分
            image=bpy.data.images.load(self.filepath,check_existing = True)
            if image.name in bpy.data.images:
                image.reload()
            name=image.name
            self.item_info[name] = (name,self.x_cut_num,self.Y_cut_num)
            preview_collections['main'][name]=bpy.utils.previews.new()
            preview_collections['info'][name]=[]
            image_num=len(self.image_list)
            list1=(name,name,"用于获取小item，和item的uv的大图",image.preview.icon_id,image_num)
            self.image_list.append(list1)
            self.image_dict[name]=image_num
            #图片分割成预览部分
            preview_path=imagecrop.image_crop(self.filepath,self.x_cut_num,self.Y_cut_num)
            for img in preview_path:
                preview_name=name.replace('.png','')+"_"+split(img)[1]
                info=preview_collections['main'][name].load(preview_name,img, 'IMAGE')
                #在info内新建对应图片名字的预览对象集合数组
                preview_collections['info'][name].append(info)

            bpy.context.window_manager.mi2bl.active_image=name#使得加载后列表中显示该图
            context.window_manager.mi2bl.UI_state=True
            #更新img_num
            bpy.context.window_manager.mi2bl.img_num=len(self.image_list)
            global build_state
            build_state=True
        else:
            self.report({'INFO'},'未选择图片,已返回')
        
        return {'FINISHED'}

class item_switch_left(bpy.types.Operator):
    bl_idname = 'mi2bl.previous_item'
    bl_label = "上一个item"
    bl_description = "更改为上一个item"
    bl_options = {'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        return 载入图片进行分割.outside_item != []
    
    def execute(self, context):
        item_num=len(载入图片进行分割.outside_item)-1
        active_item=int(context.window_manager.mi2bl.assets_files)
        if active_item != 0:
            context.window_manager.mi2bl.assets_files=str(active_item-1)
        else:
            context.window_manager.mi2bl.assets_files=str(item_num)
        return {'FINISHED'}

class item_switch_right(bpy.types.Operator):
    bl_idname = 'mi2bl.next_item'
    bl_label = "下一个item"
    bl_description = "更改为下一个item"
    bl_options = {'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        return 载入图片进行分割.outside_item != []
    
    def execute(self, context):
        item_num=len(载入图片进行分割.outside_item)-1
        active_item=int(context.window_manager.mi2bl.assets_files)
        if active_item != item_num:
            context.window_manager.mi2bl.assets_files=str(active_item+1)
        else:
            context.window_manager.mi2bl.assets_files='0'
        return {'FINISHED'}

from .MCPREP_OT_spawn_item import spawn_item_from_pixels
from .get_pixel_to_icon import get_tile_pixels, item_uv_correction
class spawn_item_from_image(bpy.types.Operator):
    """从选定的item来成item立体网格物体(物体大小为1)"""
    bl_idname = 'mi2bl.spawn_item_from_image'
    bl_label = "生成"
    bl_options = {'REGISTER', 'UNDO'}
    size: bpy.props.FloatProperty(
        name="大小",
        default=1.0,
        min=0.001,
        description="物品的blender单位的大小",
        options={'HIDDEN'})
    thickness: bpy.props.FloatProperty(
        name="厚度",
        default=1.0,
        min=0.0,
        description="物体的厚度（稍后可以在修改器中更改）", 
        options={'HIDDEN'})
    transparency: bpy.props.BoolProperty(
        name="删除透明面",
        description="透明像素在渲染后将是透明的",
        default=True, 
        options={'HIDDEN'})
    threshold: bpy.props.FloatProperty(
        name="透明阈值",
        description="1.0 =零容差，不会生成透明像素",
        default=0.5,
        min=0.0,
        max=1.0, 
        options={'HIDDEN'})
    scale_uvs: bpy.props.FloatProperty(
        name="UV缩放",
        default=0.75,
        description="缩放生成的item的各个UV面", 
        options={'HIDDEN'})
    max_pixels: bpy.props.IntProperty(
        name="最大像素",
        default=50000,
        min=1,
        description="如果所选图像包含的像素数多于给定数量，则图像将按比例缩小", 
        options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        return 载入图片进行分割.outside_item != [] and context.mode == 'OBJECT'
    
    def execute(self,context):
        item_name=int(bpy.context.window_manager.mi2bl.assets_files)
        image_name=bpy.context.window_manager.mi2bl.active_image
        imgname, x_num, y_num = 载入图片进行分割.item_info[image_name]

        if image_name not in bpy.data.images:
            self.report({'INFO'},"图片"+image_name+"丢失")
            return {'FINISHED'}
        img = bpy.data.images[imgname]

        from_pos=divmod(item_name, x_num)#要转换的item坐标 (y, x)
        to_pos=(from_pos[1], y_num - from_pos[0] - 1) #(x, y)
        
        pixels=list(img.pixels)
        width = img.size[1]
        tile_xy=(int(img.size[0] / x_num), int(img.size[1] / y_num))
        alpha_pixels = get_tile_pixels(tile_xy, width, pixels, to_pos)
        
        obj, state = spawn_item_from_pixels(context, self.max_pixels, self.thickness, self.threshold,
            self.transparency, img, alpha_pixels, tile_xy)

        item_uv_correction(obj, x_num, y_num, to_pos)

        # 应用其他设置，如整体对象比例和uv面比例
        for i in range(3):
            obj.scale[i] *= 0.5 * self.size
        bpy.ops.object.transform_apply(scale=True, location=False)
        bpy.ops.object.scale_uv(scale=self.scale_uvs, selected_only=False, skipUsage=True)
        obj.location = bpy.context.scene.cursor.location # 移动到3D游标上

        obj.name=image_name + '_%s'%item_name
        obj.data.name=image_name + '_%s'%item_name
        return {'FINISHED'}

class spawn_item_from_image_pixelsize(bpy.types.Operator):
    """生成的item的像素大小为0.1"""
    bl_idname = 'mi2bl.spawn_item_from_image_pixelsize'
    bl_label = "像素比例生成"
    bl_options = {'REGISTER', 'UNDO'}
    thickness: bpy.props.FloatProperty(
        name="厚度",
        default=1.0,
        min=0.0,
        description="物体的厚度（稍后可以在修改器中更改）", 
        options={'HIDDEN'})
    transparency: bpy.props.BoolProperty(
        name="删除透明面",
        description="透明像素在渲染后将是透明的",
        default=True, 
        options={'HIDDEN'})
    threshold: bpy.props.FloatProperty(
        name="透明阈值",
        description="1.0 =零容差，不会生成透明像素",
        default=0.5,
        min=0.0,
        max=1.0, 
        options={'HIDDEN'})
    scale_uvs: bpy.props.FloatProperty(
        name="UV缩放",
        default=0.75,
        description="缩放生成的item的各个UV面", 
        options={'HIDDEN'})
    max_pixels: bpy.props.IntProperty(
        name="最大像素",
        default=50000,
        min=1,
        description="如果所选图像包含的像素数多于给定数量，则图像将按比例缩小", 
        options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        return 载入图片进行分割.outside_item != [] and context.mode == 'OBJECT'
    
    def execute(self,context):
        item_name=int(bpy.context.window_manager.mi2bl.assets_files)
        image_name=bpy.context.window_manager.mi2bl.active_image
        imgname, x_num, y_num = 载入图片进行分割.item_info[image_name]

        if image_name not in bpy.data.images:
            self.report({'INFO'},"图片"+image_name+"丢失")
            return {'FINISHED'}
        img = bpy.data.images[imgname]

        from_pos=divmod(item_name, x_num)#要转换的item坐标 (y, x)
        to_pos=(from_pos[1], y_num - from_pos[0] - 1) #(x, y)
        
        pixels=list(img.pixels)
        width = img.size[1]
        tile_xy=(int(img.size[0] / x_num), int(img.size[1] / y_num))
        alpha_pixels = get_tile_pixels(tile_xy, width, pixels, to_pos)
        
        obj, state = spawn_item_from_pixels(context, self.max_pixels, self.thickness, self.threshold,
            self.transparency, img, alpha_pixels, tile_xy)

        item_uv_correction(obj, x_num, y_num, to_pos)

        # 应用其他设置，如整体对象比例和uv面比例
        obj.scale[0] *= (tile_xy[0] / 20)
        obj.scale[1] *= (tile_xy[1] / 20)
        bpy.ops.object.transform_apply(scale=True, location=False)
        bpy.ops.object.scale_uv(scale=self.scale_uvs, selected_only=False, skipUsage=True)
        obj.location = bpy.context.scene.cursor.location # 移动到3D游标上
        obj.name=image_name + '_%s'%item_name
        obj.data.name=image_name + '_%s'%item_name
        return {'FINISHED'}


class delete_preview_item_list(bpy.types.Operator):
    '''删除该图片的item预览'''
    bl_idname = 'mi2bl.delete_preview_item_list'
    bl_label = '删除'
    def execute(self, context):
        name = context.window_manager.mi2bl.active_image
        if name=="":
            self.report({'INFO'},'未选择有效图片')
            return {'FINISHED'}
        index=载入图片进行分割.image_dict[name]
        if len(载入图片进行分割.image_list)>1:
            next_name=载入图片进行分割.image_list[index-1][0]
            bpy.context.window_manager.mi2bl.active_image=next_name
            # TODO:当有两张图片时，删除第第一张，列表无法自动调成第二张
            # 并且还会报错current value '2' matches no enum in 'options', 'options', 'active_image'
        else:
            context.window_manager.mi2bl.UI_state=False

        载入图片进行分割.image_list.pop(index)
        preview_collections['info'].pop(name)
        bpy.utils.previews.remove(preview_collections['main'][name])
        preview_collections['main'].pop(name)
        
        #重置图片列表索引
        global image_delete_state
        image_delete_state=True
        global build_state
        build_state=True
        return {'FINISHED'}



build_state=False

#干脆按了按钮才允许生成一次
def build_item(context):
    if bpy.context.window_manager.mi2bl.active_image=="":
        载入图片进行分割.outside_item=[]
        return None
    global preview_collections
    载入图片进行分割.outside_item=[]
    name=bpy.context.window_manager.mi2bl.active_image
    list1=preview_collections['info'][name]
    num=0
    for img in list1:
        li=(str(num),str(num),"这是第"+str(num)+"块item",img.icon_id,num)
        载入图片进行分割.outside_item.append(li)
        num+=1
    

def general_icon_from_prevlist(self,context):
    global build_state
    if build_state:
        build_item(context)
        build_state=False
    return 载入图片进行分割.outside_item

#初始化加载的item大图的列表枚举
image_delete_state=False
def active_image_enum(self,context):
    global image_delete_state
    if image_delete_state:
        image_delete_state=False
        #删除后重置载入图片进行分割.image_list内的id
        #(name,name,"用于获取小item，和item的uv的大图",image.preview.icon_id,image_num)
        image_num=0
        list1=[]
        dict1={}
        for enum in 载入图片进行分割.image_list:
            if enum=='':
                continue
            name=enum[0]
            desc=enum[2]
            id=enum[3]
            list1.append((name,name,desc,id,image_num))
            dict1[name]=image_num
            
        载入图片进行分割.image_list=list1
        载入图片进行分割.image_dict=dict1
        bpy.context.window_manager.mi2bl.img_num=len(载入图片进行分割.image_list)
    
    #emmm,功能全在按钮里写了，就懒得再设一个函数
    return 载入图片进行分割.image_list

def image_set(self,context):
    #image_name=载入图片进行分割.image_list[value][1]#获取名字
    image_name=bpy.context.window_manager.mi2bl.active_image#获取名字
    载入图片进行分割.outside_item=[]
    icon_list = preview_collections["info"][image_name]#获取对应名字的预览集合
    num=0
    for icon in icon_list:
        li=(str(num),str(num),"这是第"+str(num)+"块item",icon.icon_id,num)
        载入图片进行分割.outside_item.append(li)
        num+=1

class options(PropertyGroup):
    assets_files: EnumProperty(
        description = '用于存储图片的预览',
        items = general_icon_from_prevlist,
        #updata=general_icon_from_prevlist_updata
        )
    active_image: EnumProperty(
        description = '正在显示的图片',
        items = active_image_enum, 
        update = image_set
        )
    UI_state: BoolProperty(
        name = '面板显示',
        description = '默认关闭，载入图片开启',
        default = False)
    # active_item_index: IntProperty(
    #     name = '所选的item',
    #     description = '仅用于载入初始化，所以你怎么改也不会报错，安啦安啦',
    #     default = 0)
    img_num: IntProperty(
        description = 'active_image中的图片数量',
        default = 0
        )
    # UI面板变量
    mesh_UI: BoolProperty(
        name = '建模',
        description = '显示建模面板',
        default = True)
    convert_UI: BoolProperty(
        name = '转换',
        description = '显示转换面板',
        default = False)
    notok_UI: BoolProperty(
        name = '未完成',
        description = '显示未完成面板',
        default = False)
    extra_UI_state: BoolProperty(
        name = 'extra面板显示',
        description = '按钮状态',
        default = False)

    

classes=(
    载入图片进行分割,
    options,
    delete_preview_item_list,
    spawn_item_from_image,
    item_switch_left,
    item_switch_right,
    spawn_item_from_image_pixelsize
)
# main存储每张图片preview集合
# info存储main内preview集合内对应所有所加载的图片的被分割的每个icon的对象集合，用于获取icon_id
preview_collections = {}
def register():
    import bpy.utils.previews
    global preview_collections
    if 'preview_collections' not in dir():
        preview_collections={} #del后会导致第二次注册报错提示没声明变量
    #pcoll = bpy.utils.previews.new()
    preview_collections['main'] = {}
    preview_collections['info'] = {}

    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.mi2bl = PointerProperty(type=options)#pointer是指针
    bpy.context.window_manager.mi2bl.name="options"

def unregister():
    global preview_collections
    if preview_collections['main'] !={}:
        for pcoll in  preview_collections['main']:
            bpy.utils.previews.remove(preview_collections['main'][pcoll])
    del preview_collections
    载入图片进行分割.image_list=[]
    载入图片进行分割.outside_item=[]
    载入图片进行分割.image_dict={}
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.WindowManager.mi2bl