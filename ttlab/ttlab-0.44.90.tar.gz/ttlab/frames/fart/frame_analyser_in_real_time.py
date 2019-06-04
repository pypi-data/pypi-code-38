import numpy as np
import matplotlib.pyplot as plt
from .frame_stream import FrameStream
from .file_reader import FileReader
import ipywidgets as widgets
from ipywidgets import interact
import plotly.graph_objs as go
from plotly.offline import init_notebook_mode, iplot


class FART:

    def __init__(self, filename=None, gridfs=None, recording_software='fart', force_read_into_memory=False):
        if self._get_size_of_measurement_file(filename=filename, gridfs=gridfs) > 1e9 and not force_read_into_memory:
            self._use_file_stream_for_data(filename=filename, gridfs=gridfs)
            self._in_memory = False
        else:
            self._read_data_into_memory(filename=filename, gridfs=gridfs)
            self._in_memory = True

    @property
    def measurement_info(self):
        return self.data.measurement_info

    @property
    def time(self):
        return self.data.time

    @property
    def frames(self):
        if self._in_memory:
            return self.data.frames
        else:
            return self.data

    def show_frames_as_video(self):
        out = widgets.Output()
        play = widgets.Play(
            value=0,
            min=0,
            max=len(self.time) - 1,
            step=1,
            description="Press play",
            disabled=False
        )
        slider = widgets.IntSlider(
            value=0,
            min=0,
            max=len(self.time) - 1,
            step=1,
            description='Time:',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
        )
        interact(self._plot_frame_with_index, index=play)
        widgets.jslink((play, 'value'), (slider, 'value'))
        widgets.VBox([slider, out])

    def get_frame_at_time(self, time):
        return self.data.get_frame_at_time(time)

    def plot_frame_at_time(self, time):
        frame = self.get_frame_at_time(time)
        self._plot_frame(frame)

    def plot_all_frames(self, figsize=(6, 8)):
        plt.style.use({'figure.figsize': figsize})
        interact(self.plot_frame_at_time, time=widgets.SelectionSlider(
            options=self.time,
            value=self.time[0],
            description='Time:',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True
        ))

    @staticmethod
    def _find_index_of_nearest(array, value):
        return (np.abs(np.array(array) - value)).argmin()

    @staticmethod
    def _plot_frame(frame):
        plt.imshow(frame)

    def _plot_frame_with_index(self, index):
        frame = self.frames[index]
        self._plot_frame(frame)

    def _use_file_stream_for_data(self, filename, gridfs):
        if filename:
            self._FrameStream = FrameStream(filename=filename)
        elif gridfs:
            self._FrameStream = FrameStream(gridfs=gridfs)
        else:
            raise ValueError('Needs at least one argument, filename or gridfs')

    def _get_size_of_measurement_file(self, filename, gridfs):
        if filename:
            with open(filename) as file:
                file.seek(0, 2)
                return file.tell()
        elif gridfs:
            return gridfs.length

    def _read_data_into_memory(self, filename, gridfs):
        self.data = FileReader(filename, gridfs)

    @staticmethod
    def plotly_frames(frames, time):
        init_notebook_mode(connected=True)

        data = [go.Heatmap(z=frame) for frame in frames]
        for trace in data:
            trace['visible'] = False

        data[0]['visible'] = True

        steps = []
        for i, t in enumerate(time):
            step = dict(
                method='restyle',
                args=['visible', [False] * len(data)],
                label=str(t)
            )
            step['args'][1][i] = True  # Toggle i'th trace to "visible"
            steps.append(step)

        sliders = [dict(
            active=0,
            currentvalue={"prefix": "Time: "},
            pad={"t": 50},
            steps=steps
        )]

        layout = dict(sliders=sliders)
        fig = dict(data=data, layout=layout)

        return iplot(fig, filename='basic-heatmap')
