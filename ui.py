import bpy

# UI面板变量在 多item图分割.py 394
class TTR_PT_UI(bpy.types.Panel):
    '''3d视图n侧边栏创建区的面板'''
    #bl_idname = 'TTR_UI'
    bl_label = 'MI联动组件'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'M2B'
    
    def draw(self,context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(context.window_manager.mi2bl, 'mesh_UI',text = "建模",toggle=True)
        row.prop(context.window_manager.mi2bl, 'convert_UI',text = "转换",toggle=True)
        row.prop(context.window_manager.mi2bl, 'notok_UI',text = "未完成",toggle=True)
        row.prop(context.window_manager.mi2bl, 'extra_UI_state',text = "额外",toggle=True)
        
        if context.window_manager.mi2bl.mesh_UI:
            box = layout.box()
            label = box.label(text="单item图:")
            row = box.row()
            row.operator('object.spawn_item_file')

            row = box.row()
            label=box.label(text="多item图:")
            row = box.row()
            #if context.window_manager.mi2bl.active_image!="":
            if bpy.data.window_managers['WinMan'].mi2bl.img_num>0:
                item_image_list = row.prop(context.window_manager.mi2bl,"active_image",text="",icon='RENDERLAYERS')
                row.operator('mi2bl.delete_preview_item_list',text="",icon="PANEL_CLOSE")
            
            row.operator('mi2bl.item_cut_button')

            if context.window_manager.mi2bl.UI_state:
                column = box.row()
                row = column.row(align=True)
                sub = row.row(align=True)
                sub.scale_y = 6
                sub.operator('mi2bl.previous_item', text='', icon='TRIA_LEFT')
                sub = sub.row(align=True)
                sub.scale_y = 0.17
                sub.template_icon_view(context.window_manager.mi2bl, 
                    'assets_files',show_labels=True, 
                    scale_popup=2)
                sub = sub.row(align=True)
                sub.scale_y = 6
                sub.operator('mi2bl.next_item', text='', icon='TRIA_RIGHT')
                row = box.row()
                row.operator('mi2bl.spawn_item_from_image')
                row.operator('mi2bl.spawn_item_from_image_pixelsize')


        if context.window_manager.mi2bl.convert_UI:
            row = layout.row()
            row.label(text="转换功能")
            box = layout.box()
            row = box.row()
            row.operator('mi2bl.import_miobject')
            row = box.row()
            row.operator('mi2bl.import_mbmodel')
        
        if context.window_manager.mi2bl.notok_UI:
            row = layout.row()
            row.label(text="未完成功能")
            box = layout.box()
            #row = layout.row()
            #row.operator('object.ttr_do_1')
            row = box.row()
            row.operator('export_test.rigiddata')
            row = box.row()
            row.operator('mi2bl.other_cache_clean')
            row = box.row()
            row.operator('ptcache.free_bake_all', text="Delete All Bakes")
            row.operator('ptcache.remove', text="Delete Bakes")

        if context.window_manager.mi2bl.extra_UI_state:
            row = layout.row()
            row.label(text="1.")
            row = layout.row()
            row.operator('mi2bl.other_spawn_dynamic_collections')
            row = layout.row()
            row.operator('mi2bl.other_dynamic_disable')
            row.operator('mi2bl.other_dynamic_enable')
            row = layout.row()
            row.operator('mi2bl.object_center')
            


def mi2bl_img_tools(self, context):
    '''在图片编辑器里添加一个按钮'''
    layout = self.layout
    layout.separator()
    layout.label(text="mi2bl额外工具")
    col=layout.column(align=True)
    col.operator('mi2bl.other_texture_remap')



classes=(
    TTR_PT_UI,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    if hasattr(bpy.types, 'IMAGE_MT_image'): # 2.8 *and* 2.7
        # 这是uv的下拉菜单，不是面板
        bpy.types.IMAGE_MT_image.append(mi2bl_img_tools)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    if hasattr(bpy.types, "IMAGE_MT_image"): # 2.8 *and* 2.7
        bpy.types.IMAGE_MT_image.remove(mi2bl_img_tools)