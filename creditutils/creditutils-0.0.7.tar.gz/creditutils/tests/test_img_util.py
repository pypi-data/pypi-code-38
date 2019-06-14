from PIL import Image
import creditutils.img_util as img_util


def test_01():
    src_img_01 = r'E:\temp\image\z.jpg'
    dst_img_01 = r'E:\temp\image\z_01.png'

    x = 17
    y = 369
    w = 2169
    h = 3081
    show_only = True
    img_util.crop_image(src_img_01, dst_img_01, x, y, w, h, show_only)


def replace_pixel_test(src, dst, show_only=False):
    offset = 48
    ori_r = 208
    ori_g = 206
    ori_b = 192
    dst_r = 255
    dst_g = 255
    dst_b = 255

    exclude_rect_list = [
        [164, 185, 443, 761],
        [123, 365, 49, 67],
        [453, 503, 45, 77],
        [95, 831, 663, 115],
        [27, 863, 147, 83],
        [139, 427, 37, 77],
        [609, 339, 51, 153],
        [121, 819, 561, 67]
    ]

    img_util.replace_pixel(src, dst, (ori_r, ori_g, ori_b), (dst_r, dst_g, dst_b), offset=offset, show_only=show_only,
                           excludes=exclude_rect_list)


def test_02():
    src_img_01 = r'E:\temp\image\h.jpg'
    dst_img_01 = r'E:\temp\image\h_01.png'

    show_only = True
    replace_pixel_test(src_img_01, dst_img_01, show_only)


def test_03():
    src_img_01 = r'E:\temp\image\z.jpg'
    x = 1
    y = 1
    img_util.print_image_pixel(src_img_01, x, y)

    count = 100
    img = Image.open(src_img_01)
    w = img.width
    h = img.height
    index = 0
    is_end = False
    for i in range(w):
        for j in range(h):
            index += 1
            img_util.print_pixel_value(img, i, j)
            if index >= count:
                is_end = True
                break

        if is_end:
            break

    img.close()


def test_04():
    dst_path = r'E:\temp\image\wm_01.png'
    img_util.generate_text_watermark('我们', (100, 30), 12, dst_path)
    with Image.open(dst_path) as img:
        img.show()


# 增加水印
def test_05():
    src_path_format = r'E:\temp\image\watermark\授权许可_0{}.png'

    # text = '此件仅供微信支付使用，复印或挪作他用无效。'
    # dst_path_format = r'E:\temp\image\watermark\授权许可_0{}_01.png'
    # text = '此件仅供微信小程序使用，复印或挪作他用无效。'
    # dst_path_format = r'E:\temp\image\watermark\授权许可_0{}_02.png'
    text = '此件仅供钉钉使用，复印或挪作他用无效。'
    dst_path_format = r'E:\temp\image\watermark\target\授权许可_0{}_01.png'

    cnt = 7
    for index in range(1, cnt):
        src_path = src_path_format.format(index)
        dst_path = dst_path_format.format(index)
        with Image.open(src_path) as img:
            w = 600
            h = 200
            img_w, img_h = img.size
            x = round(img_w * 2 / 3)
            y = round(img_h / 3 + h / 2)
            font_size = 48
            fill = 'gray'
            outline = 'blue'
            result = img_util.add_text_to_image(img, (x, y), (w, h), text, font_size, fill, outline=outline, text_lines=2,
                                                angle=None)
            # result.show()
            result.save(dst_path)
            result.close()


# 缩放图片
def test_06():
    # src_path_format = r'D:\document_work\pycredit\天下信用事业部\公司拆分\微信支付\授权许可_微信支付\授权许可_0{}_02.png'
    # dst_path_format = r'D:\document_work\pycredit\天下信用事业部\公司拆分\微信支付\授权许可_微信支付\授权许可_0{}_03.png'

    src_path_format = r'D:\document_work\pycredit\天下信用事业部\公司拆分\微信支付\授权许可_微信小程序\授权许可_0{}_03.png'
    dst_path_format = r'D:\document_work\pycredit\天下信用事业部\公司拆分\微信支付\授权许可_微信小程序\target\授权许可_0{}_03.png'

    cnt = 7
    ratio = 0.5
    for index in range(1, cnt):
        src_path = src_path_format.format(index)
        dst_path = dst_path_format.format(index)
        img_util.resize_image(src_path, ratio, dst_path)


# 合并图片
def test_07():
    # src_path_format = r'D:\document_work\pycredit\天下信用事业部\公司拆分\微信支付\授权许可_微信支付\target\授权许可_0{}_03.png'
    # dst_path = r'D:\document_work\pycredit\天下信用事业部\公司拆分\微信支付\授权许可_微信支付\target\join_02.png'
    # dst_path_resize = r'D:\document_work\pycredit\天下信用事业部\公司拆分\微信支付\授权许可_微信支付\target\join_02_01.png'

    src_path_format = r'E:\temp\image\watermark\target\授权许可_0{}_01.png'
    dst_path = r'E:\temp\image\watermark\target\join_01.png'
    # dst_path_resize = r'E:\temp\image\watermark\target\join_02.png'
    dst_path_resize_format = r'E:\temp\image\watermark\target\join_02_0{}.png'

    cnt = 7
    img_list = []
    for index in range(1, cnt):
        src_path = src_path_format.format(index)
        img_list.append(src_path)

    ratio = 0.135*1.71

    # img_util.join_image(img_list, 3, 2, dst_path)
    # dst_path_resize = dst_path_resize_format.format()
    # img_util.resize_image(dst_path, ratio, dst_path_resize)

    col_cnt = 2
    for i in range(3):
        img_util.join_image(img_list[i*col_cnt:(i+1)*col_cnt], 1, col_cnt, dst_path)
        dst_path_resize = dst_path_resize_format.format(i+1)
        img_util.resize_image(dst_path, ratio, dst_path_resize)


# 缩放单张图片
def test_08():
    src_path = r'D:\document_work\pycredit\天下信用事业部\公司相关\钉钉首页\20181017_01.jpg'
    dst_path = r'D:\document_work\pycredit\天下信用事业部\公司相关\钉钉首页\20181017_01_01.png'
    ratio = 0.85
    img_util.resize_image(src_path, ratio, dst_path)


# 图像旋转
def test_09():
    src_path = r'D:\document_work\myplan\family\蜗牛\snail_02.png'
    dst_path = r'D:\document_work\myplan\family\蜗牛\snail_02_r90.png'

    # 读取图像
    with Image.open(src_path) as im:
        # 指定逆时针旋转的角度
        im_rotate = im.rotate(90)
        im_rotate.show()
        # im_rotate.save(dst_path)
        im_rotate.close()


# 图像反转
def test_10():
    src_path = r'D:\document_work\myplan\family\蜗牛\snail_01.png'
    dst_path = r'D:\document_work\myplan\family\蜗牛\snail_01_r.png'

    # 读取图像
    with Image.open(src_path) as im:
        # 左右翻转
        out = im.transpose(Image.FLIP_LEFT_RIGHT)
        # 上下翻转
        # out = im.transpose(Image.FLIP_TOP_BOTTOM)
        # 逆时针90度的旋转
        # out = im.transpose(Image.ROTATE_90)
        # 逆时针180度的旋转
        # out = im.transpose(Image.ROTATE_180)
        # 逆时针270度的旋转
        # out = im.transpose(Image.ROTATE_270)

        # out.show()
        out.save(dst_path)
        out.close()


# 垂直合并两张不一样大小图片
def test_11():
    # src_path_format = r'D:\document_work\pycredit\天下信用事业部\公司拆分\微信支付\授权许可_微信支付\target\授权许可_0{}_03.png'
    # dst_path = r'D:\document_work\pycredit\天下信用事业部\公司拆分\微信支付\授权许可_微信支付\target\join_02.png'
    # dst_path_resize = r'D:\document_work\pycredit\天下信用事业部\公司拆分\微信支付\授权许可_微信支付\target\join_02_01.png'

    src_path_format = r'E:\temp\image\watermark\target\授权许可_0{}_01.png'
    dst_path = r'E:\temp\image\watermark\target\join_01.png'
    # dst_path_resize = r'E:\temp\image\watermark\target\join_02.png'
    dst_path_resize_format = r'E:\temp\image\watermark\target\join_02_0{}.png'

    cnt = 7
    img_list = []
    for index in range(1, cnt):
        src_path = src_path_format.format(index)
        img_list.append(src_path)

    ratio = 0.135*1.71

    # img_util.join_image(img_list, 3, 2, dst_path)
    # dst_path_resize = dst_path_resize_format.format()
    # img_util.resize_image(dst_path, ratio, dst_path_resize)

    col_cnt = 2
    for i in range(3):
        img_util.join_image(img_list[i*col_cnt:(i+1)*col_cnt], 1, col_cnt, dst_path)
        dst_path_resize = dst_path_resize_format.format(i+1)
        img_util.resize_image(dst_path, ratio, dst_path_resize)


def main():
    # test_01()
    # test_02()
    # test_03()
    # test_04()
    # test_05()
    # test_06()
    # test_07()
    # test_08()
    test_09()
    # test_10()


if __name__ == '__main__':
    main()
    print('to the end!')
