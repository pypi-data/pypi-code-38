import glob
import soundfile as sf
import numpy as np
import librosa

def merge_dir(pattern,sr = 16000,slience_second = 4):
        file_list = glob.glob(pattern)
        slience = np.zeros(slience_second*sr)
        d = ()
        for f in file_list:
                data,sr = librosa.core.load(f,sr=sr)
                librosa.output.write_wav(f,data,sr,norm=True)
                data,sr = librosa.core.load(f,sr=sr)
                d+=(data,)
                d+=(slience,)
                
        data = np.concatenate(d)
        print("merge: ",data.shape)
        return data


