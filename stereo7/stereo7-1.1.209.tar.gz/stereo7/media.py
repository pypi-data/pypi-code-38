from PIL import Image
import fileutils
import os


def launch_images(infile, sizes=None, filename_format='{}x{}.png'):
    if sizes is None:
        sizes = [
            (640, 960),
            (640, 1136),
            (1024, 768),
            (2048, 1536),
            (2208, 1242),
        ]

    for size in sizes:
        outfile = filename_format.format(size[0], size[1])
        im = Image.open(infile)
        if size[0] < size[1]:
            s = max(im.width, im.height)
            im = im.resize((s, s), 1)
            im = im.rotate(-90)
            im = im.resize((size[0], size[1]), 1)
            im.save(outfile, "PNG")

        rx = 1.0 * size[0] / im.width
        ry = 1.0 * size[1] / im.height

        if rx != ry:
            r = max(rx, ry)
            rsize = (int(im.width * r), int(im.height * r))
            im = im.resize(rsize, 1)
            l = (rsize[0] - size[0]) / 2
            r = im.width - l
            t = (rsize[1] - size[1]) / 2
            b = im.height - t
            im = im.crop((l, t, r, b))
        else:
            im = im.resize(size, 1)
        im = im.resize(size, 1)
        im.save(outfile)


def icons(infile, sizes=None, filename_format='Icon-{}.png'):
    if sizes is None:
        sizes = [20, 29, 32, 40, 48, 58, 60, 72, 76, 80, 87, 96, 120, 152, 167, 180, 1024]

    android_sizes = [32, 48, 72, 96]
    for size in sizes:
        outfile = filename_format.format(size)
        if size in android_sizes:
            files = {
                32: 'drawable-ldpi/icon.png',
                48: 'drawable-mdpi/icon.png',
                72: 'drawable-hdpi/icon.png',
                96: 'drawable-xhdpi/icon.png',
            }
            outfile = files[size]
            fileutils.createDirForFile(outfile)

        im = Image.open(infile)
        im.thumbnail((size, size), Image.ANTIALIAS)
        if (im.mode == 'RGBA' or 'transparency' in im.info) and size not in android_sizes:
            bg = Image.new("RGB", im.size, 2255)
            bg.paste(im)
            im = bg
        im.save(outfile)


def osx(infile, outfile='icon.icns'):
    def create_iconset():
        sizes = [
            [16, 'icon.iconset/icon_16x16.png'],
            [32, 'icon.iconset/icon_16x16@2x.png'],
            [32, 'icon.iconset/icon_32x32.png'],
            [64, 'icon.iconset/icon_32x32@2x.png'],
            [128, 'icon.iconset/icon_128x128.png'],
            [256, 'icon.iconset/icon_128x128@2x.png'],
            [256, 'icon.iconset/icon_256x256.png'],
            [512, 'icon.iconset/icon_256x256@2x.png'],
            [512, 'icon.iconset/icon_512x512.png'],
            [1024, 'icon.iconset/icon_512x512@2x.png'],
        ]
        fileutils.createDir('icon.iconset')
        for size in sizes:
            w = size[0]
            out = size[1]
            im = Image.open(infile)
            im.thumbnail((w, w), Image.ANTIALIAS)
            if (im.mode == 'RGBA' or 'transparency' in im.info):
                bg = Image.new("RGB", im.size, 2255)
                bg.paste(im)
                im = bg
            im.save(out)

    def convert():
        os.system('iconutil --convert icns icon.iconset')

    create_iconset()
    convert()


def crop_long_image(in_image, out_image_pattern='', description_file=''):
    if not out_image_pattern:
        out_image_pattern = in_image[0:in_image.find('.', -1)] + '_{}' + '.png'

    im = Image.open(in_image)
    x = 0
    w = 2048
    j = 1

    xml = ''
    while x < w:
        part = im.crop((x, 0, w, im.height))
        path = out_image_pattern.format(j)
        part.save(path, 'PNG')
        xml += '\n\t<node name="{}" type="sprite" image="{}" center="0x0" pos="{}x0"/>'.format(j, path, x)
        x = w
        w = min(w + 2048, im.width)
        j += 1

    xml = '<node name="image" type="node" size="{}x{}" center="0x0">{}\n</node>'.format(im.width, im.height, xml)
    if description_file:
        fileutils.write(description_file, xml)

if __name__ == '__main__':
    icons('icon.png', sizes=[1024])
