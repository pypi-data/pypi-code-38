from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

def show_image(path : str):
    """展示图片，输入为图片路径
       Parameters
       ----------
       path: string
           image path

       Example
       -------
       img_path = "../data/raw/gamble/pictures/_更新页面_xdqp__仙豆棋牌__0.png"
       image = show_image(img_path)
    """
    image = Image.open(path, mode='r')
    image = image.convert('RGB')
    return image

def draw_rect(image : Image.Image, location_box : list, color : str):
    """画方框
       Parameters
       ----------
       image: string
           image path
       location_box: list
           [x_min, y_min, x_max, y_max]

       Example
       -------
       img_path = "../data/raw/gamble/pictures/_更新页面_xdqp__仙豆棋牌__0.png"
       image = show_image(img_path)
       location_box = [50, 50, 100, 100]
       image = draw_rect(image, location_box, 'red')
    """
    draw = ImageDraw.Draw(image)
    draw.rectangle(xy = location_box, outline = color)
    draw.rectangle(xy = [l+1 for l in location_box], outline = color)
    return image

def draw_text(image : Image.Image, xy : list, color : str, text : str):
    """画文字
       Parameters
       ----------
       image: string
           image path

       Example
       -------
       img_path = "../data/raw/gamble/pictures/_更新页面_xdqp__仙豆棋牌__0.png"
       image = show_image(img_path)
       location_box = [50, 50, 100, 100]
       image = draw_rect(image, location_box, 'red')
    """
    font = ImageFont.truetype("../fonts/calibri/Calibri.ttf", 15)
    draw = ImageDraw.Draw(image)
    text_size = font.getsize(text)
    location_text = [xy[0] + 2., xy[1] - text_size[1]]
    location_textbox = [xy[0], xy[1] - text_size[1], xy[0] + text_size[0] + 4., xy[1]]
    draw.rectangle(xy = location_textbox, fill = color)
    draw.text(xy = location_text, text = text, fill='white', font=font)
    return image
