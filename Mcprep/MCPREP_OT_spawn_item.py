#以下代码源自mcprep,虽然我也魔改了几处
#源自mcprep.util
import bpy
from bpy_extras.io_utils import ImportHelper
import os
BV_IS_28 = None  # 全局变量初始化
def bv28():
    """检查Blender2.8的布局、用户界面和属性"""
    global BV_IS_28
    if not BV_IS_28:
        BV_IS_28 = hasattr(bpy.app, "version") and bpy.app.version >= (2, 80)
    return BV_IS_28

#from mcprep.prep.MCPREP_OT_scale_uv
#为了防止类重注册冲突，我就把名字改了。。。反正来源写上面了
class MCPREP_OT_scale_uv(bpy.types.Operator):
    bl_idname = "object.scale_uv"
    bl_label = "缩放面UV"
    bl_description = "缩放所有选定的UV面。请参见F6或重做最后一个面板以调整缩放比例"
    bl_options = {'REGISTER', 'UNDO'}

    scale: bpy.props.FloatProperty(default=0.75, name="Scale")
    selected_only: bpy.props.BoolProperty(default=True, name="Seleced only")
    skipUsage: bpy.props.BoolProperty(
        default = False,
        options = {'HIDDEN'}
        )

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH' or (
            context.mode == 'OBJECT' and context.object)

    track_function = "scale_uv"
    #没写过异常追踪，所以懒得补了
    #@tracking.report_error
    def execute(self, context):

        # INITIAL WIP
        """
        # WIP
        ob = context.active_object
        # copied from elsewhere
        uvs = ob.data.uv_layers[0].data
        matchingVertIndex = list(chain.from_iterable(polyIndices))
        # example, matching list of uv coord and 3dVert coord:
        uvs_XY = [i.uv for i in Object.data.uv_layers[0].data]
        vertXYZ= [v.co for v in Object.data.vertices]
        matchingVertIndex = list(chain.from_iterable([p.vertices for p in Object.data.polygons]))
        # and now, the coord to pair with uv coord:
        matchingVertsCoord = [vertsXYZ[i] for i in matchingVertIndex]
        """
        if not context.object:
            self.report({'ERROR'}, "No active object found")
            return {'CANCELLED'}
        elif context.object.type != 'MESH':
            self.report({'ERROR'}, "Active object must be a mesh")
            return {'CANCELLED'}
        elif not context.object.data.polygons:
            self.report({'WARNING'}, "Active object has no faces")
            return {'CANCELLED'}

        if not context.object.data.uv_layers.active:#uv==None:
            self.report({'ERROR'}, "No active UV map found")
            return {'CANCELLED'}

        mode_initial = context.mode
        bpy.ops.object.mode_set(mode="OBJECT")
        ret = self.scale_uv_faces(context.object, self.scale)
        if mode_initial != 'OBJECT':
            bpy.ops.object.mode_set(mode="EDIT")

        if ret is not None:
            self.report({'ERROR'}, ret)
            #conf.log("Error, "+ret)
            return {'CANCELLED'}

        return {'FINISHED'}

    def scale_uv_faces(self, ob, factor):
        """按给定比例缩放对象的所有UV面中心."""

        factor *= -1
        factor += 1
        modified = False

        uv = ob.data.uv_layers.active
        # initial_UV = [(d.uv[0], d.uv[1])
        #                 for d in ob.data.uv_layers.active.data]

        for f in ob.data.polygons:
            if not f.select and self.selected_only is True:
                continue  # 如果未选中，则不会显示在“UV编辑器”（UV editor）中

            # 初始化多边形上的平均中心
            x=y=n=0  # x, y, 面的顶点数量
            for i in f.loop_indices:
                # loop_indices为顶点索引
                l = ob.data.loops[i] # 此多边形/边
                v = ob.data.vertices[l.vertex_index]  # 通过循环边来找到被引用的顶点数据
                # isolate to specific UV already used
                if not uv.data[l.index].select and self.selected_only is True:
                    continue
                x+=uv.data[l.index].uv[0]
                y+=uv.data[l.index].uv[1]
                n+=1
                #为求所有顶点的坐标平均值(几何中心)
            for i in f.loop_indices:
                if not uv.data[l.index].select and self.selected_only is True:
                    continue
                l = ob.data.loops[i]
                uv.data[l.index].uv[0] = uv.data[l.index].uv[0]*(1-factor)+x/n*(factor)
                uv.data[l.index].uv[1] = uv.data[l.index].uv[1]*(1-factor)+y/n*(factor)
                #uv.data[l.index].uv[0]*(1-factor) 按照原点缩放
                #+x/n*(factor)增加缩放后的原点偏移量
                modified = True
        if not modified:
            return "No UV faces selected"

        return None

class MCPREP_OT_spawn_item_from_file(bpy.types.Operator, ImportHelper):
    """从图像文件生成立体网格物体"""
    bl_idname = "object.spawn_item_file"
    bl_label = "3D贴图"

    filter_glob: bpy.props.StringProperty(
        default="",
        options={'HIDDEN'})
    fileselectparams = "use_filter_blender"
    files: bpy.props.CollectionProperty(
        type=bpy.types.PropertyGroup,
        options={'HIDDEN', 'SKIP_SAVE'})
    filter_image: bpy.props.BoolProperty(
        default=True,
        options={'HIDDEN', 'SKIP_SAVE'})

    size: bpy.props.FloatProperty(
        name="大小",
        default=1.0,
        min=0.001,
        description="物品的blender单位的大小")
    thickness: bpy.props.FloatProperty(
        name="厚度",
        default=1.0,
        min=0.0,
        description="物体的厚度（稍后可以在修改器中更改）")
    transparency: bpy.props.BoolProperty(
        name="删除透明面",
        description="透明像素在渲染后将是透明的",
        default=True)
    threshold: bpy.props.FloatProperty(
        name="透明阈值",
        description="1.0 =零容差，不会生成透明像素",
        default=0.5,
        min=0.0,
        max=1.0)
    scale_uvs: bpy.props.FloatProperty(
        name="UV缩放",
        default=0.75,
        description="缩放生成的item的各个UV面")
    max_pixels: bpy.props.IntProperty(
        name="最大像素",
        default=50000,
        min=1,
        description="如果所选图像包含的像素数多于给定数量，则图像将按比例缩小")

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    # track_function = "item"
    # track_param = "from file"
    #@tracking.report_error 原mcprep的异常跟踪，因为没看懂所以没加
    def execute(self, context):
        if not self.filepath:
            self.report({"WARNING"}, "未选择图像，已取消")
            return {'CANCELLED'}

        obj, status = spawn_item_from_filepath(context, self.filepath,
            self.max_pixels, self.thickness, self.threshold, self.transparency)

        if status and not obj:
            self.report({'ERROR'}, status)
            return {'CANCELLED'}
        elif status:
            self.report({'INFO'}, status)

        # 应用其他设置，如整体对象比例和uv面比例
        for i in range(3):
            obj.scale[i] *= 0.5 * self.size
        bpy.ops.object.transform_apply(scale=True, location=False)
        bpy.ops.object.scale_uv(scale=self.scale_uvs, selected_only=False, skipUsage=True)
        #bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}


def spawn_item_from_filepath(context, path, max_pixels, thickness, threshold,
    transparency):
    """Reusable function for generating an item from an image filepath
    从图像文件路径生成item的可重用函数

    参数
        context
        path: 图像文件的完整路径
        max_pixels: int, maximum number of output faces, will scale down
        thickness: 实心修改器的厚度，最小为0
        threshold: float, alpha值，低于该值的面将被删除
        transparency(透明度): bool, 删除低于阈值的面
    """

    # 加载图像并初始化对象
    image = None  # 图像数据块
    img_str = os.path.basename(path)
    name = os.path.splitext(img_str)[0]
    abspath = bpy.path.abspath(path)

    if img_str in bpy.data.images and bpy.path.abspath(
            bpy.data.images[img_str].filepath) == abspath:
        image = bpy.data.images[img_str]
    elif not path or not os.path.isfile(abspath):
        return None, "File not found"
    else:
        image = bpy.data.images.load(abspath)

    # 缩放图像
    pix = len(image.pixels)/4
    if pix > max_pixels:
        #待办事项: 删除循环并进行更多直接调整大小
        while pix > max_pixels:
            width = image.size[0]
            height = image.size[1]
            image.scale(width/1.5,height/1.5)
            pix = len(image.pixels)/4
    width = image.size[0] # 宽度
    height = image.size[1] # 高度

    if width == 0 or height == 0:
        return None, "图像具有无效的0大小维度"

    # 新方法，从一个UV网格开始并从中删除面
    if bv28():
        bpy.ops.mesh.primitive_grid_add(
            x_subdivisions=width+1, # outter edges count as a subdiv外缘作为细分曲面计算
            y_subdivisions=height+1, # outter edges count as a subdiv
            size=2,
            calc_uvs=True,
            location=(0,0,0))
    elif bpy.app.version < (2, 77): # could be 2, 76 even
        bpy.ops.mesh.primitive_grid_add(
            x_subdivisions=height+1, # outter edges count as a subdiv
            y_subdivisions=width+1, # outter edges count as a subdiv
            radius=1,
            location=(0,0,0))
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.uv.unwrap()
        bpy.ops.object.mode_set(mode='OBJECT')
    else:
        bpy.ops.mesh.primitive_grid_add(
            x_subdivisions=height+1, # outter edges count as a subdiv
            y_subdivisions=width+1, # outter edges count as a subdiv
            radius=1,
            calc_uvs=True,
            location=(0,0,0))
    itm_obj = context.object

    if not itm_obj:
        print("Error, 无法创建item基本对象")
        return None, "Could not create the item primitive object"

    # 缩放对象以匹配比率，保持上面设置的最大尺寸
    if width < height:
        itm_obj.scale[0] = width/height
    elif height < width:
        itm_obj.scale[1] = height/width
    bpy.ops.object.transform_apply(scale=True)#应用缩放

    # Deselect faces now, as seetting face.select = False doens't work even现在取消选择面，因为seetting face.select=False甚至不起作用
    # though using face.select = True does work尽管使用face.select=True确实有效
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='FACE')  # ideally capture initial state
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    if transparency is True:
        # 对比图像的alpha位置数据，对符合阈值的进行选择
        alpha_faces = list(image.pixels)[3::4]
        uv = itm_obj.data.uv_layers.active
        #
        #w_even_add = (-0.5 if width%2==0 else 0) + width
        #h_even_add = (-0.5 if height%2==0 else 0) + height
        facenum=0
        for face in itm_obj.data.polygons:
            if len(face.loop_indices) < 3:
                continue

            # 因为我们只生成了uv和网格，所以可以安全地获取img
            # 与面中心的坐标，与目标中心的偏移
            # face.center[0]是中心X值
            #img_x指像素块所在x位置
            #img_x = int((face.center[0]*width + width + 1)/2)-1
            #img_y = int((face.center[1]*height + height + 1)/2)-1
            # 现在验证这个图像索引是否低于alpha值数量
            
            if len(alpha_faces) > facenum:
                #alpha = alpha_faces[img_y*width + img_x]
                alpha = alpha_faces[facenum]
                facenum+=1
            else: # 防止报错，先跳过循环
                continue
            if alpha < threshold:
                face.select = True
            #else:
                #print(facenum)
                #print(img_x,img_y,img_y*width + img_x)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='FACE')
        bpy.ops.object.mode_set(mode='OBJECT')

    #itm_obj.location = util.get_cuser_location(context)#物体定位到3D游标

    # 材质和纹理部分
    # 待办事项: 在这里使用generate函数
    mat = bpy.data.materials.new(name)
    mat.name = name

    # 用生成材质替换？
    engine = bpy.context.scene.render.engine
    if engine == 'BLENDER_RENDER' or engine == 'BLENDER_GAME':
        tex = bpy.data.textures.new(name, type = 'IMAGE')
        tex.image = image
        mat.specular_intensity = 0
        mtex = mat.texture_slots.add()
        mtex.texture = tex
        tex.name = name
        tex.use_interpolation = 0
        tex.use_mipmap = 0
        tex.filter_type = 'BOX'
        tex.filter_size = 0.1
        if transparency is True:
            mat.use_transparency = 1
            mat.alpha = 0
            mat.texture_slots[0].use_map_alpha = 1
    elif engine=='CYCLES' or engine=='BLENDER_EEVEE':
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        for node in nodes:
            nodes.remove(node)

        diffuse_node = nodes.new(type="ShaderNodeBsdfDiffuse")
        tex_node = nodes.new(type='ShaderNodeTexImage')
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        tex_node.image = image
        tex_node.interpolation = 'Closest'

        if transparency == 0:
            links.new(tex_node.outputs[0], diffuse_node.inputs[0])
            links.new(diffuse_node.outputs[0], output_node.inputs[0])

            diffuse_node.location[0] -= 200
            diffuse_node.location[1] -= 100
            tex_node.location[0] -= 400
            output_node.location[0] += 200
        else:
            transp_node = nodes.new(type='ShaderNodeBsdfTransparent')
            mix_node = nodes.new(type='ShaderNodeMixShader')
            links.new(tex_node.outputs[0], diffuse_node.inputs[0])
            links.new(diffuse_node.outputs[0], mix_node.inputs[2])
            links.new(transp_node.outputs[0], mix_node.inputs[1])
            links.new(tex_node.outputs[1], mix_node.inputs[0])
            links.new(mix_node.outputs[0], output_node.inputs[0])

            transp_node.location[0] -= 200
            transp_node.location[1] += 100
            diffuse_node.location[0] -= 200
            diffuse_node.location[1] -= 100
            tex_node.location[0] -= 400
            output_node.location[0] += 200

    # 最终对象已更新
    if thickness > 0:
        mod = itm_obj.modifiers.new(type='SOLIDIFY', name='solid')
        mod.thickness = thickness/max([width, height])
        mod.offset = 0
    itm_obj.data.name = name
    bpy.context.object.data.materials.append(mat)
    itm_obj.name = name

    # 设置图像，主要与搅拌机内部相关
    if hasattr(itm_obj.data, "uv_textures"):
        for uv_face in itm_obj.data.uv_textures.active.data:
            uv_face.image = image
    return itm_obj, None

def spawn_item_from_pixels(context, max_pixels, thickness, threshold,
    transparency, image, alpha_pixels, tile_xy):
    """
    用像素数组生成item的函数

    参数
        context
        path: 图像文件的完整路径
        max_pixels: int, maximum number of output faces, will scale down
        thickness: 实心修改器的厚度，最小为0
        threshold: float, alpha值，低于该值的面将被删除
        transparency(透明度): bool, 删除低于阈值的面
        image:图片对象
        alpha_pixels:alpha通道
        tile_xy: tile的尺寸
    """

    # # 加载图像并初始化对象
    # image = None  # 图像数据块
    # img_str = os.path.basename(path)
    name = image.name
    # abspath = bpy.path.abspath(path)

    # if img_str in bpy.data.images and bpy.path.abspath(
    #         bpy.data.images[img_str].filepath) == abspath:
    #     image = bpy.data.images[img_str]
    # elif not path or not os.path.isfile(abspath):
    #     return None, "File not found"
    # else:
    #     image = bpy.data.images.load(abspath)

    # # 缩放图像
    # pix = len(image.pixels)/4
    # if pix > max_pixels:
    #     #待办事项: 删除循环并进行更多直接调整大小
    #     while pix > max_pixels:
    #         width = image.size[0]
    #         height = image.size[1]
    #         image.scale(width/1.5,height/1.5)
    #         pix = len(image.pixels)/4
    width = tile_xy[0] # 宽度
    height = tile_xy[1] # 高度

    if width == 0 or height == 0:
        return None, "图像具有无效的0大小维度"

    # 新方法，从一个UV网格开始并从中删除面
    if bv28():
        bpy.ops.mesh.primitive_grid_add(
            x_subdivisions=width+1, # outter edges count as a subdiv外缘作为细分曲面计算
            y_subdivisions=height+1, # outter edges count as a subdiv
            size=2,
            calc_uvs=True,
            location=(0,0,0))
    elif bpy.app.version < (2, 77): # could be 2, 76 even
        bpy.ops.mesh.primitive_grid_add(
            x_subdivisions=height+1, # outter edges count as a subdiv
            y_subdivisions=width+1, # outter edges count as a subdiv
            radius=1,
            location=(0,0,0))
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.uv.unwrap()
        bpy.ops.object.mode_set(mode='OBJECT')
    else:
        bpy.ops.mesh.primitive_grid_add(
            x_subdivisions=height+1, # outter edges count as a subdiv
            y_subdivisions=width+1, # outter edges count as a subdiv
            radius=1,
            calc_uvs=True,
            location=(0,0,0))
    itm_obj = context.object

    if not itm_obj:
        print("Error, 无法创建item基本对象")
        return None, "Could not create the item primitive object"

    # 缩放对象以匹配比率，保持上面设置的最大尺寸
    if width < height:
        itm_obj.scale[0] = width/height
    elif height < width:
        itm_obj.scale[1] = height/width
    bpy.ops.object.transform_apply(scale=True)#应用缩放

    # Deselect faces now, as seetting face.select = False doens't work even现在取消选择面，因为seetting face.select=False甚至不起作用
    # though using face.select = True does work尽管使用face.select=True确实有效
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='FACE')  # ideally capture initial state
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    if transparency is True:
        # 对比图像的alpha位置数据，对符合阈值的进行选择
        uv = itm_obj.data.uv_layers.active
        facenum=0
        for face in itm_obj.data.polygons:
            if len(face.loop_indices) < 3:
                continue

            # 因为我们只生成了uv和网格，所以可以安全地获取img
            # 与面中心的坐标，与目标中心的偏移
            # face.center[0]是中心X值
            #img_x指像素块所在x位置
            #img_x = int((face.center[0]*width + width + 1)/2)-1
            #img_y = int((face.center[1]*height + height + 1)/2)-1
            # 现在验证这个图像索引是否低于alpha值数量
            
            if len(alpha_pixels) > facenum:
                alpha = alpha_pixels[facenum]
                facenum+=1
            else: # 防止报错，先跳过循环
                continue
            if alpha < threshold:
                face.select = True
            #else:
                #print(facenum)
                #print(img_x,img_y,img_y*width + img_x)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='FACE')
        bpy.ops.object.mode_set(mode='OBJECT')

    #itm_obj.location = util.get_cuser_location(context)#物体定位到3D游标

    # 材质和纹理部分
    # 待办事项: 在这里使用generate函数
    mat = bpy.data.materials.new(name)
    mat.name = name

    # 用生成材质替换？
    engine = bpy.context.scene.render.engine
    if engine == 'BLENDER_RENDER' or engine == 'BLENDER_GAME':
        tex = bpy.data.textures.new(name, type = 'IMAGE')
        tex.image = image
        mat.specular_intensity = 0
        mtex = mat.texture_slots.add()
        mtex.texture = tex
        tex.name = name
        tex.use_interpolation = 0
        tex.use_mipmap = 0
        tex.filter_type = 'BOX'
        tex.filter_size = 0.1
        if transparency is True:
            mat.use_transparency = 1
            mat.alpha = 0
            mat.texture_slots[0].use_map_alpha = 1
    elif engine=='CYCLES' or engine=='BLENDER_EEVEE':
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        for node in nodes:
            nodes.remove(node)

        diffuse_node = nodes.new(type="ShaderNodeBsdfDiffuse")
        tex_node = nodes.new(type='ShaderNodeTexImage')
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        tex_node.image = image
        tex_node.interpolation = 'Closest'

        if transparency == 0:
            links.new(tex_node.outputs[0], diffuse_node.inputs[0])
            links.new(diffuse_node.outputs[0], output_node.inputs[0])

            diffuse_node.location[0] -= 200
            diffuse_node.location[1] -= 100
            tex_node.location[0] -= 400
            output_node.location[0] += 200
        else:
            transp_node = nodes.new(type='ShaderNodeBsdfTransparent')
            mix_node = nodes.new(type='ShaderNodeMixShader')
            links.new(tex_node.outputs[0], diffuse_node.inputs[0])
            links.new(diffuse_node.outputs[0], mix_node.inputs[2])
            links.new(transp_node.outputs[0], mix_node.inputs[1])
            links.new(tex_node.outputs[1], mix_node.inputs[0])
            links.new(mix_node.outputs[0], output_node.inputs[0])

            transp_node.location[0] -= 200
            transp_node.location[1] += 100
            diffuse_node.location[0] -= 200
            diffuse_node.location[1] -= 100
            tex_node.location[0] -= 400
            output_node.location[0] += 200

    # 最终对象已更新
    if thickness > 0:
        mod = itm_obj.modifiers.new(type='SOLIDIFY', name='solid')
        #mod.thickness = thickness/max([width, height])
        mod.thickness = 0.0625
        mod.offset = 0
    itm_obj.data.name = name
    bpy.context.object.data.materials.append(mat)
    itm_obj.name = name

    # 设置图像，主要与搅拌机内部相关
    if hasattr(itm_obj.data, "uv_textures"):
        for uv_face in itm_obj.data.uv_textures.active.data:
            uv_face.image = image
    return itm_obj, None



def spawn_plane_from_pixels(context, max_pixels, thickness, threshold,
    transparency, image, alpha_pixels, tile_xy):
    """
    用像素数组生成item的函数

    参数
        context
        path: 图像文件的完整路径
        max_pixels: int, maximum number of output faces, will scale down
        thickness: 实心修改器的厚度，最小为0
        threshold: float, alpha值，低于该值的面将被删除
        transparency(透明度): bool, 删除低于阈值的面
        image:图片对象
        alpha_pixels:alpha通道
        tile_xy: tile的尺寸
    """

    # # 加载图像并初始化对象
    # image = None  # 图像数据块
    # img_str = os.path.basename(path)
    name = image.name
    # abspath = bpy.path.abspath(path)

    # if img_str in bpy.data.images and bpy.path.abspath(
    #         bpy.data.images[img_str].filepath) == abspath:
    #     image = bpy.data.images[img_str]
    # elif not path or not os.path.isfile(abspath):
    #     return None, "File not found"
    # else:
    #     image = bpy.data.images.load(abspath)

    # # 缩放图像
    # pix = len(image.pixels)/4
    # if pix > max_pixels:
    #     #待办事项: 删除循环并进行更多直接调整大小
    #     while pix > max_pixels:
    #         width = image.size[0]
    #         height = image.size[1]
    #         image.scale(width/1.5,height/1.5)
    #         pix = len(image.pixels)/4
    width = tile_xy[0] # 宽度
    height = tile_xy[1] # 高度

    if width == 0 or height == 0:
        return None, "图像具有无效的0大小维度"

    # 新方法，从一个UV网格开始并从中删除面
    if bv28():
        bpy.ops.mesh.primitive_grid_add(
            x_subdivisions=width+1, # outter edges count as a subdiv外缘作为细分曲面计算
            y_subdivisions=height+1, # outter edges count as a subdiv
            size=2,
            calc_uvs=True,
            location=(0,0,0))
    elif bpy.app.version < (2, 77): # could be 2, 76 even
        bpy.ops.mesh.primitive_grid_add(
            x_subdivisions=height+1, # outter edges count as a subdiv
            y_subdivisions=width+1, # outter edges count as a subdiv
            radius=1,
            location=(0,0,0))
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.uv.unwrap()
        bpy.ops.object.mode_set(mode='OBJECT')
    else:
        bpy.ops.mesh.primitive_grid_add(
            x_subdivisions=height+1, # outter edges count as a subdiv
            y_subdivisions=width+1, # outter edges count as a subdiv
            radius=1,
            calc_uvs=True,
            location=(0,0,0))
    itm_obj = context.object

    if not itm_obj:
        print("Error, 无法创建item基本对象")
        return None, "Could not create the item primitive object"

    # # 缩放对象以匹配比率，保持上面设置的最大尺寸
    # if width < height:
    #     itm_obj.scale[0] = width/height
    # elif height < width:
    #     itm_obj.scale[1] = height/width
    # bpy.ops.object.transform_apply(scale=True)#应用缩放

    # Deselect faces now, as seetting face.select = False doens't work even现在取消选择面，因为seetting face.select=False甚至不起作用
    # though using face.select = True does work尽管使用face.select=True确实有效
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='FACE')  # ideally capture initial state
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    if transparency is True:
        # 对比图像的alpha位置数据，对符合阈值的进行选择
        uv = itm_obj.data.uv_layers.active
        facenum=0
        for face in itm_obj.data.polygons:
            if len(face.loop_indices) < 3:
                continue

            # 因为我们只生成了uv和网格，所以可以安全地获取img
            # 与面中心的坐标，与目标中心的偏移
            # face.center[0]是中心X值
            #img_x指像素块所在x位置
            #img_x = int((face.center[0]*width + width + 1)/2)-1
            #img_y = int((face.center[1]*height + height + 1)/2)-1
            # 现在验证这个图像索引是否低于alpha值数量
            
            if len(alpha_pixels) > facenum:
                alpha = alpha_pixels[facenum]
                facenum+=1
            else: # 防止报错，先跳过循环
                continue
            if alpha < threshold:
                face.select = True
            #else:
                #print(facenum)
                #print(img_x,img_y,img_y*width + img_x)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='FACE')
        bpy.ops.object.mode_set(mode='OBJECT')

    #itm_obj.location = util.get_cuser_location(context)#物体定位到3D游标

    # 材质和纹理部分
    # 待办事项: 在这里使用generate函数
    mat = bpy.data.materials.new(name)
    mat.name = name

    # 用生成材质替换？
    engine = bpy.context.scene.render.engine
    if engine == 'BLENDER_RENDER' or engine == 'BLENDER_GAME':
        tex = bpy.data.textures.new(name, type = 'IMAGE')
        tex.image = image
        mat.specular_intensity = 0
        mtex = mat.texture_slots.add()
        mtex.texture = tex
        tex.name = name
        tex.use_interpolation = 0
        tex.use_mipmap = 0
        tex.filter_type = 'BOX'
        tex.filter_size = 0.1
        if transparency is True:
            mat.use_transparency = 1
            mat.alpha = 0
            mat.texture_slots[0].use_map_alpha = 1
    elif engine=='CYCLES' or engine=='BLENDER_EEVEE':
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        for node in nodes:
            nodes.remove(node)

        diffuse_node = nodes.new(type="ShaderNodeBsdfDiffuse")
        tex_node = nodes.new(type='ShaderNodeTexImage')
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        tex_node.image = image
        tex_node.interpolation = 'Closest'

        if transparency == 0:
            links.new(tex_node.outputs[0], diffuse_node.inputs[0])
            links.new(diffuse_node.outputs[0], output_node.inputs[0])

            diffuse_node.location[0] -= 200
            diffuse_node.location[1] -= 100
            tex_node.location[0] -= 400
            output_node.location[0] += 200
        else:
            transp_node = nodes.new(type='ShaderNodeBsdfTransparent')
            mix_node = nodes.new(type='ShaderNodeMixShader')
            links.new(tex_node.outputs[0], diffuse_node.inputs[0])
            links.new(diffuse_node.outputs[0], mix_node.inputs[2])
            links.new(transp_node.outputs[0], mix_node.inputs[1])
            links.new(tex_node.outputs[1], mix_node.inputs[0])
            links.new(mix_node.outputs[0], output_node.inputs[0])

            transp_node.location[0] -= 200
            transp_node.location[1] += 100
            diffuse_node.location[0] -= 200
            diffuse_node.location[1] -= 100
            tex_node.location[0] -= 400
            output_node.location[0] += 200

    # 最终对象已更新
    if thickness > 0:
        mod = itm_obj.modifiers.new(type='SOLIDIFY', name='solid')
        #mod.thickness = thickness/max([width, height])
        mod.thickness = 0.0625
        mod.offset = 0
    itm_obj.data.name = name
    bpy.context.object.data.materials.append(mat)
    itm_obj.name = name

    # 设置图像，主要与搅拌机内部相关
    if hasattr(itm_obj.data, "uv_textures"):
        for uv_face in itm_obj.data.uv_textures.active.data:
            uv_face.image = image
    return itm_obj, None



# -----------------------------------------------------------------------------
# Operator classes
# -----------------------------------------------------------------------------



def register():
    bpy.utils.register_class(MCPREP_OT_spawn_item_from_file)
    bpy.utils.register_class(MCPREP_OT_scale_uv)


def unregister():
    bpy.utils.unregister_class(MCPREP_OT_spawn_item_from_file)
    bpy.utils.unregister_class(MCPREP_OT_scale_uv)
