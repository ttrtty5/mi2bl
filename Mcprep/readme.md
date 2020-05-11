MI2BL

本插件内使用以下框架的代码
Mcprep -用于生成立体网格item
PIL -用于生成item预览


bl_idname = 'mi2bl.xxx'

todo路线图 某人脑袋比较容易秀逗，所以写个路线图

//已完成
general_icon_from_prevlist → build_state(按钮触发状态) → 运行build_item → 赋值给Mi2bl_do_1.outside_item(防止被刷新掉) → 回到general_icon_from_prevlist中将Mi2bl_do_1.outside_item传递给预览枚举的items


//已完成
所以切换大图片列表的预览是在image_set中 - 根据Mi2bl_do_1.image_list[value][1]的所选图片状态 - 来把对应preview_collections['info'][名字]对应图片的icon对象赋值给Mi2bl_do_1.outside_item

//已完成
拿spawn_item_from_filepath改了改，改成了spawn_item_from_pixels,用像素生成item并校正uv

//手贱覆盖了cube和mbmodel的路线图
大致是生成物体-移动缩放，按照父级传递给子级缩放，然后应用缩放，然后绑定父级，然后旋转，不想重写一遍了，呜呜呜

//mbmodel block
'from'是原点偏移点,然后长宽高lwh为shape['to'][2]-shape['from'][2]
其实直接就得到了
//mb block 材质部分
为了实现材质继承，所以在递归的时候得传个材质参数进去，首先
材质名字写之前递归里传递贴图名字,然后子级部件里要是有百分比或贴图名字就复制父级修改参数，没有就继承材质
通过贴图名字还获取材质

//mbmodel plane
因为不用算方块的uv的lwh，简单的一批，所以我先做这个了

//从parts中遍历
生成part
如果parts有parts键，就递归代入

### 已知bug ###
1.多item图 列表中有两张图片时，删掉第一张，无法自动弹出第二张，并会在报错，大概意思为对应索引的枚举不存在，不知道怎么修(因为不影响继续使用，就懒得修了)

2.spawn_item_from_pixels效率问题:当加载8*8item的1024*1024尺寸的图时，生成item需将近两秒
读取alpha通道问题能通过pil库提升速度(懒得)
像上面例子的图片，修改uv的时候会遍历128*128*4的数组，所以也很慢，看以后能不能通过c来重写(当然是看有没有其他大佬来写了)

3.生成item后会有F9的操作符弹框(无法修改，因为效率太低了)，不知道怎么隐藏

4.父级有缩放动画，子级有旋转动画时的剪切效应

5.材质的混合百分比的继承问题