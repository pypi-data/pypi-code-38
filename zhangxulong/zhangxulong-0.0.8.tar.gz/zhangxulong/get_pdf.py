import os
from PyPDF2 import PdfFileReader
import time


class Pdf_process:
    def search_and_rename_to_dir(self, src_dir, des_dir):
        for root, dirs, names in os.walk(src_dir):
            for name_item in names:
                if '.pdf' in name_item.lower():
                    pdf_path = os.path.join(root, name_item)
                    reader_pdf = PdfFileReader(open(pdf_path, 'rb'))
                    try:
                        title_name = str(reader_pdf.getDocumentInfo().title)[:160].replace('/','_').replace('\\','_') + '.pdf'
                    except:
                        continue
                    if title_name == '.pdf':
                        title_name = "%s.pdf" % time.strftime('%Y%m%d%H%M%S', time.localtime())
                    des_pdf = os.path.join(des_dir, title_name)
                    if not os.path.isdir(des_dir):
                        os.makedirs(des_dir)
                    os.rename(pdf_path, des_pdf)

        return 0


if __name__ == '__main__':
    pdf_pre = Pdf_process()
    pdf_pre.search_and_rename_to_dir('svd', 'svdN')
