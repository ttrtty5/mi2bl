from . PIL_library64 import Image

if __name__ == '__main__':
    file = r"2.png"
    SkinConverting(file)


def SkinConverting(file):
    img = Image.open(file)
    if img.size[0] == img.size[1]:
        pass
    else:
        img_size = img.size
        基础长度 = img_size[0]//16
        手臂长 = 基础长度 * 3

        img_new = Image.new(size=(img_size[0],img_size[0]),mode='RGBA')
        原图 = img.crop((0,0,img_size[0],img_size[1])) #crop((x0,y0,x1,y1))
        img_new.paste(img,(0,0))
        
        # 手翻转粘贴
        arm1_img = img.crop((0,基础长度 * 5,基础长度 * 3,img_size[1]))
        img_new.paste(arm1_img.transpose(Image.FLIP_LEFT_RIGHT), (基础长度*4,基础长度*13))
        
        arm2_img = img.crop((基础长度,基础长度 * 4,基础长度 * 2,基础长度*5))
        img_new.paste(arm2_img.transpose(Image.FLIP_LEFT_RIGHT), (基础长度*5,基础长度*12))
        
        arm3_img = img.crop((基础长度 * 2,基础长度 * 4,基础长度 * 3,基础长度*5))
        img_new.paste(arm3_img.transpose(Image.FLIP_LEFT_RIGHT), (基础长度*6,基础长度*12))
        
        arm4_img = img.crop((基础长度 * 3,基础长度 * 5,基础长度 * 4,img_size[1]))
        img_new.paste(arm4_img.transpose(Image.FLIP_LEFT_RIGHT), (基础长度*7,基础长度*13))
        
        # 腿翻转粘贴
        leg1_img = img.crop((基础长度 * 10,基础长度 * 5,基础长度 * 13,img_size[1]))
        img_new.paste(leg1_img.transpose(Image.FLIP_LEFT_RIGHT), (基础长度*8,基础长度*13))
        
        leg2_img = img.crop((基础长度 * 11,基础长度 * 4,基础长度 * 12,基础长度 * 5))
        img_new.paste(leg2_img.transpose(Image.FLIP_LEFT_RIGHT), (基础长度*9,基础长度*12))
        
        leg3_img = img.crop((基础长度 * 12,基础长度 * 4,基础长度 * 13,基础长度 * 5))
        img_new.paste(leg3_img.transpose(Image.FLIP_LEFT_RIGHT), (基础长度*10,基础长度*12))
        
        leg4_img = img.crop((基础长度 * 13,基础长度 * 5,基础长度 * 14,基础长度 * 9))
        img_new.paste(leg4_img.transpose(Image.FLIP_LEFT_RIGHT), (基础长度*11,基础长度*13))
        
        img_new.save(file.replace('.png','_18.png'))
