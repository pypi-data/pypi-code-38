from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageEnhance
import math


def is_in_range(src, target, offset):
    if src in range(target - offset, target + offset):
        return True
    else:
        return False


def print_pixel_value(img, x, y):
    no_alpha_size = 3
    result = img.getpixel((x, y))
    r = result[0]
    g = result[1]
    b = result[2]
    alpha = None
    if len(result) > no_alpha_size:
        alpha = result(3)

    info = 'pixel:({},{}), r:{}, g:{}, b:{}, alpha:{}'.format(x, y, r, g, b, alpha)
    print(info)


def print_image_pixel(src, x, y):
    img = Image.open(src)
    print_pixel_value(img, x, y)
    img.close()


def replace_pixel(src, dst, ori_pixel, dst_pixel, offset=48, show_only=False, excludes=None):
    no_alpha_size = 3

    ori_r = ori_pixel[0]
    ori_g = ori_pixel[1]
    ori_b = ori_pixel[2]
    ori_a = None
    if len(ori_pixel) > no_alpha_size:
        ori_a = ori_pixel[3]

    dst_r = dst_pixel[0]
    dst_g = dst_pixel[1]
    dst_b = dst_pixel[2]
    dst_a = None
    if len(dst_pixel) > no_alpha_size:
        dst_a = dst_pixel[3]
    else:
        if ori_a:
            dst_a = ori_a

    try:
        img = Image.open(src)
        pixel_size = len(img.getpixel((0, 0)))
        has_alpha = True
        if pixel_size == no_alpha_size:
            has_alpha = False

        for i in range(img.width):
            for j in range(img.height):
                to_exclude = False
                if excludes:
                    for item in excludes:
                        left = item[0]
                        right = item[0] + item[2]
                        top = item[1]
                        bottom = item[1] + item[3]
                        if left <= i <= right and top <= j <= bottom:
                            to_exclude = True
                            break

                    if to_exclude:
                        continue

                alpha = 255
                if has_alpha:
                    r, g, b, alpha = img.getpixel((i, j))
                else:
                    r, g, b = img.getpixel((i, j))

                target_a = alpha
                if dst_a:
                    target_a = dst_a

                if is_in_range(r, ori_r, offset) and is_in_range(g, ori_g, offset) and is_in_range(b, ori_b, offset):
                    if ori_a and is_in_range(alpha, ori_a, offset):
                        img.putpixel((i, j), (dst_r, dst_g, dst_b, target_a))
                    else:
                        img.putpixel((i, j), (dst_r, dst_g, dst_b, target_a))

        if show_only:
            img.show()
        else:
            img.save(dst)
    finally:
        img.close()


def crop_image(src, dst, x, y, w, h, show_only=False):
    img = Image.open(src)
    r = x + w
    b = y + h
    cropped_img = img.crop((x, y, r, b))
    if show_only:
        cropped_img.show()
    else:
        cropped_img.save(dst)

    cropped_img.close()
    img.close()


# 默认为识别中文，如果要识别英文，请将第二个参数传递None
def get_text(src, lang='chi_sim'):
    import pytesseract

    # 配置命令路径
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR/tesseract.exe'

    with Image.open(src) as f:
        text = pytesseract.image_to_string(f, lang=lang)
        return text


def generate_text_watermark(img, text, out_file="test4.jpg", angle=23, opacity=0.50):
    """
    添加一个文字水印，做成透明水印的模样，png图层合并
    http://www.pythoncentral.io/watermark-images-python-2x/
    Pillow安装：pip install Pillow
    """
    watermark = Image.new('RGBA', img.size, (255, 255, 255))  # 我这里有一层白色的膜，去掉(255,255,255) 这个参数就好了

    FONT = "msyh.ttf"
    size = 2

    n_font = ImageFont.truetype(FONT, size)  # 得到字体
    n_width, n_height = n_font.getsize(text)
    text_box = min(watermark.size[0], watermark.size[1])
    while (n_width + n_height < text_box):
        size += 2
        n_font = ImageFont.truetype(FONT, size=size)
        n_width, n_height = n_font.getsize(text)  # 文字逐渐放大，但是要小于图片的宽高最小值

    text_width = (watermark.size[0] - n_width) / 2
    text_height = (watermark.size[1] - n_height) / 2
    # watermark = watermark.resize((text_width,text_height), Image.ANTIALIAS)
    draw = ImageDraw.Draw(watermark, 'RGBA')  # 在水印层加画笔
    draw.text((text_width, text_height),
              text, font=n_font, fill="#21ACDA")
    watermark = watermark.rotate(angle, Image.BICUBIC)
    alpha = watermark.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    watermark.putalpha(alpha)
    Image.composite(watermark, img, watermark).save(out_file, 'JPEG')
    print('文字水印成功')


# image: 图片
# text：要添加的文本
# font：字体
def add_text_to_image(img, xy, size, text, font_size, fill, outline=None, angle=23, text_lines=1):
    font_name = 'SIMYOU.TTF'
    font = ImageFont.truetype(font_name, font_size)  # 得到字体

    rgba_image = img.convert('RGBA')
    text_overlay = Image.new('RGBA', rgba_image.size, (255, 255, 255, 0))
    # (255,255,255,0):第四个是图片的透明度,值越大,越浅
    image_draw = ImageDraw.Draw(text_overlay)

    # 设置文本文字位置
    line_cnt = math.ceil(len(text) / text_lines)
    if text_lines > 1:
        text_width, text_height = font.getsize(text[:line_cnt])
        space = round(text_height / 2)
    else:
        text_width, text_height = font.getsize(text)
        space = 0


    x, y = xy
    w, h = size
    # 设置文本颜色和透明度
    if not outline:
        outline = fill
    line_width = 4
    # image_draw.polygon([(0, 0), (w-1, 0), (w-1, h-1), (0, h-1)], outline=outline)
    image_draw.rectangle((x, y, x+w-line_width, y+h-line_width), outline=outline)

    x_offset = x + round((w - text_width) / 2)
    text_height_range = round((text_lines - 1) * space) + text_height * text_lines
    y_offset = y + round((h - text_height_range)/2)
    for index in range(text_lines):
        text_xy = x_offset, y_offset + index * (text_height + space)
        start = index * line_cnt
        end = (index+1) * line_cnt
        if end > len(text):
            end = len(text)
        image_draw.text(text_xy, text[start:end], font=font, fill=fill)
    del image_draw

    # (87,250,255,360)第四个是文字的透明度,值越大,越深

    if angle:
        text_overlay = text_overlay.rotate(angle, Image.BICUBIC)

    image_with_text = Image.alpha_composite(rgba_image, text_overlay)
    rgba_image.close()

    return image_with_text


# 等比例压缩图片
def resize_image(src_img, ratio, dst_img=None):
    """
    根据压缩比例压缩图片
    """
    if not 0 < ratio <= 1.0:
        raise Exception('the ratio {} is invalid!'.format(ratio))

    if not dst_img:
        dst_img = src_img

    with Image.open(src_img) as img:
        w, h = img.size
        dst_w = round(w*ratio)
        dst_h = round(h*ratio)
        img.resize((dst_w, dst_h), Image.ANTIALIAS).save(dst_img)

    """
   Image.ANTIALIAS还有如下值： 
   NEAREST: use nearest neighbour 
   BILINEAR: linear interpolation in a 2x2 environment 
   BICUBIC:cubic spline interpolation in a 4x4 environment 
   ANTIALIAS:best down-sizing filter
   """


def join_image(img_list, max_row, max_col, dst_path, dst_unit_width=None, dst_unit_height=None):
    max_num = max_row * max_col
    if not dst_unit_width or not dst_unit_height:
        with Image.open(img_list[0]) as first_img:
            first_w, first_h = first_img.size

        if not dst_unit_width:
            dst_unit_width = first_w

        if not dst_unit_height:
            dst_unit_height = first_h

    dst_img = Image.new('RGBA', (dst_unit_width * max_col, dst_unit_height * max_row))
    num = 0
    for i in range(max_row):
        for j in range(max_col):
            with Image.open(img_list[num]) as img_unit:
                width, height = img_unit.size

                if width != dst_unit_width or height != dst_unit_height:
                    tmp_img = img_unit.resize((dst_unit_width, dst_unit_height))
                else:
                    tmp_img = img_unit

                loc = j * dst_unit_width, i * dst_unit_height

                # print("{}'s location {}.".format(img_list[num], loc))
                dst_img.paste(tmp_img, loc)
                num += 1
                if tmp_img != img_unit:
                    tmp_img.close()

                if num >= len(img_list):
                    break

        if num >= len(img_list) or num >= max_num:
            break

    # print(dst_img.size)
    dst_img.save(dst_path)
    dst_img.close()
