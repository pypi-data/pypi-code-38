from pyaudio import PyAudio, paInt32
import wave
from VmorpheusVoice.tools.Name_files import Name_files
import os

class Microphone():
    def __init__(self,profile):
        self.CHUNK = 1024
        self.FORMAT = paInt32
        self.CHANNELS = 2
        self.RATE = 44100
        self.RECORD_SECONDS = 5
        self.name_file = Name_files()
        self.output_filename = ""
        self.input_audio = None
        self.frames = []
        self.profile = profile
        self.name_dir = 'in_audio'
        self.input_device = None
        self.stream = None
        

    def set_name_file(self):
        self.input_audio = PyAudio()
        self.output_filename = self.profile.get_filepath(self.name_dir) +"/"+ self.name_file.get_name_file("output","wav")
    
    def set_stream(self):
        self.frames = []
        self.set_name_file()
        self.stream = self.input_audio.open(format=self.FORMAT, channels=self.CHANNELS, rate = self.RATE, input=True, frames_per_buffer = self.CHUNK, input_device_index = self.input_device)

    
    def record(self,semaforo):
        if self.stream == None:
            print("No a iniciado el dispositivo de grabacion")
            return
        print("Grabando")
        semaforo.acquire()
        while True:
            data = self.stream.read(self.CHUNK)
            self.frames.append(data)
        semaforo.release()
        print("Dejando de grabar")
    
    def unset_stream(self):
        self.stream.stop_stream()
        self.stream.close()
        self.input_audio.terminate()


    def save_audio_file(self):
        self.set_name_file()
        wf = wave.open(self.output_filename,'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.input_audio.get_sample_size((self.FORMAT)))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        print("grabacion guardada en {0}".format(self.output_filename))
    

    def print_input_devices(self):
        os.system('clear')
        for i in range(0,PyAudio().get_device_count()):
            device = PyAudio().get_device_info_by_index(i)
            print("{0}: {1}".format(device['index'],device['name']))

    def set_input_device(self):
        self.print_input_devices()
        self.input_device = input("Selecciona el dispositivo(Default=None)_")
        print(range(0,PyAudio().get_device_count()))
        print(self.input_device)
        if (self.input_device == ''):
            self.input_device = None
        elif int(self.input_device) not in range(0,PyAudio().get_device_count()):
            self.input_device = None
        else:
            self.input_device = int(self.input_device)
        print(self.input_device)


