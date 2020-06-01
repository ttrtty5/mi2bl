import bpy

class other_cache_clean(bpy.types.Operator):
    bl_idname = 'mi2bl.other_cache_clean'
    bl_label = '缓存清除'

    def execute(self,context):
        meshnum = 0
        for block in bpy.data.meshes:
            if block.users == 0:
                bpy.data.meshes.remove(block)
                meshnum += 1

        matnum = 0
        for block in bpy.data.materials:
            if block.users == 0:
                bpy.data.materials.remove(block)
                matnum += 1

        texturenum = 0
        for block in bpy.data.textures:
            if block.users == 0:
                bpy.data.textures.remove(block)
                texturenum += 1

        imagenum = 0
        for block in bpy.data.images:
            if block.users == 0:
                bpy.data.images.remove(block)
                imagenum += 1
        
        清除记录 = "缓存已清除"
        清除记录 += ", 共%d网格, %d材质, %d纹理, %d图片"%(meshnum, matnum, texturenum, imagenum)
        self.report({'INFO'},清除记录)
        return {'FINISHED'}

### 动力学物体全局禁用启用部分 ###
class 生成动力学集合(bpy.types.Operator):
    '''不知道为什么，找不到别人有写过这种功能,只好自己写了\n大概是用于在k帧的时候禁用所有的布料软体的模拟'''
    # 先生成动力学物体集合
    bl_idname = 'mi2bl.other_spawn_dynamic_collections'
    bl_label = '生成动力学集合'
    def execute(self, context):
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection
        if "动力学物体" not in bpy.context.view_layer.layer_collection.children:
            coll=bpy.data.collections.new("动力学物体")
            bpy.context.view_layer.active_layer_collection.collection.children.link(coll)
        else:
            coll=bpy.data.collections["动力学物体"]
        # 遍历场景内的物体
        for obj in bpy.context.scene.objects:
            # 允许的物体类型
            allow_type = ('MESH', 'CURVE', 'LATTICE', 'SURFACE')
            modi_type = ('SOFT_BODY', 'CLOTH')
            if obj.type in allow_type:
                for modi in obj.modifiers:
                    if modi.type in modi_type :
                        # 查找修改器,find不知道怎么用
                        if obj.name in coll.objects:
                            # 物体是否已经在集合内
                            continue
                        coll.objects.link(obj)
                        # modi.show_viewport = False
        # 有没有感觉不写注释还看得懂，加完注释再看，这写的啥玩意啊
        return {'FINISHED'}

class 动力学集合禁用(bpy.types.Operator):
    '''禁用动力学集合内所有物体修改器的可视性'''
    bl_idname = 'mi2bl.other_dynamic_disable'
    bl_label = "动力学集合禁用"
    @classmethod
    def poll(cls,context):
        return "动力学物体" in bpy.context.scene.collection.children

    def execute(self, context):
        coll = bpy.data.collections["动力学物体"]
        for obj in coll.objects:
            # 允许的物体类型
            allow_type = ('MESH', 'CURVE', 'LATTICE', 'SURFACE')
            modi_type = ('SOFT_BODY', 'CLOTH')
            if obj.type in allow_type:
                for modi in obj.modifiers:
                    if modi.type in modi_type :
                        modi.show_viewport = False
        return {'FINISHED'}

class 动力学集合启用(bpy.types.Operator):
    '''启用动力学集合内所有物体修改器的可视性'''
    bl_idname = 'mi2bl.other_dynamic_enable'
    bl_label = '动力学集合启用'
    @classmethod
    def poll(cls,context):
        return "动力学物体" in bpy.context.scene.collection.children
    
    def execute(self, context):
        coll = bpy.data.collections["动力学物体"]
        for obj in coll.objects:
            # 允许的物体类型
            allow_type = ('MESH', 'CURVE', 'LATTICE', 'SURFACE')
            modi_type = ('SOFT_BODY', 'CLOTH')
            if obj.type in allow_type:
                for modi in obj.modifiers:
                    if modi.type in modi_type :
                        modi.show_viewport = True
        return {'FINISHED'}

### 贴图合并(重映射)部分 ###
# 生成上下文
def AssembleOverride(atype, rtype):
    for oWindow in bpy.context.window_manager.windows:
        oScreen = oWindow.screen
        for oArea in oScreen.areas:
            if oArea.type == atype:
                for oRegion in oArea.regions:
                    if oRegion.type == rtype:
                        oContextOverride = {
                                'window': oWindow,
                                'screen': oScreen,
                                'area': oArea,
                                'region': oRegion,
                                'scene': bpy.context.scene,
                                'edit_object': bpy.context.edit_object,
                                'active_object': bpy.context.active_object,
                                'selected_objects': bpy.context.selected_objects
                                }
                        # print("-AssembleOverride() created override context: ", oContextOverride)
                        return oContextOverride
    raise Exception("ERROR: AssembleOverride()")

def enum_imglist(self, context):
    if len(测试用ops.img_templist)==0:
        items = [("错误情况","错误情况,显示请联系开发","")]
    else:
        items = 测试用ops.img_templist
    return items

class 贴图重映射(bpy.types.Operator):
    bl_idname = 'mi2bl.other_texture_remap'
    bl_label = '贴图重映射'

    img_templist = []
    # 奇怪的bug,invoke虽然先于enum_imglist运行，但enum_imglist内访问到的img_templist始终是[]
    # 只好借位置了

    img_list: bpy.props.EnumProperty(
        name="相同图片",
        description="检测到的相同图片",
        items=enum_imglist)

    @classmethod
    def poll(cls,context):
        return bpy.context.area.type == 'IMAGE_EDITOR'

    def invoke(self, context, event):
        测试用ops.img_templist = []
        if context.area.spaces.active.image == None:
            self.report({'INFO'},"当前窗口无图片")
            return {'CANCELLED'}
        img_path = context.area.spaces.active.image.filepath
        img_name = context.area.spaces.active.image.name
        num = 0
        for img in bpy.data.images:
            if img.name == img_name:
                continue
            if img.filepath == img_path:
                print((img, img.name, "", img.preview.icon_id, num))
                测试用ops.img_templist.append((img.name, img.name, "重复加载的图片，确定清除", img.preview.icon_id, num))
                num+=1
        if len(测试用ops.img_templist) == 0:
            self.report({'INFO'},"未检测出相同图片")
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        col = self.layout
        col.prop(self,'img_list')
        row = col.row()
        row.label(text="是否删除?")

    def execute(self, context):
        img_path = bpy.context.area.spaces.active.image.filepath
        img_name = bpy.context.area.spaces.active.image.name
        # 获取图片编辑器里的图片
        # for area in bpy.context.screen.areas:
        #    if area.type == 'IMAGE_EDITOR':
        #       area.spaces.active.image = bpy.data.images['Your_image_name']
        
        # ['EMPTY', 'VIEW_3D', 'TIMELINE', 'GRAPH_EDITOR', 'DOPESHEET_EDITOR',
        # 'NLA_EDITOR', 'IMAGE_EDITOR', 'CLIP_EDITOR', 'SEQUENCE_EDITOR',
        # 'NODE_EDITOR', 'TEXT_EDITOR', 'LOGIC_EDITOR', 'PROPERTIES', 'OUTLINER',
        # 'USER_PREFERENCES', 'INFO', 'FILE_BROWSER', 'CONSOLE']
        atype = 'OUTLINER'
        # ['WINDOW', 'HEADER', 'CHANNELS', 'TEMPORARY', 'UI', 'TOOLS',
        # 'TOOL_PROPS', 'PREVIEW']
        rtype = 'WINDOW'

        override = AssembleOverride(atype, rtype)
        
        # old_id 和 new_id 必须已经存在，否则操作员将失败
        rmlist = 测试用ops.img_templist
        for img in rmlist:
            bpy.ops.outliner.id_remap(
                    override,
                    id_type='IMAGE',
                    old_id=img[0],
                    new_id=img_name
                    )
            bpy.data.images.remove(bpy.data.images[img[0]])
        return {'FINISHED'}
    

### 测试 ###
class 测试用ops(bpy.types.Operator):
    bl_idname = 'mi2bl.other_test'
    bl_label = 'ops测试'

    # 借用位置
    img_templist = []

    def execute(self, context):
        teststr = context.area.spaces.active.image
        print(teststr)
        self.report({'INFO'},str(teststr))
        return {'FINISHED'}

classes=(
    other_cache_clean,
    生成动力学集合,
    动力学集合禁用,
    动力学集合启用,
    贴图重映射,
    测试用ops
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)