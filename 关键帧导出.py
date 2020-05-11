import bpy
import math
import json
#访问物体坐标数据
wuti=bpy.context.active_object.location
wuti1=bpy.data.objects["Cube"].rotation_euler.x
bpy.context.scene.frame_current = 1
keyframes=[]
keymun = bpy.data.scenes["Scene"].frame_end-bpy.data.scenes["Scene"].frame_start-1

#保存到文件
with open("E:\暂存\data.miframes","w+")as f:
    time2=bpy.data.scenes["Scene"].frame_end-2
    for time1 in range(bpy.data.scenes["Scene"].frame_end,bpy.data.scenes["Scene"].frame_start,-1):
        #bpy.context.scene.frame_current = time1
        bpy.context.scene.frame_set(time1)
        mipos={}
        poslist=["POS_X","POS_Y","POS_Z","ROT_X","ROT_Y","ROT_Z"]
        posvalues=[round(bpy.context.active_object.location.x,5),
        round(bpy.context.active_object.location.y,5),
        round(bpy.context.active_object.location.z*10,5),
        round(math.degrees(bpy.data.objects["Cube"].rotation_euler.x),5),
        round(math.degrees(bpy.data.objects["Cube"].rotation_euler.y),4),
        round(math.degrees(bpy.data.objects["Cube"].rotation_euler.z),5)]
        
        bpnum=0
        for bppos in posvalues:
            if bppos!=0:
                mipos[poslist[bpnum]]=bppos
            bpnum+=1
        
        keyframe={"position": time2,"values":mipos}
        keyframes.append(keyframe)
        time2-=1
    
    mjson={"format": 31,
    "created_in": "1.2.4",
    'is_model': False,
    "tempo": 24,
    "length": (keymun),
    "keyframes":keyframes,
    "templates": [
    ],
    "timelines": [
    ],
    "resources": [
    ]}
    mikey= json.dumps(mjson, indent='	', ensure_ascii=False)
    f.write(mikey)

