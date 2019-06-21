# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2018/6/28 0028
__author__ = 'huohuo'
import os
try:
    import PythonMagick
    from PythonMagick import Image
    import PyPDF2
except:
    pass
bgcolor = '#FFFFFF'


def pdf2img(input_pdf, postfix='.png', **kwargs):
    img = Image(input_pdf)
    img.density('300')
    size = "%sx%s" % (img.columns(), img.rows())
    output_img = Image(size, bgcolor)
    output_img.type = img.type
    output_img.composite(img, 0, 0, PythonMagick.CompositeOperator.SrcOverCompositeOp)
    output_img.resize(str(img.rows()))
    output_img.magick('JPG')
    output_img.quality(75)
    if 'out_path' in kwargs:
        output_jpg = kwargs['out_path']
    else:
        output_jpg = input_pdf.replace(".pdf", postfix)
    if os.path.exists(output_jpg):
        os.remove(output_jpg)
    output_img.write(output_jpg)



class ManImage:
    """
    Manipulate Image Object
    """
    def __init__(self, i_file, o_dire):
        """
        init args
        :param i_file: (str) input pdf file (eg: "/home/file.pdf")
        :param o_dire: (str) output image directory (eg: "/home/")
        """
        self.i_file = i_file
        self.o_dire = o_dire

    def __str__(self):
        traceback = "Executing under {0.argv[0]} of {1.i_file} into {2.o_dire}......".format(sys, self, self)
        return traceback

    def playpdf(self, ds):
        """
        split pdf file
        :param ds: (int) set ds = 1024 ~= 1MB output under my test
        :return: splited PNG image file
        """
        # PythonMagick.Image
        pdf_file = PyPDF2.PdfFileReader(file(self.i_file, "rb"))
        pages = pdf_file.getNumPages()
        print('Totally get ***{0:^4}*** pages from "{1.i_file}", playpdf start......'.format(pages, self))
        try:
            for i in range(pages):
                image = PythonMagick.Image(self.i_file + '[' + str(i) + ']')
                # image.density(str(ds))
                image.read(self.i_file + '[' + str(i) + ']')
                image.magick("PNG")
                image.write(os.path.join(self.o_dire, '%d.png'%(i+1)))
                print("{0:>5}     page OK......".format(i + 1))
        except Exception, e:
            print(str(e))



if __name__ == "__main__":
    # pdf2img('D:\pythonproject\\report\data\part1\\tmb.pdf')
    pdf_path = r'/pythonproject/GATCReport/results/report2.pdf'
    dir_name = r'D:\pythonproject\GATCWeb_04\Web3\static'
    o_dire = os.path.join(dir_name, 'report2')
    if os.path.exists(o_dire) is False:
        os.makedirs(o_dire)
    ManImage(i_file=pdf_path, o_dire=o_dire).playpdf(ds=1024)
    # pdf2png(pdf_path, o_dire)

