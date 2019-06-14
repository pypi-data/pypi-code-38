import pyautogui as pag
import time
from datetime import datetime
from tzhutils.utils import *
import pyperclip

#set参数
TIME =  str(datetime.now())[:-16]
PERSON = '唐梓豪'
TITLE = '低温车间零件申购c' + '-' + PERSON + '-' + TIME
BUYER = '采购部'
USER = '设备部'
PROJECT = TITLE
REASON = '设备维修、保养，零件或材料采购'
NUMBER = '1'
UNIT = '批'
GUIGE = '见附件'
PRICE = '20000'

'''
关于偏移量参数：
right_x = 1000 
down_y = 40
'''

#循环找图函数
def while_template(file_name):
    while 1:
        try:
            print(f"Looking for {file_name}.......")
            x, y = pag.locateCenterOnScreen("pic/"+file_name)
            pag.moveTo(x, y)
            if x and y:
                pag.click()
                print(f"Find {file_name} at ({x},{y})")
                return x,y
                break
        except Exception as e:
            print(f"Not find {file_name}.......")


#复制粘贴函数            
def ctl_cv(info):
    pyperclip.copy(info)
    pag.hotkey('ctrl', 'v')
    print(f"填好信息:{info}")
    
    
#单次填写           
def fill_info(fname, info=None, right_x=None, down_y=None):
    x, y = while_template(fname)
    #orientation_of_fname = fname.split('.')[0].split('_')[1]
    if x and y:
        if right_x:
            right_added_x = x + right_x 
            right_added_y = y 
            pag.moveTo(right_added_x, right_added_y)
            pag.click()
            if info:
                ctl_cv(info)
                
        elif down_y:
            down_x = x
            down_y = y + down_y
            pag.moveTo(down_x, down_y)
            pag.click()
            if info:
                ctl_cv(info)
            
            
#打开新建流程页面function
def open_setup_page():
    while_template('process.png')
    while_template('newsetup.png')
    while_template('apply.png')        
    time.sleep(5)
    print(while_template('waiting.png'))

    
#填表    
def fill_params():
    #fill title
    fill_info(fname='title_right.png',info=TITLE, right_x=100)
    #fill buyer
    fill_info(fname='buyer_right.png', info=BUYER, right_x=100)
    time.sleep(2)
    x_b , y_b = while_template('caigoubu_click.png')
    pag.moveTo(x_b, y_b)
    pag.click()
    #fill user
    fill_info(fname='user_right.png', info=USER, right_x=100)
    time.sleep(2)
    x_b , y_b = while_template('shebeibu_click.png')
    pag.moveTo(x_b, y_b)
    pag.click()
    #fill project
    fill_info(fname='apply_project_down.png', info=PROJECT, down_y=35)
    #fill reason
    fill_info(fname='reason_down.png', info=REASON, down_y=35)
    #fill number
    fill_info(fname='number_down.png', info=NUMBER, down_y=35)
    #fill unit
    fill_info(fname='unit_down.png', info=UNIT, down_y=35)
    #fill guige
    fill_info(fname='param_down.png', info=GUIGE, down_y=35)
    #fill price
    fill_info(fname='price_down.png', info=PRICE, down_y=35)
    #upload files
    x_upload, y_upload = while_template(file_name='upload_file.png')
    pag.moveTo(x_upload, y_upload)
    pag.click()
    timeforfile = str(TIME).replace('-', '.')
    ctl_cv(timeforfile)
    pag.press("enter")
    
#main函数           
@wrap_time
def main():
    #open_setup_page()
    fill_params()
    
    
if __name__ == "__main__":
    main()
    


