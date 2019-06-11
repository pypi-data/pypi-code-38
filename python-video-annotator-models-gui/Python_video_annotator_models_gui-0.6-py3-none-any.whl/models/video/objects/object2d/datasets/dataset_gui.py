import json, AnyQt
from confapp import conf
from pythonvideoannotator_models_gui.models.imodel_gui import IModelGUI
from pythonvideoannotator_models_gui.dialogs import Dialog
from pythonvideoannotator.utils import tools

if conf.PYFORMS_MODE=='GUI':
	from AnyQt.QtWidgets import QFileDialog


class DatasetGUI(IModelGUI):

	def __nodes_names(self, fullname):
		fullname = fullname.lower().replace(' ', '')
		values 	 = fullname.split('>')
		if len(values)>1:
			return '_'.join( values[:-1] ), values[-1]
		else:
			return None, values[0]

	def __group_name(self, fullname):
		group_name, data_name 	= self.__nodes_names(fullname)
		return 'treenode' if group_name is None else 'treenode_{0}'.format(group_name)

	def __child_title(self, fullname): return fullname.split('>')[-1]

	def __child_name(self, fullname):
		group_name, data_name 	= self.__nodes_names(fullname)
		prefix = 'treenode' if group_name is None else 'treenode_{0}'.format(group_name)
		return prefix + '_' + data_name

	def __data_function(self, fullname):
		group_name, data_name = self.__nodes_names(fullname)
		if group_name is None:
			data_func_name = 'get_{0}_value'.format(data_name)
		else:
			data_func_name = 'get_{0}_{1}_value'.format(group_name, data_name)
		return data_func_name
	
	def __group_treenode(self, fullname):
		groupnode_name = self.__group_name(fullname)
		if not hasattr(self, groupnode_name): 
			raise Exception('The tree node [{0}] object is missing'.format(groupnode_name))
		return getattr(self, groupnode_name)


	def create_group_node(self, fullname, icon):

		# create a group of data on the project tree
		parent_node = self.__group_treenode(fullname)
		child_title = self.__child_title(fullname)
		child_node 	= self.tree.create_child(child_title, icon=icon, parent=parent_node)
		child_node.win = self

		setattr(self, self.__child_name(fullname), child_node )
		
		return child_node

	def create_data_node(self, fullname, icon):
		# create a data node on the project tree
		parent_node = self.__group_treenode(fullname)
		
		# create the node
		child_title = self.__child_title(fullname)
		child_node 	= self.tree.create_child(child_title, icon=icon, parent=parent_node)
		child_node.win = self
		
		data_func_name = self.__data_function(fullname)

		# check if the function to get the data from the node exists
		# if so add the option to the tree node
		if hasattr(self, data_func_name ):
			data_func = getattr(self, data_func_name )
			child_node.data_function = data_func

			action = tools.make_lambda_func(self.send_2_timeline_event, tree_item=child_node, data_func=data_func )
			self.tree.add_popup_menu_option(
				label='View on the timeline', 
				function_action=action ,
				item=child_node,
				icon=conf.ANNOTATOR_ICON_TIMELINE
			)

			action = tools.make_lambda_func(self.export_2_csvfile_event, data_func=data_func )
			self.tree.add_popup_menu_option(
				label='Export to file', 
				function_action=action ,
				item=child_node,
				icon=conf.PYFORMS_ICON_EVENTTIMELINE_EXPORT
			)

			action = tools.make_lambda_func(self.__create_new_value_event, tree_item=child_node, data_func=data_func )
			self.tree.add_popup_menu_option(
				label='Use this property to create a new value', 
				function_action=action ,
				item=child_node,
				icon=conf.ANNOTATOR_ICON_NEW
			)

		return child_node


	######################################################################
	### GUI EVENTS #######################################################
	######################################################################

	def __create_new_value_event(self, tree_item, data_func):
		values = self.object2d.create_value()
		values.name = str(tree_item.text(0))
		for i in range(len(self)):
			v = data_func(i)
			if v is not None: values.set_value(i, v)
		
	def send_2_timeline_event(self, tree_item, data_func):
		data = []
		for i in range(len(self)):
			v = data_func(i)
			if v is not None: data.append( (i,v) )
		self.mainwindow.add_graph(str(tree_item.text(0)), data)

	def export_2_csvfile_event(self, data_func):
		filename, ffilter = QFileDialog.getSaveFileName(parent=self,
													 caption="Export data",
													 directory="untitled.csv",
													 filter="CSV Files (*.csv)")
		if filename is not None and len(filename.strip())>0:
			filename = str(filename)
			with open(filename, 'w') as outfile:
				for i in range(len(self)):
					v = data_func(i)
					if v is not None:  outfile.write((';'.join(map(str, [i, v]) )+'\n') )

	def remove_dataset(self):
		self.object2d -= self


	def draw(self, frame, frame_index):
		pass


	def on_drag(self, p1, p2):
		pass

	def on_end_drag(self, p1, p2):
		pass

	def on_click(self, event, x, y):
		pass

	def on_double_click(self, event, x, y):
		pass