import bpy

def get_pixel_to_image(img):
    img_sources_pixel=img.pixels
    img_sources_size=img.size
    num_of_divisions=(2,2)#分割次数
    tile_x=int(img_sources_size[0]/num_of_divisions[0])
    tile_y=int(img_sources_size[1]/num_of_divisions[1])
    pixel=[]
    for y in range(0,tile_y):
        for x in range(0,tile_x):
            pixel_pos=(y*img_sources_size[1]+x)*4
            pixel.extend(img_sources_pixel[pixel_pos:pixel_pos+4])
    out_img=bpy.data.images.new(name="Untitled",
        width=tile_x, 
        height=tile_y,  
        alpha=True)
    out_img.pixels=pixel
    return out_img

def get_tile_pixels(tile_xy,width,img_sources_pixel,tile_pos):
    #tile长宽，图片宽度，图片像素，tile坐标
    #通过tile所在坐标获取其alpha像素
    pixel=[]
    for y in range(tile_xy[1]):
        y=tile_xy[1]*tile_pos[1]+y#y所在层数
        pixel_pos=(y*width+tile_xy[0]*tile_pos[0])*4
        #像素y层层数 * 图片宽度 + tile的x所在位置 * tile宽度
        pixel.extend(img_sources_pixel[pixel_pos+3:pixel_pos+tile_xy[0]*4+3:4])
        #逐行读取
    return pixel

def get_tile_pixels1(tile_xy,width,img_sources_pixel,tile_pos):
    #通过tile所在坐标获取其像素
    pixel=[]
    for y in range(0,tile_xy[1]):
        y=tile_xy[1]*tile_pos[1]+y#y所在层数
        pixel_pos=(y*width+tile_xy[0]*tile_pos[0])*4
        #像素y层层数 * 图片宽度 + tile的x所在位置 * tile宽度
        pixel.extend(img_sources_pixel[pixel_pos+3:pixel_pos+tile_xy[0]+3:4])
        #逐行读取
    return pixel

def get_pixel_generate_allimg(img,num_of_divisions):
    #通过图片像素来生成tile
    img_sources_pixel=img.pixels
    img_sources_size=img.size
    #num_of_divisions=(2,2)#分割次数
    tile_xy=(int(img_sources_size[0] / num_of_divisions[0]),
        int(img_sources_size[1] / num_of_divisions[1]))
    #tile的xy长度
    width=img_sources_size[1]
    for y in range(0,num_of_divisions[1]):
        for x in range(0,num_of_divisions[0]):
            tile_pos=(x,y)#tile位置
            print(tile_pos)
            pixel=get_tile_pixels(tile_xy,width,img_sources_pixel,tile_pos)

            out_img=bpy.data.images.new(name=img.name+"_"+str(x)+"-"+str(y),
                width=tile_xy[0], 
                height=tile_xy[1],  
                alpha=True)
            out_img.pixels=pixel

# img=bpy.data.images["Untitled"]
# num_of_divisions=(8,8)
# get_pixel_generate_allimg(img,num_of_divisions)

# img_sources_pixel=img.pixels
# pixel=get_tile_pixels((128,128),1024,img_sources_pixel,(1,1))
# print(pixel)
# out_img=bpy.data.images.new(name='0111',
#    width=128, 
#    height=128,  
#    alpha=True)
# out_img.pixels=pixel

def item_uv_correction(obj,x_num, y_num, to_pos):
    #校正item在图片中的uv
    scale_w=1/x_num
    scale_h=1/y_num
    uv = bpy.context.object.data.uv_layers.active#正在使用的uv
    #face=bpy.context.object.data.polygons[0]
    co_x_offset = scale_w*to_pos[0]
    co_y_offset = scale_h*to_pos[1]
    #先向原点缩放，再偏移
    for face in bpy.context.object.data.polygons:
        for i in face.loop_indices:
            l = obj.data.loops[i]
            uv.data[l.index].uv[0] = uv.data[l.index].uv[0] * scale_w + co_x_offset
            uv.data[l.index].uv[1] = uv.data[l.index].uv[1] * scale_h + co_y_offset



def get_pixel_from_pos(img,uv_pos,uv_wh):
    #图片，uv起始点，uv宽高，返回对应区域内的像素数组
    img_pix = list(img.pixels)
    piexls = []
    size=img.size
    from_pos_y=img.size[1] - uv_pos[1] - uv_wh[1]
    for num in range(uv_wh[1]):
        piexls.extend(img_pix[
            ((num+from_pos_y)*size[0]+uv_pos[0])*4+3:
            ((num+from_pos_y)*size[0]+uv_pos[0]+uv_wh[0])*4+3:4])
    return piexls

def plane_uv_from_uvpos(img,uv_pos,uv_wh):
    #图片，点坐标，高宽 , 校正plane在图片中的uv
    scale_w=uv_wh[0]/img.size[0]#单像素长宽
    scale_h=uv_wh[1]/img.size[1]
    from_pos_y=img.size[1] - uv_pos[1] - uv_wh[1] #y层
    uv = bpy.context.object.data.uv_layers.active #正在使用的uv
    print("pos: " + str(from_pos_y),str(uv_wh))
    #face=bpy.context.object.data.polygons[0]
    co_x_offset = 1/img.size[0] * uv_pos[0]
    co_y_offset = 1/img.size[1] * from_pos_y
    obj = bpy.context.object
    #先向原点缩放，再偏移
    for face in bpy.context.object.data.polygons:
        for i in face.loop_indices:
            l = obj.data.loops[i]
            uv.data[l.index].uv[0] = uv.data[l.index].uv[0] * scale_w + co_x_offset
            uv.data[l.index].uv[1] = uv.data[l.index].uv[1] * scale_h + co_y_offset

def hex_to_tuple(text):
    #将hex转tuple
    r, g, b=text[1:3], text[3:5], text[5:7]
    rgba=(int(r,16)/255, int(g,16)/255, int(b,16)/255, 1)
    return rgba

def default_mat_mbcube(texture,folder_path):
    #,给mb模型初始化材质
    mat = bpy.data.materials.new(texture)
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
    emiss = nodes.new(type="ShaderNodeEmission")
    dif_mix_emiss = nodes.new(type="ShaderNodeMixShader")
    mix_alpha = nodes.new(type="ShaderNodeMixShader")
    alpha_node = nodes.new(type="ShaderNodeBsdfTransparent")

    
    #命名部分
    mulrgb.name='mulrgb'
    mixrgb.name='mixrgb'
    dif_mix_emiss.name='dif_mix_emiss'
    mix_alpha.name='mix_alpha'
    

    tex_node = nodes.new(type='ShaderNodeTexImage')
    tex_node.name = 'tex_node'
    if texture not in bpy.data.images:
        bpy.data.images.load(folder_path +'\\' + texture , check_existing=True)
    tex_node.image = bpy.data.images[texture]
    tex_node.interpolation = 'Closest'
    tex_node.location[0] -= 700
    links.new(tex_node.outputs[0],mulrgb.inputs[1])
    

    #设置参数
    mulrgb.inputs[0].default_value = 1
    mulrgb.inputs[2].default_value = (1, 1, 1, 1)#TODO 参数没调
    mixrgb.inputs[0].default_value = 0
    mixrgb.inputs[1].default_value = (1, 1, 1, 1)
    mixrgb.inputs[2].default_value = (0, 0, 0, 1)
    dif_mix_emiss.inputs[0].default_value = 0
    mix_alpha.inputs[0].default_value = 0
    
    #link
    links.new(mulrgb.outputs[0],mixrgb.inputs[1])
    links.new(mixrgb.outputs[0],diffuse_node.inputs[0])
    links.new(diffuse_node.outputs[0],dif_mix_emiss.inputs[1])
    links.new(emiss.outputs[0],dif_mix_emiss.inputs[2])
    links.new(mixrgb.outputs[0],emiss.inputs[0])
    links.new(dif_mix_emiss.outputs[0],mix_alpha.inputs[1])
    links.new(alpha_node.outputs[0],mix_alpha.inputs[2])
    links.new(mix_alpha.outputs[0],output_node.inputs[0])

    #整理节点
    output_node.location[0] += 600
    emiss.location[1] -= 150
    dif_mix_emiss.location[0] += 200
    mix_alpha.location[0] += 400
    alpha_node.location[0] += 200
    alpha_node.location[1] -= 150
    mixrgb.location[0] -= 200
    mulrgb.location[0] -= 400
    #bpy.context.object.data.materials.append(mat)



def mb_mat_uvpos(mat,shape):
    '''修改mb模型的材质参数'''
    tree=mat.node_tree
    tex_node=tree.nodes['tex_node']
    mulrgb=tree.nodes['mulrgb']
    mixrgb=tree.nodes['mixrgb']
    dif_mix_emiss=tree.nodes['dif_mix_emiss']
    mix_alpha=tree.nodes['mix_alpha']
    
    if 'texture' in shape:
        tex_node.image=bpy.data.images[shape['texture']]
    
    if 'color_blend' in shape:
        mulrgb.inputs[2].default_value=hex_to_tuple(shape['color_blend'])
    
    if 'color_mix' in shape:
        mixrgb.inputs[2].default_value=hex_to_tuple(shape['color_mix'])

    if 'color_alpha' in shape:
        mix_alpha.inputs[0].default_value+=shape['color_alpha']

    if 'color_brightness' in shape:
        dif_mix_emiss.inputs[0].default_value+=shape['color_brightness']

def mb_cube_uv(uv_lwh, uvpos, size):
    #uv长宽高,uv定位点位置,调整cube的uv
    face_front = bpy.context.object.data.polygons[0]
    face_right = bpy.context.object.data.polygons[1]
    face_back = bpy.context.object.data.polygons[2]
    face_left = bpy.context.object.data.polygons[3]
    face_down = bpy.context.object.data.polygons[4]
    face_up = bpy.context.object.data.polygons[5]

    #uv单位
    pixel_unit_x = 1/size[0]
    pixel_unit_y = 1/size[1]
    pos_offset_y = size[1] - uvpos[1] - uv_lwh[2]#定点左下角
    obj = bpy.context.object
    uv = bpy.context.object.data.uv_layers.active #正在使用的uv

    #front
    bpy.context.object.data.uv_layers.active.data[0].uv=[1,0]
    bpy.context.object.data.uv_layers.active.data[1].uv=[1,1]
    bpy.context.object.data.uv_layers.active.data[2].uv=[0,1]
    bpy.context.object.data.uv_layers.active.data[3].uv=[0,0]
    for i in face_front.loop_indices:
        l = obj.data.loops[i]
        uv.data[l.index].uv[0] = uv.data[l.index].uv[0] / size[0] * uv_lwh[1] + pixel_unit_x*uvpos[0]
        uv.data[l.index].uv[1] = uv.data[l.index].uv[1]/ size[1] * uv_lwh[2] + pixel_unit_y*pos_offset_y

    #right
    bpy.context.object.data.uv_layers.active.data[4].uv=[1,0]
    bpy.context.object.data.uv_layers.active.data[5].uv=[1,1]
    bpy.context.object.data.uv_layers.active.data[6].uv=[0,1]
    bpy.context.object.data.uv_layers.active.data[7].uv=[0,0]
    for i in face_right.loop_indices:
        l = obj.data.loops[i]
        uv.data[l.index].uv[0] = uv.data[l.index].uv[0] / size[0] * uv_lwh[0] + pixel_unit_x*(uvpos[0] - uv_lwh[0])
        uv.data[l.index].uv[1] = uv.data[l.index].uv[1]/ size[1] * uv_lwh[2] + pixel_unit_y*pos_offset_y
    #back
    bpy.context.object.data.uv_layers.active.data[8].uv=[1,0]
    bpy.context.object.data.uv_layers.active.data[9].uv=[1,1]
    bpy.context.object.data.uv_layers.active.data[10].uv=[0,1]
    bpy.context.object.data.uv_layers.active.data[11].uv=[0,0]
    for i in face_back.loop_indices:
        l = obj.data.loops[i]
        uv.data[l.index].uv[0] = uv.data[l.index].uv[0] / size[0] * uv_lwh[1] + pixel_unit_x*(uvpos[0]+uv_lwh[0]+uv_lwh[1])
        uv.data[l.index].uv[1] = uv.data[l.index].uv[1]/ size[1] * uv_lwh[2] + pixel_unit_y*pos_offset_y
    #left
    bpy.context.object.data.uv_layers.active.data[12].uv=[1,0]
    bpy.context.object.data.uv_layers.active.data[13].uv=[1,1]
    bpy.context.object.data.uv_layers.active.data[14].uv=[0,1]
    bpy.context.object.data.uv_layers.active.data[15].uv=[0,0]
    for i in face_left.loop_indices:
        l = obj.data.loops[i]
        uv.data[l.index].uv[0] = uv.data[l.index].uv[0] / size[0] * uv_lwh[0] + pixel_unit_x*(uvpos[0]+uv_lwh[1])
        uv.data[l.index].uv[1] = uv.data[l.index].uv[1]/ size[1] * uv_lwh[2] + pixel_unit_y*pos_offset_y