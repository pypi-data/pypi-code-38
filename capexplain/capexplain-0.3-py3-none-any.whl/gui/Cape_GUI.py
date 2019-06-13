import tkinter as tk
from tkinter import *
from tkinter import ttk
import tkinter.messagebox
from tkinter import filedialog
from tkinter import font
from tkinter.font import Font,nametofont
import pandas as pd
import psycopg2
from pandastable import TableModel
from pandastable import PlotViewer
from pandastable import Table
import re
from capexplain.explain.explanation import ExplanationGenerator
from capexplain.explain.explanation import ExplConfig
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (
	FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import logging
from mpl_toolkits.mplot3d import Axes3D
from capexplain.gui.User_Query_Frame import User_Query_Frame
from capexplain.gui.DBinfo import DBinfo
from capexplain.gui.Pattern_Frame import Local_Pattern_Frame
from capexplain.gui.Exp_Frame import Exp_Frame
from capexplain.cl.cfgoption import DictLike
from capexplain.database.dbaccess import DBConnection



#to do
# 1. fix "when misinput system have to be restart" issue
# 2. fix "drill down" in crime data set

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s line %(lineno)d: %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


# conn = psycopg2.connect(dbname="antiprov",user="antiprov",host="127.0.0.1",port="5436")
class CAPE_UI:

	def __init__(self,parent,conn,config):
		self.conn=conn
		self.config=config
		self.cur=self.conn.cursor()
		# self.assigned_local_table = assigned_local_table
		# self.assigned_global_table = assigned_global_table

#----------------------------main frame----------------------------------------#

		self.parent=parent
		self.main_frame=ttk.Frame(self.parent,padding=(3,3,12,12))

		self.main_frame.columnconfigure(0,weight=1)
		self.main_frame.columnconfigure(1,weight=8,uniform=1)
		self.main_frame.columnconfigure(2,weight=7,uniform=1)

		self.main_frame.rowconfigure(0,weight=3)
		self.main_frame.rowconfigure(1,weight=2)
		self.main_frame.rowconfigure(2,weight=2)
		self.main_frame.rowconfigure(3,weight=2)
		self.main_frame.rowconfigure(4,weight=2)
		self.main_frame.rowconfigure(5,weight=2)
		self.main_frame.rowconfigure(6,weight=2)
		self.main_frame.rowconfigure(7,weight=2)
		self.main_frame.rowconfigure(8,weight=2)
		self.main_frame.rowconfigure(9,weight=2)

#----------------------------------place frames----------------------------------#
		
		self.main_frame.grid(column=0, row=0, columnspan=3, rowspan=10, sticky='nsew')

		self.table_frame = ttk.Frame(self.main_frame, borderwidth=5, relief="sunken")
		self.table_frame.grid(column=0,row=0, columnspan=1, rowspan=10, sticky='nsew')

		self.query_frame = ttk.Frame(self.main_frame, borderwidth=5, relief="ridge")
		self.query_frame.grid(column=1, row=0, columnspan=1, rowspan=2, sticky='nsew')

		self.query_frame.rowconfigure(0,weight=5)
		self.query_frame.rowconfigure(0,weight=1)

		self.query_template_frame = ttk.Frame(self.query_frame)
		self.query_template_frame.grid(row=0,sticky='nsew')

		self.query_button_frame = ttk.Frame(self.query_frame)
		self.query_button_frame.grid(row=1,sticky='nsew')


		self.query_result = ttk.Frame(self.main_frame, borderwidth=5, relief="sunken")
		self.query_result.grid(column=1, row=2, columnspan=1, rowspan=8, sticky='nsew')

		self.local_pattern = ttk.Frame(self.main_frame, borderwidth=5, relief="sunken")
		self.local_pattern.grid(column=2, row=0, columnspan=2, rowspan=5, sticky='nsew')

		self.explanation_frame = ttk.Frame(self.main_frame, borderwidth=5, relief="sunken")
		self.explanation_frame.grid(column=2, row=5, columnspan=2, rowspan=5, sticky='nsew')


#---------------------------table frame-----------------------------------------#
		self.table_view = ttk.Treeview(self.table_frame,height=47)
		self.table_info = ttk.Label(self.table_frame, text="Database Information",font=('Times New Roman bold',11),borderwidth=5,relief=RIDGE)
		self.table_info.grid(column=0, row=0,sticky='nsew')
		self.table_view.grid(column=0, row=1)

		self.db_info = DBinfo(conn=self.conn)
		self.db_info_dict = self.db_info.get_db_info()

		table_index = 0
		for key,value in self.db_info_dict.items(): 
		   self.table_view.insert('', 'end','item'+str(table_index),text = key)
		   for n in value:
			   self.table_view.insert('item'+str(table_index),'end',text=n)
		   table_index +=1

		# self.pub_dict = {"dict_name":"pub",
		# "global_name":"dev.pub_global",
		# "local_name":"dev.pub_local"
		# }

		# self.crime_dict = {"dict_name":"crime",
		# "global_name": "dev.crime_global",
		# "local_name":"dev.crime_local"
		# }


#----------------------------Query frame----------------------------------------#

		self.query_temp = User_Query_Frame(conn=self.conn,table_dict=self.db_info_dict,parent=self.query_frame)

		self.query_button = Button(self.query_button_frame,text="Run Query",font=('Times New Roman bold',12),command=self.run_query)
		self.query_button.pack(side=RIGHT)
		self.show_global_pattern_button = Button(self.query_button_frame,text="Show Global Pattern",font=('Times New Roman bold',12),command=self.show_global_pattern)
		self.show_global_pattern_button.pack(side=RIGHT)
		self.show_local_pattern_button = Button(self.query_button_frame,text="Show Local Pattern",font=('Times New Roman bold',12),command=self.show_local_pattern)
		self.show_local_pattern_button.pack(side=RIGHT)

#----------------------------Query result frame --------------------------------#
		self.query_result.columnconfigure(0,weight=6)
		self.query_result.columnconfigure(1,weight=1)
		self.query_result.rowconfigure(0,weight=1)
		self.query_result.rowconfigure(1,weight=10)
		self.query_result.rowconfigure(2,weight=10)

		self.result_label = Label(self.query_result,text='Query Result',font=('Times New Roman bold',12),borderwidth=5,relief=RIDGE)
		self.result_label.grid(row=0,column=0,sticky='nsew')

		self.high_low_frame = Frame(self.query_result)
		self.high_low_frame.grid(column=1,row=1,rowspan=2,sticky='nsew')
		
		self.high_low_frame.columnconfigure(0,weight=1)
		self.high_low_frame.rowconfigure(0,weight=1)
		self.high_low_frame.rowconfigure(1,weight=1)
		self.high_low_frame.rowconfigure(2,weight=1)
		self.high_low_frame.rowconfigure(3,weight=1)
		self.high_low_frame.rowconfigure(4,weight=1)
		self.high_low_frame.rowconfigure(5,weight=1)
		self.high_low_frame.rowconfigure(6,weight=1)
		self.high_low_frame.rowconfigure(7,weight=1)


		self.high_button = Button(self.high_low_frame,text='High',font=('Times New Roman bold',12), command=self.handle_high)
		self.high_button.grid(column=0,row=1)

		self.low_button = Button(self.high_low_frame,text='Low',font=('Times New Roman bold',12), command=self.handle_low)
		self.low_button.grid(column=0,row=2)

		self.show_results = Frame(self.query_result)
		self.show_results.grid(column=0,row=1,sticky='nsew')

		self.show_global = Frame(self.query_result)
		self.show_global.grid(column=0,row=2,sticky='nsew')

		self.query_result_table = Table(self.show_results)
		self.query_result_table.show()

		self.parent.columnconfigure(0, weight=1)
		self.parent.rowconfigure(0, weight=1)

#---------------------------Global Pattern Frame -----------------------------------#
		
		self.show_global.rowconfigure(0,weight=1)
		self.show_global.rowconfigure(1,weight=10)
		self.show_global.columnconfigure(0,weight=1)

		self.global_pattern_label = Label(self.show_global,text="Global Patterns",font=('Times New Roman bold',12),borderwidth=5,relief=RIDGE)
		self.global_pattern_label.grid(column=0,row=0,sticky='nsew')

		self.show_global_patterns = Frame(self.show_global)
		self.show_global_patterns.grid(column=0,row=1,sticky='nsew')

		self.global_description_button = Button(self.high_low_frame,text='Describe\nGlobal',font=('Times New Roman bold',12),command=self.global_description)
		self.global_description_button.grid(column=0,row=5)

		self.global_pattern_filter_button = Button(self.high_low_frame,text='Filter \nLocal\n Pattern',font=('Times New Roman bold',12),command=self.use_global_filter_local)
		self.global_pattern_filter_button.grid(column=0,row=6)

		self.global_pattern_table = Table(self.show_global_patterns)
		self.global_pattern_table.show()

		# create a sql function for sorting the array in order to be used for filtering

		sort_array_function = "CREATE OR REPLACE FUNCTION array_sort(anyarray) RETURNS anyarray AS $$"+\
		"SELECT array_agg(x order by x) FROM unnest($1) x;"+\
		"$$ LANGUAGE sql;"

		# logger.debug(sort_array_function)
		self.cur.execute(sort_array_function)	

#------------------------------- local pattern frame---------------------------------------#
		self.local_pattern.rowconfigure(0,weight=1)
		self.local_pattern.rowconfigure(1,weight=20)
		self.local_pattern.rowconfigure(2,weight=1)
		self.local_pattern.columnconfigure(0,weight=1)
		self.local_pattern.columnconfigure(1,weight=1)
		self.local_pattern.columnconfigure(2,weight=1)
		self.local_pattern.columnconfigure(3,weight=1)
		self.local_pattern.columnconfigure(4,weight=1)


		self.local_show_patterns = Frame(self.local_pattern)
		self.local_show_patterns.grid(column=0,row=1,sticky='nsew')
		self.local_pattern_label = Label(self.local_pattern,text="Local Patterns",font=('Times New Roman bold',12),borderwidth=5,relief=RIDGE)
		self.local_pattern_label.grid(column=0,row=0,columnspan=5,sticky='nsew')
		self.local_pattern_filter_button = Button(self.local_pattern,text='Reset Query Output',font=('Times New Roman bold',12),command=self.reset_output)
		self.local_pattern_filter_button.grid(column=0,row=2)
		self.local_pattern_filter_button = Button(self.local_pattern,text='Filter Output',font=('Times New Roman bold',12),command=self.show_updated_output)
		self.local_pattern_filter_button.grid(column=2,row=2)
		self.draw_pattern_button = Button(self.local_pattern,text='Draw Pattern',font=('Times New Roman bold',12),command=self.pop_up_pattern)
		self.draw_pattern_button.grid(column=4,row=2)

		self.local_pattern_table_frame = Frame(self.local_pattern)
		self.local_pattern_table_frame.grid(row=1,column=0,columnspan=5,sticky='nsew')
		self.local_pattern_table = Table(self.local_pattern_table_frame)
		self.local_pattern_table.show()


#---------------------------------explanation frame-----------------------------# 

		self.explanation_frame.rowconfigure(0,weight=1)
		self.explanation_frame.rowconfigure(1,weight=10)
		self.explanation_frame.rowconfigure(2,weight=1)
		self.explanation_frame.columnconfigure(0,weight=10)
		self.exp_label = Label(self.explanation_frame,text="Top Explanations",font=('Times New Roman bold',12),borderwidth=5,relief=RIDGE)
		self.exp_label.grid(column=0,row=0,sticky='nsew')
		self.exp_table_frame = Frame(self.explanation_frame)
		self.exp_table_frame.grid(row=1,column=0,sticky='nsew')
		self.exp_table = Table(self.exp_table_frame)
		self.exp_table.show()
		self.describe_exp_button = Button(self.explanation_frame,text="Describe Explanation",font=('Times New Roman bold',12),command=self.pop_up_explanation)
		self.describe_exp_button.grid(row=2,column=0)

#----------------------------------Functions----------------------------------------#

	def run_query(self):
		
		self.user_query,self.query_group_str,self.agg_function,self.user_agg,self.agg_name,self.cur_table_name=self.query_temp.get_query()
		# logger.debug(self.user_query)
		self.handle_view ="\nDROP VIEW IF EXISTS user_query;"+\
		"\nCREATE VIEW user_query as "+ self.user_query
		# logger.debug(self.handle_view)
		try:
			self.cur.execute(self.handle_view)
		except:
			tkinter.messagebox.showinfo("Info","Invalid Query, Please Doublecheck!")

		self.original_query_result_df = pd.read_sql(self.user_query,self.conn)
		self.query_result_df = self.original_query_result_df

		self.plot_data_convert_dict,self.query_data_convert_dict = self.db_info.get_db_data_type(self.cur_table_name)
		self.plot_data_convert_dict[self.agg_name] = 'numeric'
		self.query_data_convert_dict[self.agg_name] = 'float'

		self.assigned_global_table = 'dev.{}_global'.format(self.cur_table_name)
		self.assigned_local_table = 'dev.{}_local'.format(self.cur_table_name)

		model = TableModel(dataframe=self.original_query_result_df)
		self.query_result_table.updateModel(model)
		self.query_result_table.redraw()

		# if(self.cur_table_name.lower()==self.pub_dict['dict_name']):
		# 	self.table_dict = self.pub_dict
		# elif(self.cur_table_name.lower()==self.crime_dict['dict_name']):
		# 	self.table_dict = self.crime_dict


	def show_global_pattern(self):

		global_query = "select array_to_string(fixed,',') as Partition,array_to_string(variable,',') as Predictor,agg,"+\
		"round((lambda)::numeric(4,2),2) as Support,model from "+self.assigned_global_table+\
		" where array_to_string(array_sort(fixed||variable),',')='"+self.query_group_str+"';"
		# logger.debug(global_query)
		self.global_pattern_df = pd.read_sql(global_query,self.conn)
		# logger.debug(self.global_pattern_df.head())
		# logger.debug(list(self.global_pattern_df))

		pattern_model = TableModel(dataframe=self.global_pattern_df)
		self.global_pattern_table.updateModel(pattern_model)
		self.global_pattern_table.redraw()


	def show_local_pattern(self):

		local_query = "select array_to_string(fixed,',') as Partition,array_to_string(variable,',') as Predictor,"+\
		"array_to_string(fixed_value,',') as partition_values,agg,model,fixed,fixed_value,variable,"+\
		"theta,param,stats,dev_pos,dev_neg from "+self.assigned_local_table+\
		" where array_to_string(array_sort(fixed||variable),',')='"+self.query_group_str+"';"

		for n in self.local_pattern_table.multiplerowlist:
			self.chosen_local_pattern = self.local_output_pattern_df.iloc[int(n)]

		self.local_output_pattern_df = pd.read_sql(local_query,self.conn)
		self.local_output_pattern_df['stats'] = self.local_output_pattern_df['stats'].str.split(',',expand=True)[0]
		self.local_output_pattern_df['stats'] = self.local_output_pattern_df['stats'].str.strip('[')
		self.local_output_pattern_df["stats"] = pd.to_numeric(self.local_output_pattern_df["stats"])
		self.local_output_pattern_df["stats"] = self.local_output_pattern_df["stats"].round(2)

		local_shown = self.local_output_pattern_df[['partition','partition_values','predictor','agg']]

		pattern_model = TableModel(local_shown)
		self.local_pattern_table.updateModel(pattern_model)
		self.local_pattern_table.redraw()


	def use_global_filter_local(self):

		pattern_df_lists = []

		for n in self.global_pattern_table.multiplerowlist:

			model_name = self.global_pattern_df.iloc[int(n)]['model']
			# logger.debug("model_name"+model_name)
			global_partition = self.global_pattern_df.iloc[int(n)]['partition']
			global_predictor = self.global_pattern_df.iloc[int(n)]['predictor']

			g_filter_l_query = " select array_to_string(fixed,',') as Partition,array_to_string(variable,',') as Predictor,"+\
			"array_to_string(fixed_value,',') as partition_values,agg,model,fixed,fixed_value,variable,"+\
			"theta,param,stats,dev_pos,dev_neg from "+self.assigned_local_table+\
			" where array_to_string(fixed,',')='"+global_partition+\
			"' and array_to_string(variable,',')='"+global_predictor+\
			"' and model = '"+model_name+"';"

			# logger.debug(g_filter_l_query)

			self.local_output_pattern_df = pd.read_sql(g_filter_l_query,self.conn)
			self.local_output_pattern_df['stats'] = self.local_output_pattern_df['stats'].str.split(',',expand=True)[0]
			self.local_output_pattern_df['stats'] = self.local_output_pattern_df['stats'].str.strip('[')
			self.local_output_pattern_df["stats"] = pd.to_numeric(self.local_output_pattern_df["stats"])
			self.local_output_pattern_df["stats"] = self.local_output_pattern_df["stats"].round(2)

			local_shown = self.local_output_pattern_df[['partition','partition_values','predictor','agg']]

		model = TableModel(dataframe=local_shown)
		self.local_pattern_table.updateModel(model)
		self.local_pattern_table.redraw()


	def global_description(self):

		for n in self.global_pattern_table.multiplerowlist:
			fixed_attribute = self.global_pattern_df.iloc[int(n)]['partition']
			aggregation_function=self.global_pattern_df.iloc[int(n)]['agg']
			modeltype = self.global_pattern_df.iloc[int(n)]['model']
			variable_attribute = self.global_pattern_df.iloc[int(n)]['predictor']
			Lambda = self.global_pattern_df.iloc[int(n)]['support']

		fixed_attribute=fixed_attribute.replace(",",", ")

		global_desc = "For each ("+fixed_attribute+'), the '+aggregation_function +' is '+modeltype+'\n in '+variable_attribute+'.'+\
		'This pattern holds for '+str(Lambda*100)+ ' % of the '+fixed_attribute
		desc_win = Toplevel()
		x = self.parent.winfo_x()
		y = self.parent.winfo_y()
		w = 540
		h = 120 
		desc_win.geometry("%dx%d+%d+%d" % (w, h, x + 450, y + 500))
		desc_win.wm_title("Global Pattern Description")
		desc_frame = Frame(desc_win)
		desc_frame.pack(fill=BOTH,expand=True)
		desc_label= Label(desc_frame,text=global_desc,font=('Times New Roman bold',12),borderwidth=5,relief=SOLID,justify=LEFT)
		desc_label.pack(fill=BOTH,expand=True)


	def use_local_filter_output(self):  # given partition attributes and partition values, get explanation(query on user query)
		l_filter_o_query = None

		for n in self.local_pattern_table.multiplerowlist:

			chosen_row = self.local_output_pattern_df.iloc[int(n)]
			partition_attr_list = self.local_output_pattern_df.iloc[int(n)]['partition'].split(',')
			partition_value_list = self.local_output_pattern_df.iloc[int(n)]['partition_values'].split(',')

		where_clause_list = []
		where_clause = None

		for n in range(len(partition_attr_list)):
			if(self.query_data_convert_dict[partition_attr_list[n]]=='str'):
					condition = "{} =\'{}\'".format(partition_attr_list[n],partition_value_list[n])
			elif(self.query_data_convert_dict[partition_attr_list[n]]=='float'):
				condition = "{} = {}::float".format(partition_attr_list[n],partition_value_list[n])
			else:
				condition = "{} = {}::int".format(partition_attr_list[n],partition_value_list[n])

			where_clause_list.append(condition)

		if(len(where_clause_list)==1):
			where_clause = where_clause_list[0]
		else:
			where_clause = " and ".join(where_clause_list)
				
		l_filter_o_query = "select user_query.* from user_query where "+where_clause+";"
		# logger.debug("filter_output_query:")
		# logger.debug(l_filter_o_query)
		filtered_result_df = pd.read_sql(l_filter_o_query,self.conn)

		return chosen_row,filtered_result_df


	def show_updated_output(self):

		filtered_result_df = self.use_local_filter_output()[1]
		self.query_result_df = filtered_result_df
		model = TableModel(dataframe=filtered_result_df)
		self.query_result_table.updateModel(model)
		self.query_result_table.redraw()


	def handle_question(self,direction):

		self.question_tuple = ''
		config=ExplConfig()
		config.conn = self.config.conn
		config.cur = self.config.cur
		config.query_table_name = self.cur_table_name
		eg = ExplanationGenerator(config, {'pattern_table':'dev.{}'.format(self.cur_table_name),'query_result_table':self.cur_table_name})
		eg.initialize() 
		col_name = ['Explanation_Tuple',"Score",'From_Pattern',"Drill_Down_To","Distance","Outlierness","Denominator","relevent_model","relevent_param","refinement_model","drill_param"]
		exp_df = pd.DataFrame(columns=["From_Pattern","Drill_Down_To","Score","Distance","Outlierness","Denominator","relevent_model","relevent_param","refinement_model","drill_param"])
		for n in self.query_result_table.multiplerowlist:
			self.question = self.query_result_df.iloc[[int(n)]]
			self.original_question = self.question.copy(deep=True)

			self.question.rename(columns={self.agg_name:self.user_agg}, inplace=True)
			self.question_tuple = self.query_result_df.iloc[[int(n)]]
			# logger.debug(self.question)
			self.question['direction']=direction
			self.question['lambda'] = 0.2
			question = self.question.iloc[0].to_dict()
			# logger.debug(question)
			elist = eg.do_explain_online(question)

			exp_list=[]
			for e in elist:
				tuple_list=[]
				# print(str(e.tuple_value))
				# print(str(e.tuple_value.keys()))
				# e_tuple_str = ','.join(map(str, e.tuple_value.values()))
				e_tuple_str = e.ordered_tuple_string()
				tuple_list.append(e_tuple_str)

				score = round(e.score,2)
				tuple_list.append(score)

				if e.expl_type == 1:
					local_pattern=(
						'[' + ','.join(e.relevent_pattern[0]) +\
						'=' + ','.join(list(map(str, e.relevent_pattern[1]))) +']:'+ \
						','.join(list(map(str, e.relevent_pattern[2])))+' \u2933 '+self.agg_name
						)
					relevent_model = e.relevent_pattern[4]
					if e.relevent_pattern[4] == 'const':						
						relevent_param = str(round(float(e.relevent_pattern[6].split(',')[0][1:]),2))
					else:
						# relevent_param = 'Intercept=' + str(e.relevent_pattern[7]['Intercept'])+', '+str(list(e.relevent_pattern[7])[1])+'='+str(round(e.relevent_pattern[7][list(e.relevent_pattern[7])[1]],2))
						relevent_param = e.relevent_pattern[7]

					drill_down_to = ','.join([x for x in e.refinement_pattern[0] if x not in e.relevent_pattern[0]])
					refinement_model = e.refinement_pattern[4]
					if e.refinement_pattern[4] == 'const':

						drill_param =str(round(float(e.refinement_pattern[6].split(',')[0][1:]),2))
					else:
						drill_param =e.refinement_pattern[7]
				else:
					relevent_model = e.relevent_pattern[4]
					local_pattern=(
						'[' + ','.join(e.relevent_pattern[0]) +\
						'=' + ','.join(list(map(str, e.relevent_pattern[1]))) +']:'+ \
						','.join(list(map(str, e.relevent_pattern[2])))+' \u2933 '+self.agg_name
						)
					if e.relevent_pattern[4] == 'const':
						relevent_param = str(round(float(e.relevent_pattern[6].split(',')[0][1:]),2))
					else:
						# relevent_param = 'Intercept=' + str(e.relevent_pattern[7]['Intercept'])+', '+str(list(e.relevent_pattern[7])[1])+'='+str(e.relevent_pattern[7][list(e.relevent_pattern[7])[1]])
						relevent_param = e.relevent_pattern[7]

					refinement_model = ''
					drill_down_to = ''
					drill_param = ''
				tuple_list.append(local_pattern)
				tuple_list.append(drill_down_to)
				distance = round(e.distance,2)
				tuple_list.append(distance)
				outlierness = round(e.deviation,2)
				tuple_list.append(outlierness)
				denominator = round(e.denominator,2)
				tuple_list.append(denominator)
				tuple_list.append(relevent_model)
				tuple_list.append(relevent_param)
				tuple_list.append(refinement_model)
				tuple_list.append(drill_param)
				exp_list.append(tuple_list)

			df_exp = pd.DataFrame(exp_list,columns=col_name)
			exp_df = exp_df.append(df_exp,ignore_index=True)
		
		self.exp_df = exp_df[col_name]
		model = TableModel(dataframe=self.exp_df)
		self.exp_table.updateModel(model)	
		self.exp_table.redraw()

	def handle_low(self):
		self.user_direction='low'
		self.handle_question(self.user_direction)

	def handle_high(self):
		self.user_direction='high'
		self.handle_question(self.user_direction)


	def reset_output(self):

		model = TableModel(dataframe=self.original_query_result_df)
		self.query_result_table.updateModel(model)	
		self.query_result_table.redraw()

		self.query_result_df = self.original_query_result_df


	def pop_up_pattern(self):

		chosen_row,pattern_data_df = self.use_local_filter_output()
		self.local_pattern_detail = Local_Pattern_Frame(chosen_row=chosen_row,pattern_data_df=pattern_data_df,
			agg_alias=self.agg_name,data_convert_dict=self.plot_data_convert_dict)
		
		self.local_pattern_detail.load_pattern_description()
		self.local_pattern_detail.load_pattern_graph()


	def get_pattern_result(self,partition_attr_list=None,partition_value_list=None,pred_attr_list=None):  # given partition attributes and partition values, get explanation(query on table)

		where_clause_list = []
		where_clause = None

		# logger.debug("partition_attr_list is ")
		# logger.debug(partition_attr_list)

		# logger.debug("partition_value_list is ")
		# logger.debug(partition_value_list)


		for n in range(len(partition_attr_list)):
			if(self.query_data_convert_dict[partition_attr_list[n]]=='str'):
					condition = "{} =\'{}\'".format(partition_attr_list[n],partition_value_list[n])
			elif(self.query_data_convert_dict[partition_attr_list[n]]=='float'):
				condition = "{} = {}::float".format(partition_attr_list[n],partition_value_list[n])
			else:
				condition = "{} = {}::int".format(partition_attr_list[n],partition_value_list[n])
			where_clause_list.append(condition)

		if(len(where_clause_list)==1):
			where_clause = where_clause_list[0]
		else:
			where_clause = " and ".join(where_clause_list)

		if (pred_attr_list is not None):

			Pattern_Q = "SELECT "+self.agg_function+" as "+self.agg_name+","+','.join(partition_attr_list)+","+','.join(pred_attr_list)+\
			" FROM " +self.cur_table_name+" WHERE " + where_clause+\
			" GROUP BY "+','.join(partition_attr_list)+","+','.join(pred_attr_list)
		else:
			Pattern_Q = "SELECT "+self.agg_function+" as "+self.agg_name+","+','.join(partition_attr_list)+\
			" FROM " +self.cur_table_name + " WHERE " + where_clause+\
			" GROUP BY "+','.join(partition_attr_list)


		# logger.debug("Pattern_Q")
		# logger.debug(Pattern_Q)

		exp_pattern_df = pd.read_sql(Pattern_Q,self.conn)

		# logger.debug('exp_pattern_df is :')
		# logger.debug(exp_pattern_df)

		return exp_pattern_df



	def pop_up_explanation(self):

		for n in self.exp_table.multiplerowlist:
			exp_chosen_row = self.exp_df.iloc[int(n)]
			relevent_pattern = self.exp_df.iloc[int(n)]['From_Pattern']
			rel_pattern_part = relevent_pattern.split(':')[0].split('=')[0].strip('[')
			rel_pattern_part_value = relevent_pattern.split(':')[0].split('=')[1].split(']')
			rel_pattern_pred = relevent_pattern.split(':')[1].split(' \u2933 ')[0]
			agg_name = relevent_pattern.split(':')[1].split(' \u2933 ')[1]
			rel_pattern_model = self.exp_df.iloc[int(n)]['relevent_model']
			rel_param = self.exp_df.iloc[int(n)]['relevent_param']
			rel_pattern_part_list = rel_pattern_part.split(',')
			rel_pattern_pred_list = rel_pattern_pred.split(',')
			rel_pattern_part_value_list = rel_pattern_part_value[0].split(',')
			exp_tuple = self.exp_df.iloc[int(n)]['Explanation_Tuple']
			exp_tuple_list = exp_tuple.split(',')[:-1]
			exp_tuple_score = float(self.exp_df.iloc[int(n)]['Score'])
			drill_attr_list = self.exp_df.iloc[int(n)]['Drill_Down_To'].split(',')

			if(drill_attr_list!=['']):
				exp_tuple_col = rel_pattern_part_list + rel_pattern_pred_list + drill_attr_list
				exp_tuple_col.sort()
			else:
				exp_tuple_col = rel_pattern_part_list + rel_pattern_pred_list
				exp_tuple_col.sort()


		# logger.debug('exp_tuple_col is:')
		# logger.debug(exp_tuple_col)

		# logger.debug('exp_tuple_list is:')
		# logger.debug(exp_tuple_list)


		exp_tuple_df_list = [exp_tuple_list]
		exp_tuple_df = pd.DataFrame(exp_tuple_df_list)
		logger.debug("exp_tuple_df:")
		exp_tuple_df.columns = exp_tuple_col
		logger.debug(exp_tuple_df)


		if(drill_attr_list != ['']):

			drill_values = []
			for n in drill_attr_list:
				drill_value = exp_tuple_df[n].to_string(index=False)
				drill_values.append(drill_value)

			# logger.debug('rel_pattern_part_list')
			# logger.debug(rel_pattern_part_list)

			# logger.debug('rel_pattern_part_value_list')
			# logger.debug(rel_pattern_part_value_list)


			drill_pattern_df = self.get_pattern_result(partition_attr_list=rel_pattern_part_list+drill_attr_list,
													 partition_value_list=rel_pattern_part_value_list+drill_values,pred_attr_list=rel_pattern_pred_list)

			# logger.debug("drill_pattern_df is")
			# logger.debug(drill_pattern_df)

			rel_pattern_df = self.get_pattern_result(partition_attr_list=rel_pattern_part_list,
													 partition_value_list=rel_pattern_part_value_list,pred_attr_list=rel_pattern_pred_list)

			question_df = self.original_question

			explanation_df = self.get_pattern_result(partition_attr_list=exp_tuple_col,
													 partition_value_list=exp_tuple_list,pred_attr_list=None)
			logger.debug(explanation_df)
			exp_selected = exp_chosen_row

			data_convert_dict = self.plot_data_convert_dict

			self.Explainer = Exp_Frame(input_question_df=question_df, input_explanation_df=explanation_df, input_exp_chosen_row=exp_selected, input_none_drill_down_df=rel_pattern_df,
				input_drill_down_df=drill_pattern_df, input_data_convert_dict=data_convert_dict)

			self.Explainer.load_exp_graph()
			self.Explainer.load_exp_description(user_direction=self.user_direction)

		else:
			rel_pattern_df = self.get_pattern_result(partition_attr_list=rel_pattern_part_list,
														 partition_value_list=rel_pattern_part_value_list,pred_attr_list=rel_pattern_pred_list)

			question_df = self.original_question

			explanation_df = self.get_pattern_result(partition_attr_list=exp_tuple_col,
													 partition_value_list=exp_tuple_list,pred_attr_list=None)
			exp_selected = exp_chosen_row

			data_convert_dict = self.plot_data_convert_dict

			self.Explainer = Exp_Frame(input_question_df=question_df, input_explanation_df=explanation_df, input_exp_chosen_row=exp_selected, input_none_drill_down_df=rel_pattern_df,
				input_drill_down_df=None, input_data_convert_dict=data_convert_dict)

			self.Explainer.load_exp_graph()
			self.Explainer.load_exp_description(user_direction=self.user_direction)

def startCapeGUI(conn,config):
	root = Tk()
	root.title('CAPE')
	default_font = nametofont("TkTextFont")
	default_font.configure(size=12)
	bigfont = Font(family="Helvetica",size=12)
	root.option_add('*TCombobox*Listbox.font',bigfont)
	root.option_add('*TCombobox*Listbox.selectBackground', 'wheat1')
	width, height = root.winfo_screenwidth(), root.winfo_screenheight()
	root.geometry('%dx%d+0+0' % (width,height))
	ui = CAPE_UI(root,conn=conn,config=config)
	root.mainloop()


def main():

	config=DictLike()
	dbconn=DBConnection(host="127.0.0.1",user="antiprov",db="antiprov",password='1234',port="5432")
	conn=dbconn.pgconnect()
	startCapeGUI(conn=conn,config=config)

if __name__ == '__main__':
	main()




