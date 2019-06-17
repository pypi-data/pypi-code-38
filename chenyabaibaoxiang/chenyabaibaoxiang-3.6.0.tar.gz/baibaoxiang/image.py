from PIL import Image
import pytesseract
import traceback
class Image_go:
    def image_go(self,image_addres):
        try:
            # c=open(image_addres)
            im = Image.open(image_addres)
            # jiage = pytesseract.image_to_string(im,lang='chi_sim')
            jiage = pytesseract.image_to_string(im,lang='chi_sim')
            return jiage
        except Exception as e:
            ee = traceback.format_exc()
            print(ee)


if __name__ == "__main__":
    # a=Image_go().image_go("D:\\11231.png")
    # print(a)
    a = Image_go().image_go("D:\\b.png")
    print(a)


'''
1.安装tesseract之后
2.将根目录放到path之中，例：D:\job\software\tesseract\install\Tesseract-OCR
3.接着将eng.traineddata所在文件放到变量中
 例：
变量名：TESSDATA_PREFIX
值：D:\job\software\tesseract\install\Tesseract-OCR\tessdata
4.如果运行时报错路径，就将pytesseract.py中tesseract_cmd的值改成，路径\tesseract.exe
'''