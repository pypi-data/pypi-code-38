import math, cv2, os, AnyQt

from confapp import conf
if conf.PYFORMS_MODE=='GUI':
	from AnyQt.QtWidgets import QMessageBox


class VideosExporterProcess(object):


	def apply_event(self):

		if len(self._panel_path.value.datasets)<1:
			QMessageBox.information(self, "Alert", "Please select at least one path")
			return

		if self._apply.checked:
			self._toolbox.enabled = False
			self._player.stop()		
			self._player.enabled  = False
			self._outfile.enabled = False	
			self._apply.label 	  = 'Cancel'
			self.outputfile_changed_event()

			images     = self._panel_imgs.value.images
			background = None if len(images)!=1 else images[0].image.copy()

			areas  = self._panel_area.value.datasets
			colors = self._panel_colors.value.datasets
			images = self._panel_imgs.value.images

			timeline   = self.parent().timeline

			for v_index, (video, (begin,end), paths) in enumerate(self._panel_path.value.selected_data):
				if not self._apply.checked:	break
				

				### calculate the video cuts #############################
				selected_events = self._splitevents.value
				videocuts   = []
				if len(selected_events):
					# use the events to cut the video
					totalframes = 0
					for row in timeline.rows:
						for event in row.events:
							if event.end<=begin: continue
							if event.begin>=end: continue
							if event.title not in selected_events: continue
							b = int(event.begin if event.begin>=begin else begin)
							e = int(event.end   if event.end<=end else end)
							totalframes += e-b
							videocuts.append( (b, e, event.title) )
					videocuts = sorted(videocuts, key = lambda x: x[0])
				else:
					# no events were selected
					totalframes = end-begin
					videocuts   = [(int(begin), int(end), None)]
				##########################################################

				self._progress.min = 0
				self._progress.max = totalframes
				self._progress.label = 'Processing: {0}'.format(video.name)
				self._progress.show()

				fps   = int(video.video_capture.get(cv2.CAP_PROP_FPS))
				if self._codec.value==True: 
					codec = cv2.VideoWriter_fourcc('M','J','P','G')
				else:
					codec = int(video.video_capture.get(cv2.CAP_PROP_FOURCC))
							
				# start the loop that will create the video files
				for b, e, event_name in videocuts:

					if background is None:
						size    = int(video.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
						capture = cv2.VideoCapture(video.filepath)
						capture.set(cv2.CAP_PROP_POS_FRAMES, b)
					else:
						size    = background.shape[1], background.shape[0]
						capture = None

					outfilename = self._outfile.value
					outfilename = outfilename.format(videoindex=v_index, event=event_name, start=b, end=e)
					outfilename = os.path.join(self._outdir.value, outfilename)
					outputvideo = cv2.VideoWriter(outfilename, codec, fps, size, True)

					for index in range(b,e):
						if not self._apply.checked:	break

						if background is None:
							res, frame = capture.read()
							if not res: break
						else:
							frame = background.copy()

						for path in paths:	
							if not self._apply.checked:	break

							# draw the path if the option is selected
							if self._drawpath.value: path.draw_path(frame, b, index)

							area = self.get_object_area(path, areas, index)
							if area is not None:
								position = path.get_position(index)
								color 	 = self.get_object_color(path, colors, index)

								if position is not None and area is not None and color is not None:
									radius = int(round(math.sqrt(area/math.pi)))				
									cv2.circle(frame, position, radius, color, -1)

						self.draw_events(index, frame)
						outputvideo.write(frame)

						self._progress.value = index					

				outputvideo.release()

			self._toolbox.enabled 		= True
			self._player.enabled 		= True
			self._outfile.enabled 		= True
			self._apply.label 			= 'Export video(s)'
			self._apply.checked 		= False
			self._progress.hide()	