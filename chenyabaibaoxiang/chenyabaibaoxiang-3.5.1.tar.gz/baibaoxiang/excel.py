import xlwt
import time
import xlrd
#只能写不能读
class InputExcel:
    biaoti=["接口名称","接口地址","接口参数","响应状态","返回值","响应时间"]
    book = xlwt.Workbook()  # 新建一个excel
    sheet1 = book.add_sheet('case1_sheet')#添加一个sheet页
    book = xlwt.Workbook()  # 新建一个excel
    sheet1 = book.add_sheet('case1_sheet')  # 添加一个sheet页
    row = 0  # 控制行
    col = 0  # 控制列
    for stu in biaoti:
        # print(stu)
        sheet1.write(row, col, stu)
        col += 1
    row += 1
    col = 0  # 控制列
    # print(row, col)
    # sheet1.write(11, 0, '12344444')


    def input_excel(self,k):
        # print(k)
        for kk in k:
            # print(kk)
            InputExcel.sheet1.write(InputExcel.row, InputExcel.col, kk)
            InputExcel.col += 1#列+1
        InputExcel.row += 1#行+1
        InputExcel.col = 0  # 控制列
        # print(a.row,a.col)

    def input_excel_zidingyi(self,hang,k):
        lie=0
        for kk in k:
            InputExcel.sheet1.write( hang,lie, kk)
            lie += 1#列+1


    def end(self,address,name):
        tt=time.strftime("%Y%m%d%H%M%S",time.localtime())
        if address == "":
            InputExcel.book.save("D:\\baogao\\"+tt+name+"运行结果.xls")  # 保存到当前目录下
        else:
            InputExcel.book.save(address + tt + name+"运行结果.xls")  # 保存到当前目录下


class OpenExcel:
    def open_excel(self,file_address):
        excel_list=[]
        excel=xlrd.open_workbook(filename=file_address)
        '''
        excel = xlrd.open_workbook(filename="D:\linshi\涉及鲜橙收入和金额收入接口.xlsx")
        print(excel)
        '''
        sheets = excel.sheets()  # 获取工作表list。
        '''
        print(sheets)
        sheet = sheets[0]  # 通过索引顺序获取。
        sheet = excel.sheet_by_index(0)  # 通过索引顺序获取。
        sheet = excel.sheet_by_name(u'Sheet1')  # 通过名称获取。
        '''
        '''
        这里默认取的第一个sheel表
        '''
        sheet = sheets[0]
        '''
        读取行列
        '''
        nrows = sheet.nrows
        ncols = sheet.ncols
        # print("行",ncols)
        # print("列：%s\n行：%s"%(ncols,nrows))
        '''
        将每一行的前五列都读取出来
        '''
        for hang in range(1, nrows):
            xx=[]
            for lie in range(0, ncols):
                t = sheet.cell_value(hang, lie)
                if t == "":
                    t = sheet.cell_value(1, 1)
                xx.append(t)
            # print(xx)
            excel_list.append(xx)
        return excel_list

