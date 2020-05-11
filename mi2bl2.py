import json
import bpy
from math import radians

with open("E:\暂存\方块.miobject","r")as f:
    MiObjectData=f.read()

MiObjectJson = json.loads(MiObjectData)

#命名空间字典
NameDict={}

def 提取父级节点树(MiJsonData):
    ParentTreeInfo={}#ParentTreeInfo={子节点:父节点}
    for object in MiJsonData["timelines"]:
        ParentTreeInfo[object["id"]]=object["parent"]
    #print(ParentTreeInfo)

    ParentTree={}#ParentTree={父节点:子节点}
    for object in MiJsonData["timelines"]:
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
    return ParentTree

def 提取对应id的坐标(MiJsonData):
    MiIdtoPos={}
    for object in MiJsonData["timelines"]:
        MiIdtoPos[object["id"]]=object["keyframes"]
    return MiIdtoPos

#timelinesData = MiObjectJson["timelines"][0]
#print(timelinesData)

#设置函数控制作用域
def 读取cube坐标并应用(timelinesJsonData):
    #MiObjPos=timelinesJsonData["default_values"]
    MiObjPos=timelinesJsonData["keyframes"]["0"]
    POS_X=-MiObjPos["POS_X"]/16 if "POS_X" in MiObjPos.keys() else 0
    POS_Y=-MiObjPos["POS_Y"]/16 if "POS_Y" in MiObjPos.keys() else 0
    POS_Z=MiObjPos["POS_Z"]/16 if "POS_Z" in MiObjPos.keys() else 0
    bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, location=(0, 0, 0))
    
    #自义定中心(我好懒啊，原本的想法应该塞进自义定属性里，然后联动驱动器进行偏移)
    rot_point =timelinesJsonData["rot_point"] if timelinesJsonData["rot_point_custom"] else [ 0, -8, 0 ]
    #rot_point[x,z,y]
    bpy.context.object.location[0] -= rot_point[0]/16#x
    bpy.context.object.location[1] += rot_point[2]/16#y
    bpy.context.object.location[2] -= rot_point[1]/16#z
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    
    bpy.context.object.location=[POS_Y, POS_X, POS_Z]
    bpy.context.object.keyframe_insert(data_path="location", frame=0)
    
    SCA_X=MiObjPos["SCA_X"] if "SCA_X" in MiObjPos.keys() else 1
    SCA_Y=MiObjPos["SCA_Y"] if "SCA_Y" in MiObjPos.keys() else 1
    SCA_Z=MiObjPos["SCA_Z"] if "SCA_Z" in MiObjPos.keys() else 1
    
    bpy.context.object.scale = [SCA_Y,SCA_X,SCA_Z]
    '''
    mi的矩阵运算顺序是先缩放再旋转
    而bl的齐次坐标的顺序没法改，是先旋转再缩放，缩放会影响旋转
    所以先缩放应用再旋转
    '''

    #命名物体为id
    bpy.context.object.name = timelinesJsonData["id"]
    if timelinesJsonData['name']=='':
        id=timelinesJsonData['id']
        name=timelinesJsonData['name']
        NameDict[id]='方块'
    else:
        id=timelinesJsonData['id']
        name=timelinesJsonData['name']
        NameDict[id]=name

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
    if ParentId in bpy.context.collection.objects.keys():
        bpy.data.objects[id].parent = bpy.data.objects[ParentId]
    else:
        print('mi2bl:模型文件中存在无法识别的物体，请联系开发者')

def 缩放后才能旋转物体(id,MiObjectJson):
    pos=提取对应id的坐标(MiObjectJson)
    id=id
    #取消全选，上下文选择物体，应用缩放
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = bpy.data.objects[id]
    bpy.data.objects[id].select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    MiObjPos=pos[id]["0"]
    ROT_X=-radians(MiObjPos["ROT_X"]) if "ROT_X" in MiObjPos.keys() else 0
    ROT_Y=-radians(MiObjPos["ROT_Y"]) if "ROT_Y" in MiObjPos.keys() else 0
    ROT_Z=radians(MiObjPos["ROT_Z"]) if "ROT_Z" in MiObjPos.keys() else 0
    bpy.data.objects[id].rotation_euler = [ROT_Y,ROT_X,ROT_Z]
    

#创建物体
for timelinesData in MiObjectJson["timelines"]:
    if timelinesData["type"]=="folder":
        读取folder坐标并应用(timelinesData)
    if timelinesData["type"]=="cube":
        读取cube坐标并应用(timelinesData)

#绑定父级
for timelinesData in MiObjectJson["timelines"]:
    if timelinesData["type"] not in ("folder","cube"):
        continue
    if timelinesData["parent"]!="root":
        通过Id设Parent(timelinesData)

ParentTree=提取父级节点树(MiObjectJson)
#print(ParentTree)

def 检测物体是否存在(id):
    dict=[]
    for obj in bpy.context.scene.objects:
        dict.append(obj.name)
    if id in dict:
        return True
    else:
        return False

#开始旋转
dict=ParentTree['root']
def 判断键内有无子集(dict):
    for object in dict:
        print(object)
        if not 检测物体是否存在(object):
            continue
        global MiObjectJson
        缩放后才能旋转物体(object,MiObjectJson)
        if dict[object]!=None:
            判断键内有无子集(dict[object])

判断键内有无子集(dict)


    
#恢复命名
#for nnn123 in NameDict:
#    bpy.data.objects[nnn123].name=NameDict[nnn123]
    



#bpy.data.objects['123'].name='22'

#bpy.context.view_layer.objects.active 设置活动元素
#bpy.data.objects['Plane.001'].select_set(True)
