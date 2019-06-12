import pyforms
from confapp import conf
from pyforms.basewidget import BaseWidget

from pyforms.controls import ControlButton
from pyforms.controls import ControlText
from pyforms.controls import ControlDir
from pyforms.controls import ControlFile

from pythonvideoannotator_models.models.video.objects.object2d.datasets.path import Path
from pythonvideoannotator_models.models.video import Video

from os import listdir, getcwd
from os.path import isfile, join, splitext, abspath, dirname, basename
import csv

try:
    import deeplabcut
    deeplabcut_is_installed = True 
except:
    deeplabcut_is_installed = False

import re, yaml

if conf.PYFORMS_MODE=='GUI':
    from AnyQt.QtWidgets import QMessageBox

class DeepLabWindow(BaseWidget):

    def __init__(self, parent=None):
        super(DeepLabWindow, self).__init__('Label DeepLabCut', parent_win=parent)
        self.mainwindow = parent

        if deeplabcut_is_installed:

            self._file         = ControlFile('YAML  to import from:')
            self._importButton  = ControlButton('Import')

            self._outdir        = ControlDir('Output directory')
            self._outfile       = ControlText('Output file name')
            self._exportButton  = ControlButton('Export')

            self._unlabeledFramesButton = ControlButton("Check unlabeled frames ")

            self.formset = [
                ('_file', '_importButton'),
                ' ',
                '_unlabeledFramesButton',
                ' ',
                '_outdir',
                '_outfile',
                '_exportButton',
            ]

            self._importButton.value = self.__importFromYAMLFile
            self._exportButton.value = self.__exportToCSVFile
            self._unlabeledFramesButton.value = self.__checkUnlabeledFrames


            self.set_margin(5)
            #self.layout().setMargin(5)
            self.setMinimumHeight(400)
            self.setMinimumWidth(600)

            self._scorer = ""
            self._videos = {}
            self._bodyparts = []

        else:
            link = "<a target='_blank' href=\"https://pythonvideoannotator.readthedocs.io/en/master/user-docs\
            /install_and_run/index.html#install-deeplabcut\"> https://pythonvideoannotator.readthedocs.io/en/master/user-docs\
            /install_and_run/index.html#install-deeplabcut </a>"

            self.formset = [ "Please follow the instructions in the link below to install deeplabcut: <br/><br/>" + link]

    ###########################################################################
    ### EVENTS ################################################################
    ###########################################################################

    def __importFromYAMLFile(self):

        config_path = self._file.value

        if config_path == "":
            QMessageBox.warning(self, "Import error", "No YAML file was selected. Aborted import!")
            return

        with open(config_path, 'r') as f:
            try:
                dict_yaml = yaml.load(f, Loader=yaml.FullLoader)
            except yaml.YAMLError as exc:
                QMessageBox.warning(self, "Import error", "Could not import the chosen YAML file. Aborted import!")
                return

        try:
            self.scorer = dict_yaml.get("scorer")
            self.videos = dict_yaml.get("video_sets")
            self.bodyparts = dict_yaml.get("bodyparts")

        except AttributeError as err:
                QMessageBox.warning(self, "Import error", "The YAML is not configured correctly. It needs to have a scorer, a videos and a bodyparts attribute. Each video also needs to have a crop attribute.")
                return

        if len(self.videos) != len(set(self.videos)):
            QMessageBox.warning(self, "Import error", "Two videos can't have the same name! Aborted import!")
            return

        if len(self.bodyparts) != len(set(self.bodyparts)):
            QMessageBox.warning(self, "Import error", "Two bodyparts can't have the same name! Aborted import!")
            return

        for video in self.videos.keys():

            v = self.mainwindow.project.create_video()
            v.filepath = abspath(video)

            for part in self.bodyparts:
                obj = v.create_object()
                obj.name = part
                obj.create_path()
            
            #adds the pair video and track to the videos dictionary
            track = self.mainwindow.timeline.add_track(title=v.name)

            deeplabcut.extract_frames(config_path, userfeedback=False)
    
            frames_directory = join(abspath(dirname(config_path)), "labeled-data", v.name)
    
            frames = self.get_frames_from_directory_with_images(frames_directory)
            for frame in frames:
                self.mainwindow.timeline.add_event(begin=frame, end=frame+1, track=track)


        QMessageBox.information(self, "Import finished", "Completed import from YAML file")


    def __exportToCSVFile(self):

        if len(self.videos.keys())==0:
            QMessageBox.warning(self, "Export error", "You don't have any videos to export! Aborted export!")
            return

        video_names = []
        for video_path in self.videos.keys():
            video_names.append(splitext(basename(video_path))[0])
    
        for video in self.mainwindow.project.videos:

            if video.name not in video_names:
                continue

            if self._outdir.value == "":
                if self._outfile.value == "":
                    csv_file_name = join(getcwd(),video.name)
                else:
                    csv_file_name = join(getcwd(), self._outfile.value)
            else:
                if self._outfile.value == "":
                    csv_file_name =  join(self._outdir.value, video.name) 
                else:
                    csv_file_name =  join(self._outdir.value, self._outfile.value)

            csv_file_name = csv_file_name + ".csv"

            with open(csv_file_name, mode='w') as csv_file:

                writer = csv.writer(csv_file, delimiter=',')

                # write row with the name of the scorer(person labeling the frames)
                currentRow = []
                currentRow.append("scorer")
                for _ in range(len(self.bodyparts)*2):
                    currentRow.append(self.scorer)
                writer.writerow(currentRow)


                # write row with the name of the bodyparts
                currentRow = []
                currentRow.append("bodyparts")
                for bodypart in self.bodyparts:
                    currentRow.append(bodypart)
                    currentRow.append(bodypart)
                writer.writerow(currentRow)


                # write row with just x and y
                currentRow = []
                currentRow.append("coords")
                for _ in range((len(self.bodyparts))):
                    currentRow.append("x")
                    currentRow.append("y")
                writer.writerow(currentRow)


                #order the video objects to match the order of the bodyparts
                ordered_objects = []
                for bodypart in self.bodyparts:
                    for obj in video.objects:
                        if obj.name==bodypart:
                            ordered_objects.append(obj)
                            break

                #write the coords of each bodypart for every labeled frame
                track = self.mainwindow.timeline.get_track(video.name)
                if track==None:
                    msg = "No track was found with the name: " + video.name +  "."
                    QMessageBox.warning(self, "Export error", msg +" Aborted export!")
                    return

                for event in track.events:
                    currentRow = []

                    frame=event.begin
                    currentRow.append("labeled-data/"+video.name+"/img"+str(frame)+".png")

                    for obj in ordered_objects:
                        for path in obj.paths:

                            data = path.data

                            if frame<len(data) and data[frame] is not None:
                                currentRow.append(data[frame][0])
                                currentRow.append(data[frame][1])

                            break #there should only be one path for each object
                        
                        else:
                            msg = "Object " + obj.name + " has no path. All objects need to have a path to be exported."
                            QMessageBox.warning(self, "Export error", msg + " Aborted export!")

                    writer.writerow(currentRow)

        QMessageBox.information(self, "Export finished", "Completed export to CSV file")


    def __checkUnlabeledFrames(self):

        if len(self.videos.keys())==0:
            QMessageBox.warning(self, "Error", "There are no videos in the project! Stopped checking unlabeled frames!")
            return

        video_names = []
        for video_path in self.videos.keys():
            video_names.append(splitext(basename(video_path))[0])

        unlabeled_frames={}
        str_unlabeled_frames = ""
        
        for video in self.mainwindow.project.videos:

            if video.name not in video_names:
                continue

            unlabeled_frames[video.name] = {}

            track = self.mainwindow.timeline.get_track(video.name)
            if track==None:
                msg = "No track was found with the name: " + video.name + "."
                QMessageBox.warning(self, "Error", msg + " Stopped checking unlabeled frames!")
                return

            frames_to_label = []
            
            for event in track.events:
                frames_to_label.append(event.begin)


            for obj in video.objects:
                unlabeled_frames[video.name][obj.name] = []
                for path in obj.paths:
                    for frame in frames_to_label:
                        if frame >= len(path.data) or path.data[round(frame)] is None:
                            unlabeled_frames[video.name][obj.name].append(frame)

        for video_name in unlabeled_frames:
            str_unlabeled_frames += video.name + ":\n"
            for obj_name in unlabeled_frames[video_name]:
                str_unlabeled_frames += obj_name + ":\n"
                str_unlabeled_frames += str(unlabeled_frames[video_name][obj_name])
                str_unlabeled_frames += "\n\n"
            str_unlabeled_frames += "\n"


        with open("unlabeled_frames.txt", mode='w') as file:
            file.write(str_unlabeled_frames)

        message = "The results are in the file 'unlabeled_frames.txt' in your current directory"

        QMessageBox.information(self, "Finished checking unlabeled frames", message)


    
    def save_form(self, data, folder):
        if deeplabcut_is_installed:
            return {"scorer" : self.scorer, "videos" : self.videos, "bodyparts" : self.bodyparts}
        else:
            return  data

    def load_form(self, data, folder):

        self.scorer = data.get("scorer")
        self.videos = data.get("videos")
        self.bodyparts = data.get("bodyparts")


    ###########################################################################
    ### HELPER FUNCTIONS ######################################################
    ###########################################################################

    def get_frames_from_directory_with_images(self, directory):
        """
        Given a directory, assumes all files are images and extracts the frame number of each image from the image
        name. Example: filename=image0015.jpg  -> frame=0015

        :param directory: A directory with image files
        :return: A list with all the frames
        """

        files = [f for f in listdir(directory) if isfile(join(directory, f))]

        frames = []

        for filename in files:

            filename = splitext(filename)[0]

            frame = self.get_trailing_number(filename)

            if frame!=None:
                frames.append(frame)

        frames.sort()

        return frames


    def get_trailing_number(self, s):
        """
        :param s: A string with the format: imagexxxx.yyy
        :return: The frame of the image, in the above example returns xxxx
        """
        m = re.search(r'\d+$', s)

        return int(m.group()) if m else None

    ###########################################################################
    ### PROPERTIES ############################################################
    ###########################################################################
 
    @property
    def scorer(self): return self._scorer

    @scorer.setter
    def scorer(self, value): 
        self._scorer = value

    @property
    def videos(self): return self._videos

    @videos.setter
    def videos(self, value): 
        self._videos = value

    @property
    def bodyparts(self): return self._bodyparts

    @bodyparts.setter
    def bodyparts(self, value): 
        self._bodyparts = value

    def __apply_event(self):
        pass

if __name__ == '__main__': 
    pyforms.startApp(DeepLabWindow)
