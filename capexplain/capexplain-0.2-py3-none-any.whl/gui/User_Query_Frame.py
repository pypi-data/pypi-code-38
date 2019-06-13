"""
User query template frame
"""
import tkinter as tk
from tkinter import *
from tkinter import ttk
import pandas as pd

class User_Query_Frame:

	def __init__(self,conn=None,table_dict = None,parent=None):

		self.table_dict = table_dict
		self.conn = conn
		self.parent = parent
		self.attr_list = None
		self.user_query = None

		self.query_frame=ttk.Frame(self.parent,padding=(3,3,12,12))
		self.parent.columnconfigure(0, weight=1)
		self.parent.rowconfigure(0, weight=1)
		self.query_frame.grid(column=0,row=0,sticky='nsew')
		self.query_frame.rowconfigure(0,weight=3)
		self.query_frame.rowconfigure(1,weight=1)
		self.query_frame.rowconfigure(2,weight=3)
		self.query_frame.rowconfigure(3,weight=3)
		self.query_frame.rowconfigure(4,weight=3)
		self.query_frame.rowconfigure(5,weight=3)

		self.query_frame.columnconfigure(0,weight=3)
		self.query_frame.columnconfigure(1,weight=3)
		self.query_frame.columnconfigure(2,weight=3)
		self.query_frame.columnconfigure(3,weight=3)
		self.query_frame.columnconfigure(4,weight=3)
		self.query_frame.columnconfigure(5,weight=3)

		self.select_frame = Frame(self.query_frame)
		self.select_frame.grid(row=2,column=0,columnspan=6,sticky='nsew')

		self.select_frame.columnconfigure(0,weight=4)
		self.select_frame.columnconfigure(1,weight=6)
		self.select_frame.columnconfigure(2,weight=6)
		self.select_frame.columnconfigure(3,weight=4)
		self.select_frame.columnconfigure(4,weight=1)
		self.select_frame.columnconfigure(5,weight=4)
		self.select_frame.columnconfigure(6,weight=1)
		self.select_frame.columnconfigure(7,weight=1)
		self.select_frame.columnconfigure(8,weight=4)

		self.from_where = StringVar()
		self.select_clause = StringVar()

#************************************************* Choose Table****************************************************************

		self.table_label = Label(self.query_frame,text='Choose Table:',font=('New Times Roman Bold',12))
		self.table_label.grid(row=0,column=1,sticky='nsew')
		self.table = ttk.Combobox(self.query_frame,width=15,state='readonly')
		self.table.bind('<<ComboboxSelected>>', self.table_decide_attrs)
		self.table['values'] = list(self.table_dict.keys())
		self.table.grid(row=0,column=2,sticky='ew')

#*************************************************  SELECT  ******************************************************************
		self.agg_label = Label(self.select_frame,text='Aggregate',font=('New Times Roman Bold',10))
		self.agg_label.grid(row=1,column=3,sticky='e')
		self.agg_label = Label(self.select_frame,text='Over',font=('New Times Roman Bold',10))
		self.agg_label.grid(row=1,column=5,sticky='ew')

		self.select_label = Label(self.select_frame,text="SELECT",font=('New Times Roman Bold',12))
		self.select_label.grid(row=2,column=0,sticky='ew')
		self.select_content = Label(self.select_frame, textvariable=self.select_clause,font=('New Times Roman Bold',12),wraplength=400)
		self.select_content.grid(row=2,column=1,columnspan=2,sticky='ew')
		self.agg_type = ttk.Combobox(self.select_frame,width=5,state='readonly')
		self.agg_type.grid(row=2,column=3,sticky=E)
		self.first_bracket = Label(self.select_frame,text='(')
		self.first_bracket.grid(row=2,column=4,sticky=E)
		self.agg_attr = ttk.Combobox(self.select_frame,width=8,state='readonly')
		self.agg_attr.bind('<<ComboboxSelected>>', self.update_query_frame)
		self.agg_attr.grid(row=2,column=5,sticky='ew')
		self.second_bracket = Label(self.select_frame,text=')')
		self.second_bracket.grid(row=2,column=6,sticky=W)
		self.as_label = Label(self.select_frame,text=' AS ',font=('New Times Roman Bold',12))
		self.as_label.grid(row=2,column=7,sticky='we')
		self.alias = Entry(self.select_frame,bg="white",width=2)
		self.alias.grid(row=2,column=8,sticky='we')

#*************************************************   FROM   ********************************************************************     
		self.from_table = Label(self.query_frame,text="FROM",font=('New Times Roman Bold',12))
		self.from_table.grid(row=3,column=0,sticky='ew')
		self.from_table = Label(self.query_frame,textvariable=self.from_where,font=('New Times Roman Bold',12))
		self.from_table.grid(row=3,column=1,sticky='ew')

#*****************************************************GROUP BY ******************************************************************		
		self.group_by_label = Label(self.query_frame,text="GROUP BY",font=('New Times Roman Bold',12))
		self.group_by_label.grid(column=0,row=4)

		self.group1 = ttk.Combobox(self.query_frame,width=13,state='readonly')
		self.group1.grid(column=1,row=4)
		self.group1.bind('<<ComboboxSelected>>', self.update_query_frame)

		self.group2 = ttk.Combobox(self.query_frame,width=13,state='readonly')
		self.group2.grid(column=2,row=4)
		self.group2.bind('<<ComboboxSelected>>', self.update_query_frame)

		self.group3 = ttk.Combobox(self.query_frame,width=13,state='readonly')
		self.group3.grid(column=3,row=4)
		self.group3.bind('<<ComboboxSelected>>', self.update_query_frame)

		self.group4 = ttk.Combobox(self.query_frame,width=13,state='readonly')
		self.group4.grid(column=4,row=4)
		self.group4.bind('<<ComboboxSelected>>', self.update_query_frame)

		self.group5 = ttk.Combobox(self.query_frame,width=13,state='readonly')
		self.group5.grid(column=5,row=4)
		self.group5.bind('<<ComboboxSelected>>', self.update_query_frame)

#******************************************************Functions*****************************************************************

	def table_decide_attrs(self,event):
		self.attr_list= self.table_dict[self.table.get()]
		self.from_where.set(self.table.get())
		self.shown_attrs = self.attr_list
		self.shown_attrs.insert(0,' ')
		self.shown_attrs.insert(1,'*')
		self.shown_attrs.sort()
		self.group1.set(' ')
		self.group2.set(' ')
		self.group3.set(' ')
		self.group4.set(' ')
		self.group5.set(' ')
		self.agg_type.set(' ')
		self.agg_attr.set(' ')
		self.group1['values'] = self.shown_attrs
		self.group2['values'] = self.shown_attrs
		self.group3['values'] = self.shown_attrs
		self.group4['values'] = self.shown_attrs
		self.group5['values'] = self.shown_attrs
		self.agg_attr['values'] = self.shown_attrs

		table_name = self.table.get()
		q = "select distinct substring( agg from '(sum|max|avg|min|count)') as agg from dev." +str(table_name)+'_global'
		agg_df = pd.read_sql(q,self.conn)
		agg_list = agg_df['agg'].values.tolist()
		self.agg_type['values'] = agg_list

	def update_query_frame(self,event):
		g1 = self.group1.get()
		g2 = self.group2.get()
		g3 = self.group3.get()
		g4 = self.group4.get()
		g5 = self.group5.get()
		attr = self.agg_attr.get()
		self.chosen_attrs = [g1,g2,g3,g4,g5,attr]
		self.shown_attrs = list(set(self.attr_list) - set(list(filter(None, self.chosen_attrs))))
		self.selected_attrs = list(filter(lambda x :' ' not in x,self.chosen_attrs ))
		if(self.shown_attrs == []):
			self.shown_attrs = [' ']
		if(self.shown_attrs[0]!=' '):
			self.shown_attrs.insert(0,' ')
		self.shown_attrs.sort()
		self.group1['values'] = self.shown_attrs
		self.group2['values'] = self.shown_attrs
		self.group3['values'] = self.shown_attrs
		self.group4['values'] = self.shown_attrs
		self.group5['values'] = self.shown_attrs
		self.agg_attr['values'] = self.shown_attrs
		if attr in self.selected_attrs:
			self.selected_attrs.remove(attr)
		self.select_clause.set(','.join(self.selected_attrs))

	def get_query(self):
		query_group_str = self.select_clause.get()
		query_group_list = query_group_str.split(',')
		query_group_list.sort()
		sorted_query_group = ','.join(query_group_list)
		alias_name = self.alias.get().lower()
		table_name = self.from_where.get()
		agg_function=self.agg_type.get()+'('+self.agg_attr.get()+')'

		user_agg =self.agg_type.get()+'_'+self.agg_attr.get()

		query = "SELECT " +self.select_clause.get() + ","+agg_function+ " as " + alias_name+\
		"\nFROM " + table_name+\
		"\nGROUP BY " + query_group_str+";"

		return query,sorted_query_group,agg_function,user_agg,alias_name,table_name



if __name__ == '__main__':
	root = Tk()
	uqf = User_Query_Frame(parent=root)
	root.title('CAPE')
	root.mainloop()



		







		

