import json
import bpy
from math import radians



def 提取父级节点树(MiJsonData):
    ParentTreeInfo={}#ParentTreeInfo={子节点:父节点}
    for object in MiJsonData["timelines"]:
        ParentTreeInfo[object["id"]]=object["parent"]
    #print(ParentTreeInfo)

    ParentTree={}#ParentTree={父节点:子节点}
    for object in MiJsonData["timelines"]:
        if object['type'] not in ('cube','item','folder'):
            continue
        id=object["id"]
        parent=object["parent"]
        if parent in ParentTree:
            ParentTree[parent].update({id:None})
            continue
        ParentTree[parent]={id:None}

    def 遍历字典返回(id,value,location):
        for 子id in location:
            if location[子id] != None:
                遍历字典返回(id,value,location[子id])
            if 子id==id:
                location[子id]=value
                del ParentTree[id]

    while len(ParentTree)>1:
        for obj in list(ParentTree):
            if obj=='root':
                continue
            遍历字典返回(obj,ParentTree[obj],ParentTree['root'])
    if len(ParentTree)<1:
        ParentTree['root']=None
    return ParentTree

def 提取对应id的坐标(MiJsonData):
    MiIdtoPos={}
    for object in MiJsonData["timelines"]:
        MiIdtoPos[object["id"]]=object["keyframes"]
    return MiIdtoPos

def hex_to_tuple(text):
    #将hex转tuple
    r, g, b=text[0:2], text[2:4], text[4:6]
    rgba=(int(r,16)/255, int(g,16)/255, int(b,16)/255, 1)
    return rgba

def 给cube添加材质(timelinesJsonData):
    keyframe_data=timelinesJsonData['keyframes']['0']
    tex = keyframe_data['TEXTURE_OBJ'] if 'TEXTURE_OBJ' in keyframe_data else False
    mix_percent = keyframe_data['MIX_PERCENT'] if 'MIX_PERCENT' in keyframe_data else 0
    rgb_mul = hex_to_tuple(keyframe_data['RGB_MUL']) if 'RGB_MUL' in keyframe_data else (1, 1, 1, 1)
    mix_color = hex_to_tuple(keyframe_data['MIX_COLOR']) if 'MIX_COLOR' in keyframe_data else (0, 0, 0, 1)

    if timelinesJsonData['name'] == '':
        mat = bpy.data.materials.new("方块")
    else:
        mat = bpy.data.materials.new(timelinesJsonData['name'])
    
    mat.use_nodes=True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    for node in nodes:
        nodes.remove(node)

    diffuse_node = nodes.new(type="ShaderNodeBsdfDiffuse")
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    mulrgb = nodes.new(type="ShaderNodeMixRGB")
    mulrgb.blend_type = 'MULTIPLY'
    mixrgb = nodes.new(type="ShaderNodeMixRGB")
    
    if tex:
        tex_node = nodes.new(type='ShaderNodeTexImage')
        tex_node.image = bpy.data.images[tex]
        tex_node.interpolation = 'Closest'
        tex_node.location[0] -= 700
        links.new(tex_node.outputs[0],mulrgb.inputs[1])
    
    #设置参数
    mulrgb.inputs[0].default_value = 1
    mulrgb.inputs[2].default_value = rgb_mul
    mixrgb.inputs[0].default_value = mix_percent
    mixrgb.inputs[1].default_value = (1, 1, 1, 1)
    mixrgb.inputs[2].default_value = mix_color
    
    #link
    links.new(mulrgb.outputs[0],mixrgb.inputs[1])
    links.new(mixrgb.outputs[0],diffuse_node.inputs[0])
    links.new(diffuse_node.outputs[0],output_node.inputs[0])

    #整理节点
    output_node.location[0] += 200
    mixrgb.location[0] -= 200
    mulrgb.location[0] -= 400
    bpy.context.object.data.materials.append(mat)
    

#设置函数控制作用域
def 读取cube坐标并应用(timelinesJsonData):
    #MiObjPos=timelinesJsonData["default_values"]
    bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, location=(0, 0, 0))
    
    给cube添加材质(timelinesJsonData)
    #自义定中心(我好懒啊，原本的想法应该塞进自义定属性里，然后联动驱动器进行偏移)
    rot_point =timelinesJsonData["rot_point"] if timelinesJsonData["rot_point_custom"] else [ 0, -8, 0 ]
    #rot_point[x,z,y]
    bpy.context.object.location[0] -= rot_point[0]/16#x
    bpy.context.object.location[1] += rot_point[2]/16#y
    bpy.context.object.location[2] -= rot_point[1]/16#z
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    
    #把default_values设置成-1帧
    obj_default_pos=timelinesJsonData["default_values"]
    obj_default_pos_x=-obj_default_pos["POS_X"]/16 if "POS_X" in obj_default_pos.keys() else 0
    obj_default_pos_y=-obj_default_pos["POS_Y"]/16 if "POS_Y" in obj_default_pos.keys() else 0
    obj_default_pos_z=obj_default_pos["POS_Z"]/16 if "POS_Z" in obj_default_pos.keys() else 0
    bpy.context.object.location=[obj_default_pos_y, obj_default_pos_x, obj_default_pos_z]
    bpy.context.object.keyframe_insert(data_path="location", frame=0)
    
    
    MiObj=timelinesJsonData["keyframes"]
    for KeyNum in MiObj:
    
        POS_X=-MiObj[KeyNum]["POS_X"]/16 if "POS_X" in MiObj[KeyNum].keys() else 0
        POS_Y=-MiObj[KeyNum]["POS_Y"]/16 if "POS_Y" in MiObj[KeyNum].keys() else 0
        POS_Z=MiObj[KeyNum]["POS_Z"]/16 if "POS_Z" in MiObj[KeyNum].keys() else 0
    
        SCA_X=MiObj[KeyNum]["SCA_X"] if "SCA_X" in MiObj[KeyNum].keys() else 1
        SCA_Y=MiObj[KeyNum]["SCA_Y"] if "SCA_Y" in MiObj[KeyNum].keys() else 1
        SCA_Z=MiObj[KeyNum]["SCA_Z"] if "SCA_Z" in MiObj[KeyNum].keys() else 1
        
        bpy.context.object.location=[POS_Y, POS_X, POS_Z]
        #bpy.context.object.keyframe_insert(data_path="location", frame=int(KeyNum)+1)
        #设置关键帧
        bpy.context.object.scale = [SCA_Y,SCA_X,SCA_Z]
        #bpy.context.object.keyframe_insert(data_path="scale", frame=int(KeyNum)+1)
    '''
    mi的矩阵运算顺序是先缩放再旋转
    而bl的齐次坐标的顺序没法改，是先旋转再缩放，缩放会影响旋转
    所以先缩放应用再旋转
    '''

    #命名物体为id
    global NameDict
    bpy.context.object.name = timelinesJsonData["id"]
    if timelinesJsonData['name']=='':
        id=timelinesJsonData['id']
        name=timelinesJsonData['name']
        NameDict[id]='方块'
    else:
        id=timelinesJsonData['id']
        name=timelinesJsonData['name']
        NameDict[id]=name

def 读取item坐标并应用(timelinesJsonData):
    temp_id=timelinesJsonData['temp']
    obj_id=timelinesJsonData['id']

    #取消全选，上下文选择物体，应用缩放
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = bpy.data.objects[temp_id]
    bpy.data.objects[temp_id].select_set(True)
    
    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'})
    #应用修改器
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="solid")
    
    obj=bpy.context.object
    bpy.data.collections['obj'].objects.link(obj)
    bpy.data.collections['templates'].objects.unlink(obj)
    

    #自义定中心(我好懒啊，原本的想法应该塞进自义定属性里，然后联动驱动器进行偏移)
    rot_point =timelinesJsonData["rot_point"] if timelinesJsonData["rot_point_custom"] else [ 8, 0, 0.5 ]
    #rot_point[x,z,y]
    bpy.context.object.rotation_euler[0] =radians(90)
    bpy.context.object.rotation_euler[2] =radians(-90)
    bpy.context.object.location[0] -= rot_point[2]/16 - (0.5/16)#y
    bpy.context.object.location[1] += rot_point[0]/16 - 0.5#x
    bpy.context.object.location[2] -= rot_point[1]/16 - 0.5#z
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
    
    
    obj_default_pos=timelinesJsonData["default_values"]
    obj_default_pos_x=-obj_default_pos["POS_X"]/16 if "POS_X" in obj_default_pos.keys() else 0
    obj_default_pos_y=-obj_default_pos["POS_Y"]/16 if "POS_Y" in obj_default_pos.keys() else 0
    obj_default_pos_z=obj_default_pos["POS_Z"]/16 if "POS_Z" in obj_default_pos.keys() else 0
    bpy.context.object.location=[obj_default_pos_y, obj_default_pos_x, obj_default_pos_z]
    
    
    MiObj=timelinesJsonData["keyframes"]
    for KeyNum in MiObj:
    
        POS_X=-MiObj[KeyNum]["POS_X"]/16 if "POS_X" in MiObj[KeyNum].keys() else bpy.context.object.location[1]
        POS_Y=-MiObj[KeyNum]["POS_Y"]/16 if "POS_Y" in MiObj[KeyNum].keys() else bpy.context.object.location[0]
        POS_Z=MiObj[KeyNum]["POS_Z"]/16 if "POS_Z" in MiObj[KeyNum].keys() else bpy.context.object.location[2]
    
        SCA_X=MiObj[KeyNum]["SCA_X"] if "SCA_X" in MiObj[KeyNum].keys() else 1
        SCA_Y=MiObj[KeyNum]["SCA_Y"] if "SCA_Y" in MiObj[KeyNum].keys() else 1
        SCA_Z=MiObj[KeyNum]["SCA_Z"] if "SCA_Z" in MiObj[KeyNum].keys() else 1
        
        #设置关键帧
        bpy.context.object.location=[POS_Y, POS_X, POS_Z]
        bpy.context.object.scale = [SCA_Y,SCA_X,SCA_Z]
        #bpy.context.object.keyframe_insert(data_path="location", frame=int(KeyNum)+1)
        #bpy.context.object.keyframe_insert(data_path="scale", frame=int(KeyNum)+1)
        
    '''
    mi的矩阵运算顺序是先缩放再旋转
    而bl的齐次坐标的顺序没法改，是先旋转再缩放，缩放会影响旋转
    所以先缩放应用再旋转
    '''

    #命名物体为id
    global NameDict
    bpy.context.object.name = timelinesJsonData["id"]
    if timelinesJsonData['name']=='':
        id=timelinesJsonData['id']
        name=timelinesJsonData['name']
        NameDict[id]="方块"
    else:
        id=timelinesJsonData['id']
        name=timelinesJsonData['name']
        NameDict[id]=name

def 读取camera坐标并应用(timelinesJsonData):
    transdata = timelinesJsonData['keyframes']['0']
    POS_X = -transdata['POS_X']/16 if 'POS_X' in transdata else 0
    POS_Y = -transdata['POS_Y']/16 if 'POS_Y' in transdata else 0
    POS_Z = transdata['POS_Z']/16 if 'POS_Z' in transdata else 0
    ROT_X = -radians(transdata['ROT_X']) if 'ROT_X' in transdata else 0
    ROT_Y = -radians(transdata['ROT_Y']) if 'ROT_Y' in transdata else 0
    ROT_Z = radians(transdata['ROT_Z']) if 'ROT_Z' in transdata else 0
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(POS_Y, POS_X, POS_Z), rotation=(ROT_Y, ROT_Z, ROT_X))#XZY
    bpy.context.object.delta_rotation_euler=[radians(90),0,radians(90)]
    bpy.context.object.name = timelinesJsonData['id']
    

def 读取folder坐标并应用(timelinesJsonData):
    #MiObjPos=timelinesJsonData["default_values"]
    MiObjPos=timelinesJsonData["keyframes"]["0"]
    POS_X=-MiObjPos["POS_X"]/16 if "POS_X" in MiObjPos.keys() else 0
    POS_Y=-MiObjPos["POS_Y"]/16 if "POS_Y" in MiObjPos.keys() else 0
    POS_Z=MiObjPos["POS_Z"]/16 if "POS_Z" in MiObjPos.keys() else 0
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(POS_Y, POS_X, POS_Z))
    
    ROT_X=-radians(MiObjPos["ROT_X"]) if "ROT_X" in MiObjPos.keys() else 0
    ROT_Y=-radians(MiObjPos["ROT_Y"]) if "ROT_Y" in MiObjPos.keys() else 0
    ROT_Z=radians(MiObjPos["ROT_Z"]) if "ROT_Z" in MiObjPos.keys() else 0
    SCA_X=MiObjPos["SCA_X"] if "SCA_X" in MiObjPos.keys() else 1
    SCA_Y=MiObjPos["SCA_Y"] if "SCA_Y" in MiObjPos.keys() else 1
    SCA_Z=MiObjPos["SCA_Z"] if "SCA_Z" in MiObjPos.keys() else 1
    
    bpy.context.object.scale = [SCA_Y,SCA_X,SCA_Z]

    bpy.context.object.name = timelinesJsonData["id"]
    global NameDict
    if timelinesJsonData["name"]=="":
        id=timelinesJsonData['id']
        name=timelinesJsonData["name"]
        NameDict[id]='文件夹'
    else:
        id=timelinesJsonData['id']
        name=timelinesJsonData['name']
        NameDict[id]=name

def 通过Id设Parent(timelinesJsonData):
    id=timelinesJsonData["id"]
    ParentId=timelinesJsonData["parent"]
    if ParentId in bpy.data.objects:
        bpy.data.objects[id].parent = bpy.data.objects[ParentId]
    else:
        print('mi2bl:模型文件中存在无法识别的物体，请联系开发者')

def 缩放后才能旋转物体(id,pos):
    
    #取消全选，上下文选择物体，应用缩放
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = bpy.data.objects[id]
    bpy.data.objects[id].select_set(True)
    #bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)不能应用父级，应用会使子级上出现一个父级矩阵

    
    MiObjPos=pos[id]["0"]
    ROT_X=-radians(MiObjPos["ROT_X"]) if "ROT_X" in MiObjPos.keys() else 0
    ROT_Y=-radians(MiObjPos["ROT_Y"]) if "ROT_Y" in MiObjPos.keys() else 0
    ROT_Z=radians(MiObjPos["ROT_Z"]) if "ROT_Z" in MiObjPos.keys() else 0
    bpy.data.objects[id].rotation_euler = [ROT_Y,ROT_X,ROT_Z]
    
    
def 检测物体是否存在(id):
    #dict=[]
    #for obj in bpy.context.scene.objects:
    #    dict.append(obj.name)
    if id in bpy.data.objects:
        return True
    else:
        return False

#开始旋转
def 判断键内有无子集(dict, MiObjectJson):
    pos=提取对应id的坐标(MiObjectJson)
    for object in dict:
        #print(object)
        if not 检测物体是否存在(object):
            continue
        缩放后才能旋转物体(object,pos)
        if dict[object]!=None:
            判断键内有无子集(dict[object], MiObjectJson)


def main():
    with open("E:\暂存\方块.miobject","r")as f:
        MiObjectData=f.read()
    MiObjectJson = json.loads(MiObjectData)
    #创建物体，并读取坐标和缩放
    for timelinesData in MiObjectJson["timelines"]:
        if timelinesData["type"]=="folder":
            读取folder坐标并应用(timelinesData)
        if timelinesData["type"]=="cube":
            读取cube坐标并应用(timelinesData)
        if timelinesData["type"]=="item":
            读取item坐标并应用(timelinesData)
    #创建通过父级查找子级的字典
    ParentTree=提取父级节点树(MiObjectJson)
    dict=ParentTree['root']
    
    #应用缩放，并将缩放传给子级
    应用缩放并传给子级(dict)
    
    #绑定父级
    for timelinesData in MiObjectJson["timelines"]:
        if timelinesData["type"] not in ("folder","cube"):
            continue
        if timelinesData["parent"]!="root":
            通过Id设Parent(timelinesData)
    
    #开始旋转
    判断键内有无子集(dict)
        
    #恢复命名
    global NameDict
    for nnn123 in NameDict:
        bpy.data.objects[nnn123].name=NameDict[nnn123]


def 应用缩放并传给子级(dict):
    for obj in dict:
        if dict[obj]==None:
            #选择最子子级，应用缩放，跳下一个循环
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = bpy.data.objects[obj]
            bpy.data.objects[obj].select_set(True)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            continue
        #缩放传递给子级
        for child_obj in dict[obj]:
            for num in range(3):
                bpy.data.objects[child_obj].scale[num] *= bpy.data.objects[obj].scale[num]
                bpy.data.objects[child_obj].location[num] *= bpy.data.objects[obj].scale[num]
            
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = bpy.data.objects[obj]
        bpy.data.objects[obj].select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        应用缩放并传给子级(dict[obj])

#物体名称字典
NameDict={}
def spawn_timelines_obj(MiObjectJson):
    #创建物体
    for timelinesData in MiObjectJson["timelines"]:
        if timelinesData["type"]=='folder':
            读取folder坐标并应用(timelinesData)
        if timelinesData["type"]=='cube':
            读取cube坐标并应用(timelinesData)
        if timelinesData["type"]=='item':
            读取item坐标并应用(timelinesData)
        if timelinesData["type"]=='camera':
            读取camera坐标并应用(timelinesData)
            return 0
    
    #创建通过父级查找子级的字典
    ParentTree=提取父级节点树(MiObjectJson)
    dict=ParentTree['root']
    
    if dict==None:
        return 0
    #应用缩放，并将缩放传给子级
    应用缩放并传给子级(dict)
    
    #绑定父级
    for timelinesData in MiObjectJson['timelines']:
        if timelinesData['type'] not in ('folder', 'cube', 'item'):
            continue
        if timelinesData['parent']!="root":
            通过Id设Parent(timelinesData)
            

    #开始旋转
    判断键内有无子集(dict, MiObjectJson)
    
    #恢复命名
    #global NameDict
    #for nnn123 in NameDict:
    #    bpy.data.objects[nnn123].name=NameDict[nnn123]


#bpy.context.view_layer.objects.active 设置活动元素
#bpy.data.objects['Plane.001'].select_set(True)
