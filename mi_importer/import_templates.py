from os.path import split
from json import loads
import bpy
from bpy_extras.io_utils import ImportHelper
from ..Mcprep.MCPREP_OT_spawn_item import spawn_item_from_pixels, spawn_plane_from_pixels
from ..Mcprep.get_pixel_to_icon import get_tile_pixels, item_uv_correction,default_mat_mbcube, mb_mat_uvpos, mb_cube_uv
from . mi2bl3 import spawn_timelines_obj
# from . mi2bl约束 import spawn_timelines_obj
from math import radians

class import_templates(bpy.types.Operator, ImportHelper):
    '''导入miobject，其实miproject也可以，格式一样的'''
    bl_idname = 'mi2bl.import_miobject'
    bl_label = '导入miobject'
    bl_options = {'INTERNAL'}
    
    #过滤其他文件，只选择*.miobject
    filter_glob: bpy.props.StringProperty(
        default="*.miobject",
        options={'HIDDEN'})
    
    restore_naming: bpy.props.BoolProperty(
        name = '恢复命名',
        description = '调试功能, 不恢复名字以查看id',
        default = True)

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'
    
    
    def execute(self,context):
        if not self.filepath:
            self.report({'INFO'},"未选择文件,已返回")
            return {'CANCELLED'}

        with open(self.filepath,'r')as f:
            fileData=f.read()

        folder_path = split(self.filepath)[0]

        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection
        #将当前活动集合设置为场景集合
        if 'templates' not in bpy.context.view_layer.layer_collection.children:
            coll=bpy.data.collections.new('templates')
            bpy.context.view_layer.active_layer_collection.collection.children.link(coll)
        # else:
        #     coll=bpy.data.collections['templates']
        
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children['templates']
        #设置当前活动集合设置
        
        MiTemplatesData = loads(fileData)
        #制作贴图引用字典
        ResourceDict={}
        for res in MiTemplatesData['resources']:
            if res['type'] not in ('texture', 'itemsheet'):
                continue
            ResourceDict[res['id']] = res
            imgpath = folder_path+'\\' + res['filename']
            if res['id'] in bpy.data.images:
                continue
            img = bpy.data.images.load(imgpath)#因为有重复贴图只能重复加载, 不能check_existing=True
            img.name = res['id']
        #print(ResourceDict)

        #将物体生成在templates集合中
        for obj in MiTemplatesData['templates']:
            if obj['type'] == 'item':
                item_id = obj['id']
                tex_id = obj['item']['tex']
                slot = int(obj['item']['slot'])
                x_num, y_num=ResourceDict[tex_id]['item_sheet_size'] if 'item_sheet_size' in ResourceDict[tex_id] else [1,1]
                
                img=bpy.data.images[tex_id]

                from_pos=divmod(slot, x_num)#要转换的item坐标 (y, x)
                to_pos=(from_pos[1], y_num - from_pos[0] - 1) #(x, y)

                pixels=list(img.pixels)
                width = img.size[1]
                tile_xy=(int(img.size[0] / x_num), int(img.size[1] / y_num))
                alpha_pixels = get_tile_pixels(tile_xy, width, pixels, to_pos)
                
                obj, state = spawn_item_from_pixels(context, 
                    50000, 1.0, 0.5,
                    True, img, alpha_pixels, tile_xy)
                obj.name=item_id
                item_uv_correction(obj, x_num, y_num, to_pos)

                for i in range(3):
                    obj.scale[i] *= 0.5
                bpy.ops.object.transform_apply(scale=True, location=False)
                bpy.ops.object.scale_uv(scale=0.5, selected_only=False, skipUsage=True)

            else:
                print('是未发现的物体类型,类型:'+obj['type'])
                #TODO: 将temp中的物体实例到obj集合中，并设置位置缩放等变换
                
        

        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection
        # 将当前活动集合设置为场景集合
        if 'obj' not in bpy.context.view_layer.layer_collection.children:
            coll=bpy.data.collections.new('obj')
            bpy.context.view_layer.active_layer_collection.collection.children.link(coll)
        
        # 设置当前活动集合设置
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children['obj']

        # 将temp中的物体复制一份，并添加动画坐标等属性
        spawn_timelines_obj(MiTemplatesData, self.restore_naming)
        
        # 恢复贴图命名
        for res in ResourceDict:
            img = ResourceDict[res]
            bpy.data.images[img['id']].name = img['filename']

        return {'FINISHED'}

from ..Mcprep.get_pixel_to_icon import get_pixel_from_pos, plane_uv_from_uvpos
class import_mbmodel(bpy.types.Operator, ImportHelper):
    '''导入mbmodel,因为区分读取mb部件很麻烦,就懒得弄了'''
    bl_idname = 'mi2bl.import_mbmodel'
    bl_label = '导入mbmodel'
    bl_options = {'INTERNAL'}

    #过滤其他文件，只选择*.miobject
    filter_glob: bpy.props.StringProperty(
        default='*.mimodel',
        options={'HIDDEN'})
        #;*.mbbackup1;*.mbbackup2;*.mbbackup3
    

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'
    
    
    def execute(self,context):
        if not self.filepath:
            self.report({'INFO'},"未选择文件,已返回")
            return {'CANCELLED'}
        with open(self.filepath,'r')as f:
            fileData=f.read()
        
        folder_path = split(self.filepath)[0]
        MbData = loads(fileData)

        PartName=MbData['name']
        parts = MbData['parts']
        texture = MbData['texture'] if 'texture' in MbData else ''
        parent=''
        #默认父级材质
        mat=default_mat_mbcube(texture, folder_path)
        递归生成部件(parts,folder_path,context, parent, texture)

        return {'FINISHED'}


def 递归生成部件(parts,folder_path,context,parent, textureName):
    for part in parts:
        #防止只是用来存储部件的空shape部件
        shapes=part['shapes'] if 'shapes' in part else []
        ShapeDirt=[]
        #part贴图
        Ptexture = part['texture'] if 'texture' in part else textureName
                 
        if 'texture' in part or 'color_mix_percent' in part or 'color_alpha' in part or 'color_brightness' in part:
            bpy.data.images.load(folder_path + '\\' + Ptexture, check_existing=True)
            part_mat = bpy.data.materials[textureName].copy()
            part_mat.name = Ptexture
            mb_mat_uvpos(part_mat,part)
        
        for shape in shapes:
            #shape贴图
            Stexture = shape['texture'] if 'texture' in shape else Ptexture
            if shape['type'] == 'block':
                origin_pos = shape['from'] #x, z ,y
                origin_offset = [ (-origin_pos[2])/16, (-origin_pos[0])/16, origin_pos[1]/16 ] # x, y, z
                bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, location=[-0.5, -0.5, 0.5])
                bpy.ops.object.transform_apply(location=True)
                bpy.context.object.location = origin_offset

                uv_lwh=[shape['to'][2]-origin_pos[2], 
                    shape['to'][0]-origin_pos[0], 
                    shape['to'][1]-origin_pos[1]]
                #scale
                origin_scale = [uv_lwh[0]/16, uv_lwh[1]/16, uv_lwh[2]/16]
                bpy.context.object.scale = origin_scale
                bpy.ops.object.transform_apply(location=True, scale=True)

                #读取变换数据
                position=[-shape['position'][2]/16, -shape['position'][0]/16, shape['position'][1]/16] if 'position' in shape else [0,0,0]
                # x , z ,y
                rotation=[-radians(shape['rotation'][2]), -radians(shape['rotation'][0]), radians(shape['rotation'][1])] if 'rotation' in shape else [0,0,0]
                scale=[shape['scale'][2], shape['scale'][0], shape['scale'][1]] if 'scale' in shape else [1,1,1]
                bpy.context.object.location = position
                bpy.context.object.rotation_euler = rotation
                bpy.context.object.scale = scale
                #bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

                #TODO:方块的材质uv部分
                if 'texture' in shape or 'color_mix_percent' in shape or 'color_alpha' in shape or 'color_brightness' in shape:
                    img=bpy.data.images.load(folder_path + '\\' + Stexture, check_existing=True)
                    if (Ptexture+ '_' +part['name']) in bpy.data.materials:
                        shape_mat = bpy.data.materials[Ptexture+ '_' +part['name']].copy()
                    else:
                        shape_mat = bpy.data.materials[Stexture].copy()
                    
                    mb_mat_uvpos(shape_mat,shape)
                    bpy.context.object.data.materials.append(shape_mat)
                    #开阴影混合等
                    bpy.context.object.active_material.blend_method = 'BLEND'
                    bpy.context.object.active_material.shadow_method = 'CLIP'
                else:
                    bpy.context.object.data.materials.append(bpy.data.materials[Stexture])
                
                image_size = bpy.data.images[Stexture].size
                mb_cube_uv(uv_lwh,shape['uv'], image_size)


                ShapeDirt.append(bpy.context.object)
            
            if shape['type'] == 'plane':
                if '3d' in shape:
                    #生成立体平面
                    origin_pos = shape['from'] #x, z ,y
                    origin_offset = [ (-origin_pos[2])/16, (-origin_pos[0])/16, origin_pos[1]/16 ] # x, y, z
                    uv_wh=[int(shape['to'][0]-origin_pos[0]), 
                        int(shape['to'][1]-origin_pos[1])]
                    
                    if 'texture' in shape:
                        img=bpy.data.images.load(folder_path +'\\' + shape['texture'] , check_existing=True)
                    else:
                        img=bpy.data.images.load(folder_path + '\\' + Stexture, check_existing=True)
                    
                    #获取像素
                    alpha_pixels = get_pixel_from_pos(img,shape['uv'],uv_wh)
                    obj, state = spawn_plane_from_pixels(context, 
                        50000, 1.0, 0.5,
                        True, img, alpha_pixels, uv_wh)
                    
                    plane_uv_from_uvpos(img,shape['uv'],uv_wh)
                    bpy.ops.object.scale_uv(scale=0.5, selected_only=False, skipUsage=True)

                    bpy.context.object.scale=[0.5,0.5,0.5]
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                    #应用修改器
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="solid")
                    #初始化物体
                    bpy.context.object.location = [-0.03125, -0.5, 0.5]
                    #纠正物体左下为原点
                    bpy.context.object.rotation_euler[0]=radians(90)
                    bpy.context.object.rotation_euler[2]=radians(-90)
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

                    
                    #初始化物体原点
                    bpy.context.object.scale = [1, uv_wh[0]/16, uv_wh[1]/16]
                    bpy.context.object.location=origin_offset
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

                    #读取变换数据
                    position=[-shape['position'][2]/16, -shape['position'][0]/16, shape['position'][1]/16] if 'position' in shape else [0,0,0]
                    # x , z ,y
                    rotation=[-radians(shape['rotation'][2]), -radians(shape['rotation'][0]), radians(shape['rotation'][1])] if 'rotation' in shape else [0,0,0]
                    scale=[shape['scale'][2], shape['scale'][0], shape['scale'][1]] if 'scale' in shape else [1,1,1]
                    bpy.context.object.location = position
                    bpy.context.object.rotation_euler = rotation
                    bpy.context.object.scale = scale
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

                    ShapeDirt.append(bpy.context.object)

                else:
                    #生成非立体平面
                    origin_pos = shape['from'] #x, z ,y
                    origin_offset = [ (-origin_pos[2])/16, (-origin_pos[0])/16, origin_pos[1]/16 ] # x, y, z
                    bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=[0, -0.5, 0.5])
                    bpy.context.object.rotation_euler[1]=radians(90)
                    bpy.ops.object.transform_apply(location=True)
                    bpy.context.object.location=origin_offset

                    uv_wh=[shape['to'][0]-origin_pos[0], 
                        shape['to'][1]-origin_pos[1]]
                    #scale
                    origin_scale = [1, uv_wh[0]/16, uv_wh[1]/16]
                    bpy.context.object.scale=origin_scale
                    bpy.ops.object.transform_apply(location=True, scale=True)

                    ShapeDirt.append(bpy.context.object)

        #当碰到空shape的部件
        if len(ShapeDirt)==0:
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))

        #合并ShapeDirt内的物体
        if len(ShapeDirt)>1:
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = ShapeDirt[0]
            for shape in ShapeDirt:
                shape.select_set(True)
            bpy.ops.object.join()
        bpy.context.object.name = part['name']
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        #读取变换数据
        position=[-part['position'][2]/16, -part['position'][0]/16, part['position'][1]/16] if 'position' in part else [0,0,0]
        # x , z ,y
        rotation=[-radians(part['rotation'][2]), -radians(part['rotation'][0]), radians(part['rotation'][1])] if 'rotation' in part else [0,0,0]
        scale=[part['scale'][2], part['scale'][0], part['scale'][1]] if 'scale' in part else [1,1,1]
        bpy.context.object.location = position
        bpy.context.object.rotation_euler = rotation
        bpy.context.object.scale = scale
        #设置父级
        if parent != '':
            bpy.context.object.parent=parent
        
        if 'parts' in part:
            递归生成部件(part['parts'],folder_path,context,bpy.context.object,Ptexture)
        
        


classes=(
    import_templates,
    import_mbmodel
)
# main存储preview集合
# info存储main内preview集合内对应所有所加载的图片的被分割的每个icon的对象集合，用于获取icon_id
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)