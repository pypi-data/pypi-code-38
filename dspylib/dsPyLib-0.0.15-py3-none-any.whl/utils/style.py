# -*-coding:utf-8-*-
__author__ = 'Dragon Sun'

from enum import Enum

"""
    仅支持Bash以及兼容Bash的Shell
    
    语法：
        echo -e "\033(属性字符串)(要显示的字符串)\033[0m"
        echo -e "\033[文字背景色;文字前景色m(要显示的字符串)\033[0m"
        echo -e "\033[文字前景色m(要显示的字符串)\033[0m"
        
    属性项：
    　　\033[0m       关闭所有属性 
    　　\033[1m       粗体
    　　\033[2m       一半亮度
    　　\033[4m       下划线 
    　　\033[5m       闪烁 
    　　\033[7m       反显 
    　　\033[8m       消隐 
    　　\033[30m—37m  设置前景色 
    　　\033[40m—47m  设置背景色 
    　　\033[nA       光标上移n行 
    　　\033[nB       光标下移n行 
    　　\033[nC       光标右移n行 
    　　\033[nD       光标左移n行 
    　　\033[y;xH     设置光标位置(x, y)
    　　\033[2J       清屏 
    　　\033[K        清除从光标到行尾的内容 
    　　\033[s        保存光标位置 
    　　\033[u        恢复光标位置 
    　　\033[?25l     隐藏光标 
    　　\033[?25h     显示光标
    
        前景色     背景色     颜色
        30         40        黑(black)
        31         41        暗红(cayenne)
        32         42        暗绿(clover)
        33         43        暗黄(asparagus)
        34         44        暗蓝(midnight)
        35         45        紫(purple)           
        36         46        暗蓝绿(teal)             
        37         47        灰(silver)
        90         100       深灰(steel)
        91         101       红(red)
        92         102       绿(green)
        93         103       黄(yellow)
        94         104       蓝(blue)
        95         105       洋红(magenta)
        96         106       蓝绿(cyan)
        97         107       浅灰(mercury)     
        
    例子：
        1、蓝底黄字
            echo -e "\033[44;33m蓝底黄字\033[0m"
        2、红字
            echo -e "\033[31m红字\033[0m"
"""


class FrontColor(Enum):
    blank = 30
    cayenne = 31
    clover = 32
    asparagus = 33
    midnight = 34
    purple = 35
    teal = 36
    silver = 37
    steel = 90
    red = 91
    green = 92
    yellow = 93
    blue = 94
    magenta = 95
    cyan = 96
    mercury = 97


class BackgroundColor(Enum):
    blank = 40
    cayenne = 41
    clover = 42
    asparagus = 43
    midnight = 44
    purple = 45
    teal = 46
    silver = 47
    steel = 100
    red = 101
    green = 102
    yellow = 103
    blue = 104
    magenta = 105
    cyan = 106
    mercury = 107


def _style(s, style):
    return style + s + '\033[0m'


def color(s, front: FrontColor, background: BackgroundColor = None):
    if background:
        style = '\033[%s;%sm' % (background.value, front.value)
    else:
        style = '\033[%sm' % front.value
    return _style(s, style)


def bold(s):
    return _style(s, '\033[1m')


def underline(s):
    return _style(s, '\033[4m')


def flash(s):
    return _style(s, '\033[5m')


if __name__ == '__main__':
    colors = (30, 31, 32, 33, 34, 35, 36, 37, 90, 91, 92, 93, 94, 95, 96, 97)
    for i in colors:
        print('\033[%dm 这是文字(%d) \033[0m' % (i, i))

    print(color('你好', FrontColor.red))
