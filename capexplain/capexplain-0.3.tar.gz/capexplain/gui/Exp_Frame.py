import tkinter as tk
from tkinter import *
from tkinter import ttk
import tkinter.messagebox
from tkinter import filedialog
from tkinter import font
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
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from capexplain.gui.Plotting import Plotter
import logging
import textwrap
import copy

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s line %(lineno)d: %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)



class Exp_Frame:

	def __init__(self,input_question_df=None, input_explanation_df=None, input_exp_chosen_row=None, input_none_drill_down_df=None, input_drill_down_df=None, input_data_convert_dict=None):

		self.win = Toplevel()
		self.win.geometry("%dx%d%+d%+d" % (1580, 900, 250, 125))
		self.win.wm_title("Explanation Detail")		
		self.win_frame = Frame(self.win)
		self.win_frame.pack(fill=BOTH,expand=True)

		self.question_df = input_question_df
		self.explanation_df = input_explanation_df
		self.exp_chosen_row = input_exp_chosen_row
		self.none_drill_down_df = input_none_drill_down_df

		# print("self.question_df type-----------------")
		# print(self.question_df.dtypes)

		# print("self.explanation_df type-----------------")
		# print(self.explanation_df.dtypes)

		# print("self.exp_chosen_row type-----------------")
		# print(self.exp_chosen_row.dtypes)

		# print("self.none_drill_down_df type-----------------")
		# print(self.none_drill_down_df.dtypes)


		if(input_drill_down_df is not None):
			self.drill_down_df = input_drill_down_df.astype(object)
			# print("self.drill_down_df type-----------------")
			# print(self.drill_down_df.dtypes)
		else:
			self.drill_down_df = None
		self.data_convert_dict=input_data_convert_dict
		self.drill_exist=False

		self.relevent_pattern = self.exp_chosen_row['From_Pattern']
		self.rel_pattern_part = self.relevent_pattern.split(':')[0].split('=')[0].strip('[')
		self.rel_pattern_pred = self.relevent_pattern.split(':')[1].split(' \u2933 ')[0]
		self.rel_pattern_agg = self.relevent_pattern.split(':')[1].split(' \u2933 ')[1]
		self.rel_pattern_part_value = self.relevent_pattern.split(':')[0].split('=')[1].strip(']')
		self.rel_pattern_pred_list = self.rel_pattern_pred.split(',')
		self.rel_pattern_model = self.exp_chosen_row['relevent_model']
		self.rel_param = self.exp_chosen_row['relevent_param']
		self.rel_pattern_part_list = self.rel_pattern_part.split(',')
		self.rel_pattern_pred_list = self.rel_pattern_pred.split(',')
		self.exp_tuple_score = float(self.exp_chosen_row['Score'])
		self.drill_attr = [self.exp_chosen_row['Drill_Down_To'].split(',')]
		self.drill_model = self.exp_chosen_row['refinement_model']
		self.drill_param = self.exp_chosen_row['drill_param']


	# configure the frame structure according the exp type

		if(self.drill_down_df is None):

			self.win_frame.columnconfigure(0,weight=2)
			self.win_frame.columnconfigure(1,weight=3)
			self.win_frame.rowconfigure(0,weight=8)
			self.win_frame.rowconfigure(1,weight=1)

			self.Quit_Button = Button(self.win_frame, text="Quit",width=10, height=4, command=self.win.destroy)
			self.Quit_Button.grid(column=0,row=1)

			self.rel_graph_frame = Frame(self.win_frame,borderwidth=5,relief=RIDGE,bg='white')
			self.rel_graph_frame.grid(column=1,row=0,rowspan=2,sticky='nesw')

			self.exp_frame = Frame(self.win_frame,borderwidth=5,relief=RIDGE,bg='white')
			self.exp_frame.grid(column=0,row=0,sticky='nesw')

			self.rel_figure = Figure(figsize=(5,5),dpi=130)

			self.rel_canvas = FigureCanvasTkAgg(self.rel_figure,self.rel_graph_frame)
			self.rel_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
			self.rel_toolbar = NavigationToolbar2Tk(self.rel_canvas,self.rel_graph_frame)
			self.rel_toolbar.update()
			self.rel_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
		
		else:

			self.drill_exist = True
			self.win_frame.columnconfigure(0,weight=1)
			self.win_frame.columnconfigure(1,weight=1)
			self.win_frame.rowconfigure(0,weight=2)
			self.win_frame.rowconfigure(1,weight=1)

			self.rel_graph_frame = Frame(self.win_frame,borderwidth=5,relief=RIDGE,bg='white')
			self.rel_graph_frame.grid(column=0,row=0,sticky='nesw')

			self.drill_graph_frame = Frame(self.win_frame,borderwidth=5,relief=RIDGE,bg='white')
			self.drill_graph_frame.grid(column=1,row=0,sticky='nesw')

			self.rel_figure = Figure(figsize=(5,5),dpi=130)
			self.rel_canvas = FigureCanvasTkAgg(self.rel_figure,self.rel_graph_frame)
			self.rel_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
			self.rel_toolbar = NavigationToolbar2Tk(self.rel_canvas,self.rel_graph_frame)
			self.rel_toolbar.update()
			self.rel_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

			self.drill_figure = Figure(figsize=(5,5),dpi=130)
			self.drill_canvas = FigureCanvasTkAgg(self.drill_figure,self.drill_graph_frame)
			self.drill_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
			self.drill_toolbar = NavigationToolbar2Tk(self.drill_canvas,self.drill_graph_frame)
			self.drill_toolbar.update()
			self.drill_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

			self.exp_frame = Frame(self.win_frame,borderwidth=5,relief=RIDGE,bg='white')
			self.exp_frame.grid(column=0,columnspan=2,row=1,sticky='nesw')


	def load_exp_graph(self):

		if(self.drill_exist==False):
			self.load_rel_exp_graph()
		else:
			self.load_rel_question_graph()
			self.load_drill_exp_graph()



	def load_rel_exp_graph(self):

		if(len(self.none_drill_down_df)>=50):

			self.text_plotter = Plotter(figure=self.rel_figure,data_convert_dict=self.data_convert_dict,mode='2D')
			self.rel_plotter.add_text("Cannot plot because the size of the data is so large!")


		elif(len(self.rel_pattern_pred_list)>2):

			self.text_plotter = Plotter(figure=self.rel_figure,data_convert_dict=self.data_convert_dict,mode='2D')
			self.rel_plotter.add_text("Cannot plot because the number of dimension of data is higher than 2!")


		elif(self.rel_pattern_model=='const'):

			if(len(self.rel_pattern_pred_list)==1):
				self.rel_plotter = Plotter(figure=self.rel_figure,data_convert_dict=self.data_convert_dict,mode='2D')
				const=round(float(self.rel_param),2)

				x=self.rel_pattern_pred_list[0]
				y=self.rel_pattern_agg

				self.rel_plotter.plot_2D_const(const,label='Explanation Model')
				# self.rel_plotter.plot_categorical_scatter_2D(x,y)
				none_drill_down_df = copy.deepcopy(self.none_drill_down_df[[x,y]])
				# logger.debug(none_drill_down_df)

				common_cols = self.rel_pattern_part_list + self.rel_pattern_pred_list

				# logger.debug("common_cols for question is ")
				# print(common_cols)

				# logger.debug("self.explanation_df is")
				# logger.debug(self.explanation_df)

				question_df = pd.merge(self.none_drill_down_df,self.question_df,on=common_cols)

				explanation_df = pd.merge(self.none_drill_down_df,self.explanation_df,on=common_cols)

				# logger.debug("question_df is ")
				# print(question_df)


				question_df = question_df.rename(index=str, columns={(y+"_x"): y,(x+"_x"):x})
				question_df = question_df[[x,y]]

				explanation_df = explanation_df.rename(index=str, columns={(y+"_x"): y,(x+"_x"):x})
				explanation_df = explanation_df[[x,y]]

				self.rel_plotter.plot_2D_scatter(question_df,x=x,y=y,color='r',marker='v',size=250,zorder=10,label="User Question")
				self.rel_plotter.plot_2D_scatter(explanation_df,x=x,y=y,color='b',marker='^',size=250,zorder=5,label="Explanation")
				self.rel_plotter.plot_2D_scatter(none_drill_down_df,x=x,y=y,zorder=0,label=self.rel_pattern_agg)
				self.rel_plotter.set_x_label(x)
				self.rel_plotter.set_y_label(y)
				self.rel_plotter.set_title("Pattern Graph")
		
			else:

				self.rel_plotter = Plotter(figure=self.rel_figure,data_convert_dict=self.data_convert_dict,mode='3D')

				x = self.rel_pattern_pred_list[0]
				y = self.rel_pattern_pred_list[1]
				z = self.rel_pattern_agg

				const = round(self.rel_param,2)

				none_drill_down_df = copy.deepcopy(self.none_drill_down_df[[x,y,z]])
				# logger.debug(none_drill_down_df)

				common_cols = self.rel_pattern_part_list + self.rel_pattern_pred_list

				# logger.debug("common_cols for question is ")
				# print(common_cols)

				# logger.debug("self.explanation_df is")
				# logger.debug(self.explanation_df)

				question_df = pd.merge(self.none_drill_down_df,self.question_df,on=common_cols)

				explanation_df = pd.merge(self.none_drill_down_df,self.explanation_df,on=common_cols)

				# logger.debug("question_df is ")
				# print(question_df)

				question_df = question_df.rename(index=str, columns={(y+"_x"): y,(x+"_x"):x,(z+"_x"):z})
				question_df = question_df[[x,y,z]]

				explanation_df = explanation_df.rename(index=str, columns={(y+"_x"): y,(z+"_x"):z})
				explanation_df = explanation_df[[x,y,z]]


				pattern_only_df = pd.concat([none_drill_down_df,question_df,explanation_df]).drop_duplicates(keep=False)

				self.rel_plotter.plot_3D_const(none_drill_down_df,x=x,y=y,z_value=const,label="Explanation Model")
				self.rel_plotter.plot_3D_scatter(none_drill_down_df,x=x,y=y,z=z,alpha=0)
				self.rel_plotter.plot_3D_scatter(pattern_only_df,x=x,y=y,z=z,label=self.rel_pattern_agg)
				self.rel_plotter.plot_3D_scatter(question_df,x=x,y=y,z=z,color='r',marker='v',size=250,label="User Question")
				self.rel_plotter.plot_3D_scatter(explanation_df,x=x,y=y,z=z,color='b',marker='^',size=250,label="Explanation")

				self.rel_plotter.set_x_label(x)
				self.rel_plotter.set_y_label(y)
				self.rel_plotter.set_z_label(z)
				self.rel_plotter.set_title("Pattern Graph")

		elif(self.rel_pattern_model=='linear'):
			if(len(self.rel_pattern_pred_list)==1):

				self.rel_plotter = Plotter(figure=self.rel_figure,data_convert_dict=self.data_convert_dict,mode='2D')
				x = self.rel_pattern_pred_list[0]
				y = self.rel_pattern_agg

				intercept_value = self.rel_param['Intercept']
				slope_name = list(self.rel_param)[1]
				slope_value = float(self.rel_param[slope_name])

				draw_line_df = copy.deepcopy(self.none_drill_down_df[[x]])

				none_drill_down_df = copy.deepcopy(self.none_drill_down_df[[x,y]])

				common_cols = self.rel_pattern_part_list + self.rel_pattern_pred_list

				# logger.debug("common_cols for question is ")
				# print(common_cols)

				# logger.debug("self.explanation_df is")
				# logger.debug(self.explanation_df)

				question_df = pd.merge(self.none_drill_down_df,self.question_df,on=common_cols)

				explanation_df = pd.merge(self.none_drill_down_df,self.explanation_df,on=common_cols)

				# logger.debug("question_df is ")
				# print(question_df)


				question_df = question_df.rename(index=str, columns={(y+"_x"): y,(x+"_x"):x})
				question_df = question_df[[x,y]]

				explanation_df = explanation_df.rename(index=str, columns={(y+"_x"): y,(x+"_x"):x})
				explanation_df = explanation_df[[x,y]]

				self.rel_plotter.plot_2D_linear(draw_line_df,slope=slope_value,intercept=intercept_value,label="Explanation Model")
				self.rel_plotter.plot_2D_scatter(none_drill_down_df,x=x,y=y,label=self.rel_pattern_agg)
				self.rel_plotter.plot_2D_scatter(question_df,x=x,y=y,color='r',marker='v',size=250,zorder=1,label="User Question")
				self.rel_plotter.plot_2D_scatter(explanation_df,x=x,y=y,color='b',marker='^',size=250,zorder=2,label="Explanation")
				self.rel_plotter.set_x_label(x)
				self.rel_plotter.set_y_label(y)
				self.rel_plotter.set_title("Pattern Graph")

		self.rel_canvas.draw()


	def load_rel_question_graph(self):

		if(len(self.none_drill_down_df)>=50):

			self.text_plotter = Plotter(figure=self.drill_figure,data_convert_dict=self.data_convert_dict,mode='2D')
			self.rel_plotter.add_text("Cannot plot because the size of the data is so large!")


		elif(len(self.rel_pattern_pred_list)>2):
			
			self.text_plotter = Plotter(figure=self.drill_figure,data_convert_dict=self.data_convert_dict,mode='2D')
			self.rel_plotter.add_text("Cannot plot because the dimension of the data is higher than 2!")


		elif(self.rel_pattern_model=='const'):
			if(len(self.rel_pattern_pred_list)==1):
				self.rel_plotter = Plotter(figure=self.rel_figure,data_convert_dict=self.data_convert_dict,mode='2D')
				const=round(float(self.rel_param),2)

				x=self.rel_pattern_pred_list[0]
				y=self.rel_pattern_agg

				self.rel_plotter.plot_2D_const(const)
				# self.rel_plotter.plot_categorical_scatter_2D(x,y)

				common_cols = self.rel_pattern_part_list + self.rel_pattern_pred_list

				# logger.debug("common_cols for question is ")
				# print(common_cols)

				# logger.debug("self.explanation_df is")
				# logger.debug(self.explanation_df)

				question_df = pd.merge(self.none_drill_down_df,self.question_df,on=common_cols)

				explanation_df = pd.merge(self.none_drill_down_df,self.explanation_df,on=common_cols)

				# logger.debug("question_df is ")
				# print(question_df)


				question_df = question_df.rename(index=str, columns={(y+"_x"): y,(x+"_x"):x})
				question_df = question_df[[x,y]]

				explanation_df = explanation_df.rename(index=str, columns={(y+"_x"): y,(x+"_x"):x})
				explanation_df = explanation_df[[x,y]]

				# logger.debug(question_df)

				self.rel_plotter.plot_2D_scatter(question_df,x=x,y=y,color='r',marker='v',size=250,zorder=10,label="User Question")
				self.rel_plotter.plot_2D_scatter(copy.deepcopy(self.none_drill_down_df),x=x,y=y,zorder=0,label=self.rel_pattern_agg)
				self.rel_plotter.plot_2D_scatter(explanation_df,x=x,y=y,color='b',marker='^',size=250,zorder=0,label="Explanation")
				self.rel_plotter.set_x_label(x)
				self.rel_plotter.set_y_label(y)
				self.rel_plotter.set_title("User Question Graph")
		
			else:


				pass

				# self.rel_plotter = Plotter(figure=self.rel_figure,data_convert_dict=self.data_convert_dict,mode='3D')

				# x = self.rel_pattern_pred_list[0]
				# y = self.rel_pattern_pred_list[1]
				# z = self.rel_pattern_agg

				# const = round(float(self.rel_param),2)

				# none_drill_down_df = self.none_drill_down_df[[x,y,z]]
				# logger.debug(none_drill_down_df)

				# question_df = self.question_df[[x,y,z]]
				# logger.debug(question_df)


				# pattern_only_df = pd.concat([none_drill_down_df,question_df]).drop_duplicates(keep=False)

				# self.rel_plotter.plot_3D_const(none_drill_down_df,x=x,y=y,z_value=const)
				# self.rel_plotter.plot_3D_scatter(none_drill_down_df,x=x,y=y,z=z,alpha=0)
				# self.rel_plotter.plot_3D_scatter(pattern_only_df,x=x,y=y,z=z)
				# self.rel_plotter.plot_3D_scatter(question_df,x=x,y=y,z=z,color='b',marker='s',size=200)

				# self.rel_plotter.set_x_label(x)
				# self.rel_plotter.set_y_label(y)
				# self.rel_plotter.set_z_label(z)
				# self.rel_plotter.set_title("User Question Graph")

		elif(self.rel_pattern_model=='linear'):
			if(len(self.rel_pattern_pred_list)==1):

				self.rel_plotter = Plotter(figure=self.rel_figure,data_convert_dict=self.data_convert_dict,mode='2D')
				x = self.rel_pattern_pred_list[0]
				y = self.rel_pattern_agg

				intercept_value = self.rel_param['Intercept']
				slope_name = list(self.rel_param)[1]
				slope_value = float(self.rel_param[slope_name])

				draw_line_df = self.none_drill_down_df[[x]]

				common_cols = self.rel_pattern_part_list+ self.rel_pattern_pred_list
				question_df = pd.merge(self.none_drill_down_df,self.question_df,on=common_cols)
				logger.debug(self.none_drill_down_df)
				logger.debug(self.explanation_df)
				explanation_df = pd.merge(self.none_drill_down_df,self.explanation_df,on=common_cols)

				# logger.debug("question_df is ")
				# print(question_df)


				question_df = question_df.rename(index=str, columns={(y+"_x"): y,(x+"_x"):x})
				question_df = question_df[[x,y]]
				logger.debug(question_df)

				explanation_df = explanation_df.rename(index=str, columns={(y+"_x"): y,(x+"_x"):x})
				explanation_df = explanation_df[[x,y]]
				logger.debug(explanation_df)

				self.rel_plotter.plot_2D_linear(draw_line_df,slope=slope_value,intercept=intercept_value,label="Relevent Model")
				self.rel_plotter.plot_2D_scatter(copy.deepcopy(self.none_drill_down_df),x=x,y=y,label=self.rel_pattern_agg)
				self.rel_plotter.plot_2D_scatter(question_df,x=x,y=y,color='r',marker='v',size=150,zorder=1,label="User Question")
				logger.debug(explanation_df)
				self.rel_plotter.plot_2D_scatter(explanation_df,x=x,y=y,color='b',marker='^',size=150,zorder=0,label="Explanation")

				self.rel_plotter.set_x_label(x)
				self.rel_plotter.set_y_label(y)
				self.rel_plotter.set_title("User Question Graph")

		self.rel_canvas.draw()

	def load_drill_exp_graph(self):

		if(len(self.none_drill_down_df)>=50):
			self.drill_plotter.add_text("Cannot plot because the size of the data is so large!")

		elif(len(self.rel_pattern_pred_list)>2):
			self.drill_plotter.add_text("Cannot plot because the number of dimension of data is higher than 2!")

		if(self.drill_model=='const'):

			if(len(self.drill_attr)==1):
				self.drill_plotter = Plotter(figure=self.drill_figure,data_convert_dict=self.data_convert_dict,mode='2D')
				const=round(float(self.drill_param),2)

				x=self.rel_pattern_pred_list[0]
				y=self.rel_pattern_agg

				self.drill_plotter.plot_2D_const(const,label="Refined Explanation Model")
				# self.drill_plotter.plot_categorical_scatter_2D(x,y)

				common_cols = self.rel_pattern_part_list+ self.drill_attr+self.rel_pattern_pred_list


				self.drill_plotter.plot_2D_scatter(copy.deepcopy(self.explanation_df),x=x,y=y,color='b',marker='^',size=250,zorder=10,label="Explanation")
				logger.debug("After Drilldown explanation:")
				logger.debug(self.drill_plotter.x_max)
				logger.debug(self.drill_plotter.x_min)
				logger.debug(self.drill_plotter.y_max)
				logger.debug(self.drill_plotter.y_min)
				self.drill_plotter.plot_2D_scatter(copy.deepcopy(self.drill_down_df),x=x,y=y,zorder=0,label=self.rel_pattern_agg)
				logger.debug(copy.deepcopy(self.drill_down_df))
				logger.debug("After Drilldown scatters:")
				logger.debug(self.drill_plotter.x_max)
				logger.debug(self.drill_plotter.x_min)
				logger.debug(self.drill_plotter.y_max)
				logger.debug(self.drill_plotter.y_min)
				self.drill_plotter.set_x_label(x)
				self.drill_plotter.set_y_label(y)
				self.drill_plotter.set_title("Refined Pattern Explanation")
		
			else:
				pass

				# self.drill_plotter = Plotter(figure=self.drill_figure,data_convert_dict=self.data_convert_dict,mode='3D')

				# x = self.rel_pattern_pred_list[0]
				# y = self.rel_pattern_pred_list[1]
				# z = self.rel_pattern_agg

				# const = round(float(self.drill_param),2)

				# drill_down_df = self.drill_down_df[[x,y,z]]
				# logger.debug(drill_down_df)

				# explanation_df = self.explanation_df[[x,y,z]]
				# logger.debug(explanation_df)


				# pattern_only_df = pd.concat([drill_down_df,explanation_df]).drop_duplicates(keep=False)

				# self.drill_plotter.plot_3D_const(drill_down_df,x=x,y=y,z_value=const)
				# self.drill_plotter.plot_3D_scatter(drill_down_df,x=x,y=y,z=z,alpha=0)
				# self.drill_plotter.plot_3D_scatter(pattern_only_df,x=x,y=y,z=z)
				# self.drill_plotter.plot_3D_scatter(explanation_df,x=x,y=y,z=z,color='b',marker='s',size=200,label='Explanation')

				# self.drill_plotter.set_x_label(x)
				# self.drill_plotter.set_y_label(y)
				# self.drill_plotter.set_z_label(z)
				# self.drill_plotter.set_title("Pattern Graph")

				# self.drill_canvas.draw()


		elif(self.drill_model=='linear'):

			if(len(self.drill_attr)==1):
				self.drill_plotter = Plotter(figure=self.drill_figure,data_convert_dict=self.data_convert_dict,mode='2D')
				x = self.drill_attr[0]
				y = self.rel_pattern_agg

				intercept_value = self.drill_param['Intercept']
				slope_name = list(self.drill_param)[1]
				slope_value = float(self.drill_param[slope_name])

				draw_line_df = self.none_drill_down_df[[x]]

				common_cols = self.rel_pattern_part_list+self.drill_attr

				explanation_df = pd.merge(self.drill_down_df,self.explanation_df,on=common_cols)

				explanation_df = explanation_df.rename(index=str, columns={(y+"_x"): y,(x+"_x"):x})

				explanation_df = explanation_df[[x,y]]

				# logger.debug(explanation_df)
				self.drill_plotter.plot_2D_linear(draw_line_df,slope=slope_value,intercept=intercept_value)
				self.drill_plotter.plot_2D_scatter(copy.deepcopy(self.drill_down_df)	,x=x,y=y)
				self.drill_plotter.plot_2D_scatter(explanation_df,x=x,y=y,zorder=1)
				self.drill_plotter.set_x_label(x)
				self.drill_plotter.set_y_label(y)
				self.drill_plotter.set_title("Pattern Graph")

		self.drill_canvas.draw()

	def load_exp_description(self,user_direction=None):

		exp_tuple_score = float(self.exp_chosen_row['Score'])

		likelihood_words = []

		if(exp_tuple_score<=0):
			likelihood_words = ['unlikely','not similar','slighlty']
		elif(exp_tuple_score<=10):
			likelihood_words = ['plausible','somewhat similar','']
		else:
			likelihood_words = ['highly plausible','similar','extremly']

		ranking_clause = "  This explanation was ranked "+likelihood_words[0] + " because the counterbalance is " + likelihood_words[1]+" to the user question and it deviates "+likelihood_words[2]+" from the predicted outcome."

		# logger.debug('ranking_clause:')
		# logger.debug(ranking_clause)

		# logger.debug('self.question_df is:')
		# logger.debug(self.question_df)

		user_question_list = []
		# logger.debug('question_df.items()')
		# logger.debug(self.question_df.items())

		for k,v in self.question_df.items():
			if(k==self.rel_pattern_agg):
				continue
			else:
				user_question_list.append(str(k)+"="+str(v.to_string(index=False)))
		user_question_clause = ',\n  '.join(user_question_list)
		# logger.debug("user_question_list")
		# logger.debug(user_question_clause)

		predict = '' 
		if(len(self.rel_pattern_pred_list)>1):
			predict = 'predict'
		else:
			predict = 'predicts'	

		fixed_pair_list=[]
		rel_pattern_part_value_list = self.rel_pattern_part_value.split(",")

		for n in range(len(self.rel_pattern_part_list)):
			eq = (self.rel_pattern_part_list[n]+"="+rel_pattern_part_value_list[n])
			fixed_pair_list.append(eq)
		if(len(fixed_pair_list)==1):
			fixed_pair = fixed_pair_list[0]
		else:
			fixed_pair = ",".join(fixed_pair_list)

		variable_pair_list=[]
		variable_attr_list = self.rel_pattern_pred_list

		for n in range(len(variable_attr_list)):
			eq = (str(variable_attr_list[n])+"="+str(self.question_df[variable_attr_list[n]].to_string(index=False)))
			variable_pair_list.append(eq)
		if(len(variable_pair_list)==1):
			variable_pair = variable_pair_list[0]
		else:
			variable_pair = ",".join(variable_pair_list)

		counter_dir = ''


		if(user_direction=='high'):
			counter_dir='low'
		else:
			counter_dir='high'


		# logger.debug('counter_dir:')
		# logger.debug(counter_dir)

		exp_tuple_dict = self.explanation_df.to_dict('records')[0]

		exp_list = []
		for k,v in exp_tuple_dict.items():
			if(k==self.rel_pattern_agg or k in self.rel_pattern_part.split(',')):
				continue
			else:
				exp_list.append(str(k)+"="+str(v))
		exp_clause = ','.join(exp_list)

		# logger.debug('exp_clause:')
		# logger.debug(exp_clause)


		# logger.debug('exp_tuple_dict.items()')
		# logger.debug(exp_tuple_dict.items())

		if(self.drill_down_df is None):

			comprehensive_exp = """Explanation for why {} is {}er than expected for: {}. In general, {} {} {}  for most {}. This is also true for {}. However, for {}, {} is {}er than predicted. This may be explained through the {}er than expected outcome for {}.
			""".format(self.rel_pattern_agg,user_direction,user_question_clause,
				str(self.rel_pattern_pred),predict,self.rel_pattern_agg,str(self.rel_pattern_part),fixed_pair,
				variable_pair,self.rel_pattern_agg,user_direction,counter_dir,exp_clause)

			raw_exp = ranking_clause+comprehensive_exp
			raw_exp_lists = textwrap.wrap(raw_exp,width=50)
			final_exp_lists = '\n'.join(raw_exp_lists)

		else:

			drill_pair_list=[]
			for n in range(len(self.drill_attr)):
				eq = (str(self.drill_attr[n])+"="+str(self.explanation_df[self.drill_attr[n]].to_string(index=False)))
				drill_pair_list.append(eq)
			if(len(drill_pair_list)==1):
				drill_pair = drill_pair_list[0]
			else:
				drill_pair = ",".join(drill_pair_list)

			user_question_clause = ','.join(user_question_list)

			comprehensive_exp = """ Explanation for why {} is {}er than expected for: {}.Even though like many other {}, {} {} {} for {}(Left Graph), the fact that  {} is {} can also be explained by \n{}er than usual number of {} in {}(Right Graph).
			""".format(self.rel_pattern_agg,user_direction,user_question_clause,
				str(self.rel_pattern_part),str(self.rel_pattern_pred),predict,self.rel_pattern_agg,
				fixed_pair,user_question_clause,user_direction,
				counter_dir,self.rel_pattern_agg,exp_clause)


			raw_exp = ranking_clause+comprehensive_exp
			raw_exp_lists = textwrap.wrap(raw_exp,width=90)
			final_exp_lists = '\n'.join(raw_exp_lists)

		final_exp_lists = final_exp_lists.replace('name','author')
		final_exp_lists = final_exp_lists.replace('\'','')



		pattern_description = Label(self.exp_frame,text=final_exp_lists,font=('Times New Roman bold',19),bg='white',relief=SOLID,justify=LEFT)
		pattern_description.pack(expand=True)




def main():
	
	relevent_pattern_df = pd.DataFrame({'name':['Boris Glavic','Boris Glavic','Boris Glavic','Boris Glavic'],'venue':['sigmod','vldb','kdd','icde'],'year':['2013','2014','2016','2018'],'pubcount':[5,4,3,10]})

	drill_down_df = pd.DataFrame({'name':['Boris Glavic','Boris Glavic','Boris Glavic','Boris Glavic'],'year':['2013','2014','2016','2018'],'venue':['sigmod','vldb','kdd','icde'],'pubcount':[5,4,1,7]})
	question_df = pd.DataFrame({'name':['Boris Glavic'],'venue':['icde'],'year':['2018'],'pubcount':[10]})
	explanation_df = pd.DataFrame({'name':['Boris Glavic'],'venue':['kdd'],'year':['2016'],'pubcount':[1]})

	exp_chosen_row = pd.DataFrame({'Explanation_Tuple':['Boris Glavic,kdd,2016,3'],'Score':[7.34],
		'From_Pattern':['[name=Boris Glavic]:year \u2933 pubcount'],'Drill_Down_To':['venue'],'Distance':[11.36],
		'Outlierness':[0],'Denominator':[-0.83],'relevent_model':['const'],'relevent_param':[4.5],'refinement_model':['const'],
		'drill_param':[3.2]})

	data_type_dict = {'name': 'str', 'venue': 'str', 'year': 'numeric', 'pubcount': 'numeric'}


	root = Tk()

	exp_frame_1 = Exp_Frame(question_df=question_df, explanation_df=explanation_df, exp_chosen_row=exp_chosen_row, none_drill_down_df=relevent_pattern_df,
		drill_down_df=drill_down_df, data_convert_dict=data_type_dict)

	exp_frame_1.load_exp_graph()

	root.mainloop()
	
if __name__ == '__main__':
	main()

