# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 23:23:49 2019

@author: Steven
"""

import sqlite3 as sq
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import os
class VGUIAPP:
 def __init__(self):
 self.root=Tk()
 self.root.wm_title('SQlite3操作')
 #禁止调整窗口大小
 self.root.resizable(0, 0) 
 self.frame=Frame(self.root)
 self.frame.pack()
 #数据库连接标识
 self.conflag=0
 #row=0
 self.lab_sid=Label(self.frame,text="学号").grid(row=0,column=0)
 self.vt_sid=StringVar()
 self.txt_sid=Entry(self.frame,textvariable=self.vt_sid,justify='left').grid(row=0,column=1)
 self.lab_sname=Label(self.frame,text="姓名").grid(row=0,column=2)
 self.vt_sname=StringVar()
 self.txt_sname=Entry(self.frame,textvariable=self.vt_sname,justify='left').grid(row=0,column=3)
 #row=1
 self.but_connect=Button(self.frame,text="连接数据库",command=self.ev_but_connect).grid(row=1,column=0,columnspan=2)
 self.but_close=Button(self.frame,text="关闭数据库",command=self.ev_but_close).grid(row=1,column=2,columnspan=2)
 #row=2
 self.but_insert=Button(self.frame,text="插入",command=self.ev_but_insert).grid(row=2,column=0)
 self.but_search=Button(self.frame,text="查询",command=self.ev_but_search).grid(row=2,column=1)
 self.but_update=Button(self.frame,text="更新",command=self.ev_but_update).grid(row=2,column=2)
 self.but_delete=Button(self.frame,text="删除",command=self.ev_but_delete).grid(row=2,column=3)
 def ev_but_connect(self):
 try:
 conn=self.get_connect()
 c=conn.cursor()
 c.execute("CREATE TABLE IF NOT EXISTS stuInfo (sid INTEGER PRIMARY KEY,sname TEXT)")
 connmit()
 self.conflag=1
 messagebox.showinfo('提示','连接成功！')
 except:
 ex="未知错误:"+ str(sys.exc_info()[0])
 messagebox.showerror('错误',ex)
 def ev_but_close(self):
 try:
 if(self.conflag==0):
 messagebox.showinfo('提示','数据库是关闭的！')
 return
 conn=self.get_connect()
 conn.close()
 self.conflag=0
 messagebox.showinfo('提示','关闭成功！')
 except:
 ex="未知错误:"+ str(sys.exc_info()[0])
 messagebox.showerror('错误', ex)
 def ev_but_delete(self):
 try:
 if(self.conflag==0):
 messagebox.showinfo('提示','请连接数据库！')
 return
 conn=self.get_connect()
 c=conn.cursor()
 sid=self.vt_sid.get()
 stu=(sid,)
 c.execute("DELETE FROM stuInfo WHERE sid=?",stu)
 connmit()
 self.vt_sname.set("")
 messagebox.showinfo('提示','删除成功！')
 except:
 ex="未知错误:"+ str(sys.exc_info()[0])
 messagebox.showerror('错误', ex)
 def ev_but_update(self):
 try:
 if(self.conflag==0):
 messagebox.showinfo('提示','请连接数据库！')
 return
 conn=self.get_connect()
 c=conn.cursor()
 sid=int(self.vt_sid.get())
 sname=self.vt_sname.get()
 stu=(sname,sid)
 c.execute("UPDATE stuInfo SET sname=? WHERE sid=?",stu)
 connmit()
 messagebox.showinfo('提示','更新成功！')
 except:
 ex="未知错误:"+ str(sys.exc_info()[0])
 messagebox.showerror('错误', ex)
 def ev_but_insert(self):
 try:
 if(self.conflag==0):
 messagebox.showinfo('提示','请连接数据库！')
 return
 conn=self.get_connect()
 c=conn.cursor()
 sid=int(self.vt_sid.get())
 sname=self.vt_sname.get()
 stu=(sid,sname)
 c.execute("INSERT INTO stuInfo VALUES (?,?)",stu)
 connmit()
 messagebox.showinfo('提示','插入成功！')
 except:
 ex="未知错误:"+ str(sys.exc_info()[0])
 messagebox.showerror('错误', ex)
 def ev_but_search(self):
 try:
 if(self.conflag==0):
 messagebox.showinfo('提示','请连接数据库！')
 return
 conn=self.get_connect()
 c=conn.cursor()
 sid=self.vt_sid.get()
 stu=(sid,)
 c.execute("SELECT sname FROM stuInfo WHERE sid=?",stu)
 sname=c.fetchone()
 connmit()
 self.vt_sname.set(sname)
 except:
 ex="未知错误:"+ str(sys.exc_info()[0])
 messagebox.showerror('错误', ex)
 #创建数据库或连接数据库
 def get_connect(self):
 conn=sq.connect('stu.db')
 return conn
mapp_v=VGUIAPP()
mapp_v.root.mainloop()