from PIL import Image, ImageFont, ImageDraw, ImageOps

color_back = (255, 255, 255, 255)
color = (0, 255, 255, 255)
color2 = (255, 128, 255, 255)
width = 20
space = 2
font = ImageFont.load_default()


def draw_rotated_text(image, text, x, y):
    txt = Image.new('RGBA', (250, 50), (0, 0, 0, 0))
    d = ImageDraw.Draw(txt)
    d.text((0, 0), text, font=font, fill=(0, 0, 0, 192))
    txt = txt.rotate(90,  expand=1)
    px = x
    py = y
    sx = 50
    sy = 250
    image.paste(txt, (px, py, px + sx, py + sy), txt)


def build(values, caption, file, total_as_max=False, add_text='', values2=None, add_to_index=1):
    iwidth = len(values) * (width + space) + space
    iwidth = max(iwidth, 700)
    iheight = 500
    image = Image.new("RGBA", (iwidth, iheight), color_back)

    draw = ImageDraw.Draw(image)
    # draw.rectangle(((0, 00), (100, 100)), fill=color)
    if len(values) > 0:
        max_value = float(max(values))
        if values2:
            max_value += max(values2)

        x = space
        total = float(sum(values))
        for i, value in enumerate(values):
            print value, max_value, iheight, value / max_value * (iheight - 100)
            height = value / max_value * (iheight - 100)
            bottom = iheight - 20
            top = bottom - height
            draw.line((x, 50, x, iheight), fill=(0, 0, 0, 1))
            draw.text((x + 5, bottom), str(i + add_to_index), fill='black', font=font)

            draw.rectangle(((x, bottom), (x + width, top)), fill=color)
            if(values2):
                value2 = values2[i]
                height2 = value2 / max_value * (iheight - 100)
                bottom2 = top
                top2 = bottom2 - height2
                draw.rectangle(((x, bottom2), (x + width, top2)), fill=color2)

            if values2 is None:
                t = max_value if total_as_max else total
                text = str(value) + ' ({}%)'.format(round(value / t * 100, 1))
                draw_rotated_text(image, text, x + width / 5, image.height - 275)
            else:
                t = max_value if total_as_max else total
                text = '{}/{} ({}/{}%)'.format(value, values2[i],
                                               round(value / t * 100, 1), round(values2[i] / t * 100, 1))

                draw_rotated_text(image, text, x + width / 5, image.height - 275)

            x += width + space

    if len(add_text) > 0:
        draw.text((iwidth / 2, 50), add_text, fill='black', font=font)

    draw.text((10, 10), caption, fill='black', font=font)
    image.save(file)
