#   @author: 马朝威 1570858572@qq.com
#   @time: 2019-02-24 21:56

from os import listdir


def floderiterdeco(path):
    def wrapper(func):
        def inner(*args):
            file_names = listdir(path)
            for file_name in file_names:
                file_path = path+'//'+file_name
                with open(file_path,'r',encoding='utf-8') as f:
                    func(f)
        return inner
    return wrapper



@floderiterdeco('E:\\test')
def print_file_content(file):
    print(file.read())
    print('完成')












