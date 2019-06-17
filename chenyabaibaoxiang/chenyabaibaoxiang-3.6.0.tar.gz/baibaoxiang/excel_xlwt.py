import xlwt
import time
#只能写不能读
class a:
    """
    不满足使用标准
    """
    biaoti=["接口名称","接口地址","接口参数","响应状态","返回值"]
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
            a.sheet1.write(a.row, a.col, kk)
            a.col += 1
        a.row += 1
        a.col = 0  # 控制列
        # print(a.row,a.col)


    def end(self,address,name):
        tt=time.strftime("%Y%m%d%H%M%S",time.localtime())
        if address == "":
            a.book.save("D:\\baogao\\"+tt+name+"运行结果.xls")  # 保存到当前目录下
        else:
            a.book.save(address + tt + name+"运行结果.xls")  # 保存到当前目录下

if __name__ == "__main__":
    print("这个已不用")