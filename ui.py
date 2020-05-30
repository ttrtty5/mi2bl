import bpy

class TTR_PT_UI(bpy.types.Panel):
    '''3d视图n侧边栏创建区的面板'''
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

        row = layout.row()
        row.label(text="转换功能")
        row = layout.row()
        row.operator('mi2bl.import_miobject')
        row = layout.row()
        row.operator('mi2bl.import_mbmodel')
        row = layout.row()
        row.label(text="未完成功能")
        #row = layout.row()
        #row.operator('object.ttr_do_1')
        row = layout.row()
        row.operator('export_test.rigiddata')
        row = layout.row()
        row.operator('mi2bl.other_cache_clean')
        row = layout.row()
        row.operator("ptcache.free_bake_all", text="Delete All Bakes")
        row.operator("ptcache.remove", text="Delete Bakes")
        layout.prop(context.window_manager.mi2bl,"extra_UI_state",text = "额外功能:")
        if context.window_manager.mi2bl.extra_UI_state:
            row = layout.row()
            row.operator('mi2bl.other_spawn_dynamic_collections')
            row = layout.row()
            row.operator('mi2bl.other_dynamic_disable')
            row.operator('mi2bl.other_dynamic_enable')
        


classes=(
    TTR_PT_UI,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)