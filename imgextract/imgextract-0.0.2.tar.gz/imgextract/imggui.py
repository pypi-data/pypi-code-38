import os
import glob
from os.path import dirname, abspath
import platform
from concurrent import futures
from PIL import Image as pillowimg
from skimage.io import MultiImage
from pdf2image import convert_from_path
from tkinter import *
from tkinter.ttk import Progressbar
from tkinter import filedialog


class GuiExtractor:
    def __init__(self):
        self.__thread_pool_executor = futures.ThreadPoolExecutor(max_workers=1)
        self.__ttk = Tk()
        self.__confwindow()
        self.__gui = Frame(self.__ttk, bd=10)
        self.__gui.grid()
        self.__gui.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.__s = Label(self.__gui, text='')
        self.__status = Label(self.__gui, text='')
        self.__var = IntVar()
        self.__progress = Progressbar(self.__gui, orient=HORIZONTAL, length=400, mode='determinate')
        self.i_folder_selected = ""
        self.o_folder_selected = ""

    def __confwindow(self):
        """ this will resize window """
        window_height = 530
        window_width = 900

        screen_width = self.__ttk.winfo_screenwidth()
        screen_height = self.__ttk.winfo_screenheight()

        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))

        self.__ttk.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

        # gui.geometry("530x400")
        self.__ttk.resizable(False, False)
        self.__ttk.title("ImgExtract")
        self.__ttk.deiconify()

    def openwindow(self):
        """ this will open window """

        # -------------- title label ----------- #
        Label(self.__gui, text='ImgExtract', font=('Helvetica', 18, 'bold')).grid(row=0, column=0, padx=10,
                                                                                  pady=10)

        # -------------- File and Folder selection  ----------- #
        def setfolderpath():
            self.i_folder_selected = filedialog.askdirectory()
            # delete content from position 0 to end
            b2.delete(0, END)
            # insert new_text at position 0
            b2.insert(0, self.i_folder_selected)

        def setfilepath():
            self.o_folder_selected = filedialog.askdirectory()
            # delete content from position 0 to end
            b5.delete(0, END)
            # insert new_text at position 0
            b5.insert(0, self.o_folder_selected)

        selection = Frame(self.__gui)
        # buttons.pack(fill="x")
        selection.grid()

        b1 = Label(selection, text="Select Input Files Folder")
        b2 = Entry(selection, width=30)
        b3 = Button(selection, text="Browse Folder", command=setfolderpath)

        b1.grid(row=1, column=1)
        b2.grid(row=1, column=2)
        b3.grid(row=1, column=3)

        b4 = Label(selection, text="Select Output Images Folder")
        b5 = Entry(selection, width=30)
        b6 = Button(selection, text="Browse Folder", command=setfilepath)

        b4.grid(row=2, column=1, padx=5, pady=5)
        b5.grid(row=2, column=2, padx=5, pady=5)
        b6.grid(row=2, column=3, padx=5, pady=5)

        # -------------- title label ----------- #
        Label(self.__gui, text='Select File Type', font=('Helvetica', 10, 'bold')).grid(row=3, column=0, padx=10,
                                                                                        pady=10)
        # -------------- radio button frame ----------- #
        frm = Frame(self.__gui, bd=10)
        frm.grid()

        self.__var.set(1)

        mild = Radiobutton(frm, text='PDF', variable=self.__var, value=1)
        mild.grid(row=4, column=0)
        medium = Radiobutton(frm, text='TIF', variable=self.__var, value=2)
        medium.grid(row=4, column=1)

        # -------------- buttons frame ----------- #
        frm1 = Frame(self.__gui, bd=10)
        frm1.grid()

        d = Button(frm1, text="Start Process", command=self.__start, width=12)
        d.grid(row=5, column=0, padx=10, pady=0)

        c = Button(frm1, text="Cancel", command=self.__closewindow, width=12)
        # c['state'] = 'disabled' or 'normal'
        c.grid(row=5, column=1, padx=10, pady=30)

        # -------------- progressbar ----------- #
        self.__progress.grid(row=6, column=0, padx=0, pady=0)
        self.__progress.grid_remove()

        self.__status.grid(row=7, column=0, padx=0, pady=0)

        self.__s.grid(row=8, column=0, padx=10, pady=30)

        self.__ttk.tk.call('wm', 'iconphoto', self.__ttk._w, PhotoImage(file=dirname(
            abspath(__file__)) + os.sep + 'da_icon.png'))

        self.__ttk.mainloop()

    def __setcount(self, file, count, length, output):
        """ this will set counter in window """

        if file is not None:
            if count == length:

                self.__progress.grid()
                self.__progress['value'] = 100

                self.__s['text'] = "Image extraction completed from all files,\nplease find images at " + output

                self.__status['text'] = str(count) + " of " + str(length) + " file(s) completed"
            else:

                self.__progress.grid()
                self.__progress['value'] = int((count / length) * 100)

                self.__s['text'] = os.path.basename(file) + " is being extracted...."
                self.__status['text'] = str(count) + " of " + str(length) + " file(s) completed"
        else:
            self.__s['text'] = "No Files Found"

    def __pdfutil(self, file, output_path):
        """ this will extract text from  pdf file """

        if platform.system() == 'Windows':
            images = convert_from_path(file,
                                       poppler_path=dirname(abspath(__file__)) + os.sep + 'poppler' + os.sep + 'bin')
        else:
            images = convert_from_path(file)

        file_name = os.path.basename(file)

        for i, img in enumerate(images, start=1):
            path = output_path + os.sep + file_name + '_' + str(i) + ".jpg"
            img.save(path, 'JPEG')

    def __tifutil(self, file, output_path):
        """ this will extract text from tif images """
        file_name = os.path.basename(file)

        images = MultiImage(file, plugin='pil')

        for i, img in enumerate(images, start=1):
            pil_img = pillowimg.fromarray(img)
            path = output_path + os.sep + file_name + '_' + str(i) + ".jpg"
            pil_img.save(path, 'JPEG')

    def __extractor(self):
        """ this will read files from input folder and starts process """
        if self.__var.get() == 2:

            files = glob.glob(self.i_folder_selected + "/*.TIF") + glob.glob(self.i_folder_selected + "/*.TIFF")
            ll = len(files)
            if ll != 0:
                for i, file in enumerate(files):
                    self.__setcount(file, i, ll, self.o_folder_selected)
                    self.__tifutil(file, self.o_folder_selected)
                self.__setcount("", ll, ll, self.o_folder_selected)
            else:
                print('No file found')

        elif self.__var.get() == 1:

            files = glob.glob(self.i_folder_selected + "/*.PDF")
            ll = len(files)
            if ll != 0:
                for i, file in enumerate(files):
                    self.__setcount(file, i, ll, self.o_folder_selected)
                    self.__pdfutil(file, self.o_folder_selected)
                self.__setcount("", ll, ll, self.o_folder_selected)
            else:
                print('No file found')

    def __start(self):
        """ this will start process in thread """
        self.__thread_pool_executor.submit(self.__extractor)

    def __closewindow(self):
        """ this will close window """
        self.__thread_pool_executor.shutdown(wait=False)
        self.__ttk.quit()
        self.__ttk.destroy()
        raise ValueError()


if __name__ == '__main__':
    cc = GuiExtractor()
    cc.openwindow()
