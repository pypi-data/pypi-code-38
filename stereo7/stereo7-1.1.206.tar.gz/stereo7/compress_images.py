import os
from PIL import Image
import tempfile
import fileutils


def mb(size):
    return round(float(size) / (1024.0 * 1024.0), 2)


def run(parser=None):
    fileutils.ignore_folders.extend(['steam', 'cocoscenes'])
    fileutils.inspectResources()

    total_images_size = 0
    optimized = 0
    for i, file in enumerate(fileutils.images):
        fullpath = fileutils.root_dir + '/Resources/' + file
        size = fileutils.getSize(fullpath)
        total_images_size += size

        im = Image.open(fullpath)
        temppath = tempfile.gettempdir() + '/' + file
        fileutils.createDirForFile(temppath)
        im.save(temppath, quality=99)

        new_size = fileutils.getSize(temppath)
        os.remove(temppath)

        diff = size - new_size
        min_diff = int(parser.s) if parser is not None else 128 * 1024
        if diff > min_diff:
            im.save(fullpath, quality=99)
            optimized += diff
        print 'Processing {}% ({}/{})'.format(int(i * 100.0 / len(fileutils.images)), i, len(fileutils.images))

    print 'Optimized {}mb. \nSumary size before: {}mb. \nFinaly sumary size: {}mb'. \
        format(mb(optimized), mb(total_images_size), mb(total_images_size - optimized))


if __name__ == '__main__':
    run()
