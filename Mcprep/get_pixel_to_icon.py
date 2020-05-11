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
    scale_w=uv_wh[0]/img.size[0]
    scale_h=uv_wh[1]/img.size[1]
    from_pos_y=img.size[1] - uv_pos[1] - uv_wh[1]
    uv = bpy.context.object.data.uv_layers.active #正在使用的uv
    #face=bpy.context.object.data.polygons[0]
    co_x_offset = 1/img.size[0] * uv_wh[0]
    co_y_offset = 1/img.size[1] * from_pos_y
    obj = bpy.context.object
    #先向原点缩放，再偏移
    for face in bpy.context.object.data.polygons:
        for i in face.loop_indices:
            l = obj.data.loops[i]
            uv.data[l.index].uv[0] = uv.data[l.index].uv[0] * scale_w + co_x_offset
            uv.data[l.index].uv[1] = uv.data[l.index].uv[1] * scale_h + co_y_offset