import importlib

if "bpy" in locals():
    importlib.reload(MCPREP_OT_spawn_item)
    importlib.reload(多item图分割)
else:
    import bpy
#    from . import ()
    from .Mcprep import(
        MCPREP_OT_spawn_item,
        多item图分割
        )
    from .mi_importer import(
        import_templates,
        )

module_list = (
    MCPREP_OT_spawn_item,
    多item图分割,
    import_templates
    )

def register():
    for mod in module_list:
        mod.register()

def unregister():
    for mod in reversed(module_list):
        mod.unregister()
