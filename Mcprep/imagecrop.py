from . PIL_library64 import Image
#from . PIL_library64 import Image
import sys

def cut_image(image,x,y):
    #x指横上切的刀数
    width, height = image.size
    item_width = int(width / x)
    item_height = int(width / y)
    box_list = []
    # (left, upper, right, lower)
    for i in range(0,y):
        for j in range(0,x):
            box = (j*item_width,i*item_height,(j+1)*item_width,(i+1)*item_height)
            box_list.append(box)
    image_list = [image.crop(box) for box in box_list]
    return image_list

#保存
def save_images(image_list):
    from os.path import exists
    from os import makedirs
    import bpy
    temppath=bpy.app.tempdir
    # temppath="E:\\暂存\\a1\\"
    print(temppath)
    if not exists(temppath+"mi2bl"): #判断文件夹存在
        makedirs(temppath+"mi2bl")#创建文件夹
    index = 1
    file_list=[]
    for image in image_list:
        image.save(temppath+"mi2bl\\"+str(index) + '.png', 'PNG')
        file_list.append(temppath+"mi2bl\\"+str(index) + '.png')
        index += 1
    return file_list
    
#主函数-分割图片，存储到blender的项目缓存文件夹中
def image_crop(file_path, x, y):
    #file_path = r"E:\暂存\a1\Untitled.png"  #图片保存的地址
    image = Image.open(file_path)
    #image.show()
    image_list = cut_image(image,x,y)
    file_list=save_images(image_list)
    return file_list

if __name__ == '__main__':
    file_path = r"E:\暂存\a1\Untitled.png"
    image_crop(file_path, 2, 2)