# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2018/7/30 0030
__author__ = 'huohuo'
import scipy.io
data = scipy.io.loadmat(r'D:\pythonproject\report\data\variant_anno.v2.maf')  # 读取mat文件
print(data.keys())   # 查看mat文件中的所有变量
print(data['matrix1'])
print(data['matrix2'])
matrix1 = data['matrix1']
matrix2 = data['matrix2']
print(matrix1)
print(matrix2)
# scipy.io.savemat('matData2.mat',{'matrix1':matrix1, 'matrix2':matrix2})  # 写入mat文件

if __name__ == "__main__":
    pass
    

