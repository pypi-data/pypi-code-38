from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import textwrap
import uuid,os
import math
from w3lib.html import remove_tags
from w3lib.html import strip_html5_whitespace
from w3lib.html import remove_tags_with_content


def add_logo(image_path, logo_path, tmp_path,output=None, pos="TR"):
    if output == None:
        output = os.path.join(tmp_path, uuid.uuid4().hex + "_logo_text.jpg")
    img = Image.open(image_path)
    image_size = img.size
    img_logo = Image.open(logo_path)
    img_logo_size=img_logo.size
    img.paste(img_logo, (image_size[0]-img_logo_size[0], 0),img_logo)
    img.save(output)
    img.close()
    img_logo.close()
    return output

def write_text_on_logo(image_path, tmp_path, arr_letter, arr_top_index,font_file,output=None,font_size=50,text_spacing=" "):
    if output == None:
        output = os.path.join(tmp_path, uuid.uuid4().hex + "_logo_text.jpg")
    img = Image.open(image_path)
    image_size = img.size
    img_box = Image.new('RGBA', (image_size[0], image_size[1]), (0, 0, 0, 130))
    white = 'rgb(255, 255, 255)'
    yellow= 'rgb(255,255,0)'
    beige='rgb(245,245,220)'
    red = 'rgb(255,0,0)'
    blue='rgb(0,0,255)'
    green = 'rgb(0,255,0)'
    margin = 20
    logo_w=80
    draw = ImageDraw.Draw(img_box)
    font = ImageFont.truetype(font_file, size=font_size, encoding="unic")
    line_height = font.getsize('hg')[1]
    start_x=margin
    start_y =margin
    x=start_x
    y=start_y
    for letter in arr_letter:
        color=white
        if(letter.value == arr_top_index[0]):
            color=red
        if (letter.value == arr_top_index[1]):
            color = yellow
        if (letter.value == arr_top_index[2]):
            color = green
        if(letter.value == 1):
            color = white
        letter_x=font.getsize(letter.text+text_spacing)[0]
        if x+letter_x>image_size[0]-margin-logo_w:
            x=start_x
            y+=line_height
        draw.text((x,y), letter.text,fill=color, font=font)
        x+=letter_x
    img.paste(img_box, (0, 0),img_box)
    img.save(output)
    img.close()
    img_box.close()
    return output




def content(image_path,text,font_file,tmp_path,wrap_text_len=70,font_size=33):
    output = os.path.join(tmp_path, uuid.uuid4().hex + "_draw_text.jpg")
    if text ==None or text =="":
        return image_path
    img = Image.open(image_path)
    image_size = img.size
    img_box = Image.new('RGBA', (image_size[0], 250), (0, 0, 0, 130))
    draw = ImageDraw.Draw(img_box)
    font = ImageFont.truetype(font_file, size=font_size, encoding="unic")
    lines = textwrap.wrap(text, wrap_text_len)
    line_height = font.getsize('hg')[1]
    color = 'rgb(255, 255, 255)'
    y = 20
    x = (image_size[0] - font.getsize(lines[0])[0]) / 2
    for line in lines:
        draw.text((x, y), line, fill=color, font=font)
        # update the y position so that we can use it for next line
        y = y + line_height
    img.paste(img_box, (0, image_size[1] - 300), img_box)
    img.save(output)
    img.close()
    img_box.close()
    return output

def balance_image(arr_image,arr_text):
    if len(arr_image) < len(arr_text):
        step=1
        i=0
        while (len(arr_image) < len(arr_text)):
            if(step + i > len(arr_image)):
                i=0
                step +=1
            arr_image.insert(step+i,arr_image[i])
            i+=step+1
    if len(arr_text) < len(arr_image):
        d = len(arr_image) - len(arr_text)
        i=0
        while(i<d):
            arr_text.append("")
            i+=1
def filter_text(text):
        return strip_html5_whitespace((remove_tags(remove_tags_with_content(text, which_ones=('sup', 'script')))))

def nomalize_text(arr_text,max_text_read):
        i=0
        while(i<len(arr_text)):
            arr_text[i] = filter_text(arr_text[i])
            if(arr_text[i]==None or arr_text[i]==""):
                arr_text.pop(i)
            else:
                if len(textwrap.wrap(arr_text[i], math.ceil(max_text_read*1.5)))>1 :
                    arr_tmp=textwrap.wrap(arr_text[i],math.ceil(max_text_read))
                    arr_text[i]=arr_tmp[0]
                    arr_tmp.pop(0)
                    arr_text.insert(i+1,"".join(arr_tmp))
                i+=1