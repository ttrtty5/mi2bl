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

classes=(
    other_cache_clean,
    生成动力学集合,
    动力学集合禁用,
    动力学集合启用
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)