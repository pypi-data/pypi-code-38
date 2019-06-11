

class ProjectTimeline(object):
	

	def __init__(self, parent=None):
		super(ProjectTimeline, self).__init__(parent)


	def tree_item_selection_changed_event(self):
		super(ProjectTimeline, self).tree_item_selection_changed_event()
		item = self.tree.selected_item 

		if self.tree.selected_item is not None:
			if hasattr(item, 'win') and item.win is not None:
				if self.mainwindow.video!=self.tree.selected_item.win.video_capture:
					self.mainwindow.player.stop()
					self.mainwindow.video = self.tree.selected_item.win.video_capture
		else:
			self.mainwindow.video = None