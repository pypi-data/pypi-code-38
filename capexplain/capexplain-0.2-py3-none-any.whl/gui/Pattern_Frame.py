import pandas as pd
import psycopg2
import tkinter as tk
from tkinter import *
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from capexplain.gui.Plotting import Plotter
import logging
import textwrap


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s line %(lineno)d: %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class Local_Pattern_Frame:

	def __init__(self,chosen_row=None,pattern_data_df=None,agg_alias=None,data_convert_dict=None):

		self.chosen_row = chosen_row
		self.pattern_data_df = pattern_data_df
		self.agg_alias = agg_alias
		self.data_convert_dict = data_convert_dict

		self.pop_up_frame = Toplevel()
		self.pop_up_frame.geometry("%dx%d%+d%+d" % (1200, 800, 250, 125))
		self.pop_up_frame.wm_title("Pattern Detail")

		self.win_frame = Frame(self.pop_up_frame)
		self.win_frame.pack(fill=BOTH,expand=True)
		self.win_frame.columnconfigure(0,weight=1)
		self.win_frame.columnconfigure(1,weight=3)
		self.win_frame.rowconfigure(0,weight=1)


	def load_pattern_graph(self):

		graph_frame = Frame(self.win_frame)
		graph_frame.grid(column=1,row=0,sticky='nesw')
		self.figure = Figure(figsize=(5,5),dpi=130)
		canvas = FigureCanvasTkAgg(self.figure,graph_frame)
		canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
		toolbar = NavigationToolbar2Tk(canvas,graph_frame)
		toolbar.update()
		canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

		if(len(self.pattern_data_df)>=50):
			self.text_plotter = Plotter(figure=self.figure,data_convert_dict=self.data_convert_dict,mode='2D')
			self.text_plotter.add_text("Cannot plot because the size of the data is so large!")

		elif(len(self.chosen_row['variable'])>2):
			self.text_plotter = Plotter(figure=self.figure,data_convert_dict=self.data_convert_dict,mode='2D')
			self.text_plotter.add_text("Cannot plot because the number of dimension of data is higher than 2!")

		elif(self.chosen_row['model']=='const'):
			if(len(self.chosen_row['variable'])==1):
				self.plotter = Plotter(figure=self.figure,data_convert_dict=self.data_convert_dict,mode='2D')
				variable_name= self.chosen_row['variable'][0]
				const=round(self.chosen_row['stats'],2)
				self.plotter.plot_2D_const(const,label="Pattern Model")
				draw_df = self.pattern_data_df[[variable_name,self.agg_alias]]
				logger.debug(draw_df)

				self.plotter.plot_2D_scatter(draw_df,x=variable_name,y=self.agg_alias,label=self.agg_alias)
				self.plotter.set_x_label(variable_name)
				self.plotter.set_y_label(self.agg_alias)
				self.plotter.set_title("Pattern Graph")
		
			else:

				self.plotter = Plotter(figure=self.figure,data_convert_dict=self.data_convert_dict,mode='3D')
				x_name = self.chosen_row['variable'][0]
				y_name = self.chosen_row['variable'][1]
				const = self.chosen_row['stats']
				draw_const_df = self.pattern_data_df[[x_name,y_name]]
				draw_scatter_df = self.pattern_data_df[[x_name,y_name,self.agg_alias]]
				self.plotter.plot_3D_const(draw_const_df,x=x_name,y=y_name,z_value=const,label="Pattern Model")
				self.plotter.plot_3D_scatter(draw_scatter_df,x=x_name,y=y_name,z=self.agg_alias,label=self.agg_alias)
				self.plotter.set_x_label(x_name)
				self.plotter.set_y_label(y_name)
				self.plotter.set_z_label(self.agg_alias)
				self.plotter.set_title("Pattern Graph")

		elif(self.chosen_row['model']=='linear'):
			if(len(self.chosen_row['variable'])==1):

				self.plotter = Plotter(figure=self.figure,data_convert_dict=self.data_convert_dict,mode='2D')
				variable_name = self.chosen_row['variable'][0]
				intercept_value = self.chosen_row['param']['Intercept']
				slope_name = list(self.chosen_row['param'])[1]
				slope_value = float(self.chosen_row['param'][slope_name])

				draw_line_df = self.pattern_data_df[[variable_name]]
				draw_scatter_df = self.pattern_data_df[[variable_name,self.agg_alias]]
				self.plotter.plot_2D_linear(draw_line_df,slope=slope_value,intercept=intercept_value,label="Pattern Model")
				self.plotter.plot_2D_scatter(draw_scatter_df,x=variable_name,y=self.agg_alias,label=self.agg_alias)
				self.plotter.set_x_label(variable_name)
				self.plotter.set_y_label(self.agg_alias)
				self.plotter.set_title("Pattern Graph")

		canvas.draw()


	def load_pattern_description(self):

		fixed_attribute = self.chosen_row['fixed']
		fixed_value = self.chosen_row['fixed_value']
		if(len(fixed_attribute)==1):
			fixed_clause=fixed_attribute[0]+' = '+fixed_value[0]
		else:
			pairs = []
			for n in range(len(fixed_attribute)):
				pair = str(fixed_attribute[n])+' = '+str(fixed_value[n])
				pairs.append(pair)
			fixed_clause=',\n'.join(pairs)
		aggregation_function=self.chosen_row['agg']
		modeltype = self.chosen_row['model']
		variable_attribute = self.chosen_row['variable']
		if(len(variable_attribute)==1):
			variable_attribute=variable_attribute[0]
		else:
			variable_attribute=','.join(variable_attribute)
		if(self.chosen_row['model']=='const'):
			pass
			model_str = "\n"
		else:
			Intercept_value = round((self.chosen_row['param']['Intercept']),2)
			slope_name = list(self.chosen_row['param'])[1]
			slope_value = round((self.chosen_row['param'][slope_name]),2)
			model_str = "\nIntercept: "+str(Intercept_value)+',\n '+str(slope_name)+" as Coefficient: "+str(slope_value)
		theta = "The goodness of fit of the model is "+str(round(self.chosen_row['theta'],2))
		local_desc = "For "+fixed_clause+',the '+self.agg_alias +' is '+modeltype+' in '+variable_attribute+'.'
		local_desc = local_desc.replace('const','constant')
		pattern_attr = model_str+theta
		raw_pattern_description = local_desc+pattern_attr
		raw_pattern_description_lists = textwrap.wrap(raw_pattern_description,width=35)
		final_pattern_description = '\n'.join(raw_pattern_description_lists)

		pattern_description = Label(self.win_frame,text=final_pattern_description,font=('Times New Roman bold',18),borderwidth=5,bg='white',relief=SOLID,justify=LEFT)
		pattern_description.grid(column=0,row=0,sticky='nsew')


