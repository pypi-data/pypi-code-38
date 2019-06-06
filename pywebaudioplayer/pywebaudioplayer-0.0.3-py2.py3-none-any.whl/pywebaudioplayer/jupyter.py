# coding: utf-8
from IPython.core.display import DisplayObject
from .core import wavesurfer, waveform_playlist, trackswitch

class WaveSurfer(DisplayObject):
    # _read_flags = 'rb'

    def __init__(self, audio_path=None, controls={}, display={}, behaviour={}, samples=None):
        self.audio_path = audio_path
        self.controls = controls
        self.display = display
        self.behaviour = behaviour
        self.samples = samples
        #data=None, filename=None, url=None, embed=None, rate=None, autoplay=False):
        # if filename is None and url is None and data is None:
        #     raise ValueError("No image data found. Expecting filename, url, or data.")
        # if embed is False and url is None:
        #     raise ValueError("No url found. Expecting url when embed=False")

        # if url is not None and embed is not True:
        #     self.embed = False
        # else:
        #     self.embed = True
        # self.autoplay = autoplay
        # super(Audio, self).__init__(data=data, url=url, filename=filename)

        # if self.data is not None and not isinstance(self.data, bytes):
        #     self.data = self._make_wav(data,rate)

    # def reload(self):
    #     """Reload the raw data from file or URL."""
    #     import mimetypes
    #     if self.embed:
    #         super(Audio, self).reload()

    #     if self.filename is not None:
    #         self.mimetype = mimetypes.guess_type(self.filename)[0]
    #     elif self.url is not None:
    #         self.mimetype = mimetypes.guess_type(self.url)[0]
    #     else:
    #         self.mimetype = "audio/wav"

    # def _data_and_metadata(self):
    #     """shortcut for returning metadata with url information, if defined"""
    #     md = {}
    #     if self.url:
    #         md['url'] = self.url
    #     if md:
    #         return self.data, md
    #     else:
    #         return self.data

    def _repr_html_(self):
        # src = """
        #         <audio controls="controls" {autoplay}>
        #             <source src="{src}" type="{type}" />
        #             Your browser does not support the audio element.
        #         </audio>
        #       """
        # return src.format(src=self.src_attr(),type=self.mimetype, autoplay=self.autoplay_attr())
        return wavesurfer(self.audio_path, self.controls, self.display, self.behaviour, self.samples)

    # def src_attr(self):
    #     import base64
    #     if self.embed and (self.data is not None):
    #         data = base64=base64.b64encode(self.data).decode('ascii')
    #         return """data:{type};base64,{base64}""".format(type=self.mimetype,
    #                                                         base64=data)
    #     elif self.url is not None:
    #         return self.url
    #     else:
    #         return ""

    # def autoplay_attr(self):
    #     if(self.autoplay):
    #         return 'autoplay="autoplay"'
    #     else:
    #         return ''

class WaveformPlaylist(DisplayObject):
    def __init__(self, tracks, controls={}, display={}, behaviour={}):
        self.tracks = tracks
        self.controls = controls
        self.display = display
        self.behaviour = behaviour

    def _repr_html_(self):
        return waveform_playlist(self.tracks, self.controls, self.display, self.behaviour)

class TrackSwitch(DisplayObject):
    def __init__(self, tracks, text='', seekable_image=None, seek_margin=None, mute=True, solo=True, globalsolo=True, repeat=False, radiosolo=False, onlyradiosolo=False, spacebar=False, tabview=False):
        self.tracks = tracks
        self.text = text
        self.seekable_image = seekable_image
        self.seek_margin = seek_margin
        self.mute = mute
        self.solo = solo
        self.globalsolo = globalsolo
        self.repeat = repeat
        self.radiosolo = radiosolo
        self.onlyradiosolo = onlyradiosolo
        self.spacebar = spacebar
        self.tabview = tabview

    def _repr_html_(self):
        return trackswitch(self.tracks, self.text, self.seekable_image, self.seek_margin, self.mute, self.solo, self.globalsolo, self.repeat, self.radiosolo, self.onlyradiosolo, self.spacebar, self.tabview)

