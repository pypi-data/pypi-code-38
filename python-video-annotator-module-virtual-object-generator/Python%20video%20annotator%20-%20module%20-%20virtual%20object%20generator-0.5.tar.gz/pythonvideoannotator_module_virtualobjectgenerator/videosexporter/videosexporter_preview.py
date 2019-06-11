import math, cv2, os

class VideosExporterPreview(object):

	def player_processframe_event(self, frame):
		"""
		Function called before rendering the frame in the preview player
		"""
		paths    = self._panel_path.value.datasets
		areas    = self._panel_area.value.datasets
		colors   = self._panel_colors.value.datasets
		images   = self._panel_imgs.value.images

		# check if should use the current frame or an image selected to background
		frame  = frame if len(images)!=1 else images[0].image.copy()
		index  = self._player.video_index-1
	
		for path in paths:
			# draw the path if the option is selected
			if self._drawpath.value: path.draw_path(frame, None, index)

			area = self.get_object_area(path, areas, index)
			if area is not None:
				color 	 = self.get_object_color(path, colors, index)
				position = path.get_position(index)
				
				if position is not None and area is not None and color is not None:
					radius = int(round(math.sqrt(area/math.pi)))				
					cv2.circle(frame, position, radius, color, -1)

		self.draw_events(index, frame)

		return frame


	def draw_events(self, index, frame):
		"""
		Draw the selected events
		"""
		timeline = self.parent().timeline
		
		img_width  = frame.shape[1]
		img_height = frame.shape[0]
		half_img   = int(img_width/2)
		begin 	   = index - half_img
		end 	   = index + half_img

		# variables used to draw the green line in the middle of the video
		higher_y, lower_y  = None, None
		
		for row in timeline.rows:
			for event in row.events:
				if event.title in self._drawevents.value and event.in_range(begin, end):

					line_y = int(img_height - 25 - 15*event.track.index)

					if higher_y is None or line_y>higher_y: higher_y = line_y
					if lower_y is None or line_y<lower_y:   lower_y  = line_y

					x, y   = int(half_img + event.begin - index), int(img_height - 25 - 15*event.track.index)
					xx, yy = int(half_img + event.end - index),   int(img_height - 25 - 15*event.track.index)
					cv2.rectangle(frame, (x,y),(xx,yy+4), event.bgrcolor, -1)

					if self._eventstitles.value:
						#cv2.putText(frame,event.title,(x,y-3), cv2.FONT_HERSHEY_SIMPLEX, .3,(0,0,0), 2,cv2.LINE_AA)
						cv2.putText(frame,event.title,(x,y-3), cv2.FONT_HERSHEY_SIMPLEX, .3,event.bgrcolor,1,cv2.LINE_AA)
					
		if lower_y is not None and higher_y is not None:
			cv2.line(frame, (half_img,lower_y-2),(half_img,higher_y+6), (0,255,0), 1)