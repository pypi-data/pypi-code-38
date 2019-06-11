import aud

logger = setupLogger()

dirpath = aud.AudDir("test")

dirpath.extensions = [".wav", ".mp3"]

dirpath.setOutputDir("_Processed")

dirpath.metadata(["Artist": "Nobukazu Takemura", "Type": "sfx", "Keywords": "sword oneshot stereo"])

dirpath.renameUpper()

dirpath.renameLower()

dirpath.renamePrepend("FX_")

dirpath.renameIterate(3)

dirpath.normalize(_type="ebu", _target=-6)

dirpath.pad(_in=2.0, _out=3.5)

dirpath.log("_Processed")

dirpath.move("C://Share/Audio")

dirpath.convertTo(_extension=".wav", _target_samplerate=44100, _target_bitdepth=16)

dirpath.fade(_in = 5.0, _out = 10.5)

filepath = aud.AudDir("test.wav")

filepath.renameReplaceSpaces()

filepath.renamePrepend("sword_sfx_")

filepath.normalize(_type="peak", _target=0)

filepath.convertTo(_extension=".mp3", _target_samplerate=44100, _target_bitrate="320k") #bitrate="0" for lossy compression

filepath.move("/mnt/share")

filepath.fade(_out = 2.2)

logger.debug(filepath)
# C:\Folder\test.wav
