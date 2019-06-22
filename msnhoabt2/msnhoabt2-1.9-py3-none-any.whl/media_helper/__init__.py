import os
import json
import uuid
import re
from shutil import copyfile
import math

def ffprobe(input):
    cmd = "ffprobe -pretty -loglevel quiet -show_format -show_streams -print_format json {}".format(input)
    return os.popen(cmd).read()
def duration(input):
    duration="0"
    try:
        obj = json.loads(ffprobe(input))
        durationT = obj['format']['duration']
        arr_d=re.split("[:.]",durationT)
        return int(arr_d[0])*3600+int(arr_d[1])*60+int(arr_d[2])
    except:
        pass
    return duration
def makefullhd(input,tmp_path):
    output=os.path.join(tmp_path,uuid.uuid4().hex +"_full_hd.jpg")
    cmd="ffmpeg -i \""+input+"\" -filter_complex \" [0:v] split=2 [video0-1][video0-2];"\
                + "[video0-1] scale=w=1280:h=720,boxblur=luma_radius=min(h\,w)/20:luma_power=1:"\
                + "chroma_radius=min(cw\,h)/20:chroma_power=1,setsar=1 [bg0];[video0-2] "\
                + "scale=w=min(iw\,min(iw*1280/ih\,720)):h=min(ih\,min(ih*1280/iw\,720)),"\
                +"setsar=1 [video0-2-scaled];[bg0][video0-2-scaled] overlay=x=(W-w)/2:y=(H-h)/2 [video0]\" "\
                + "-map \"[video0]\" "+output
    print(cmd)
    os.popen(cmd).read()
    return output
def makevid(image,sound,tmp_path):
    output = os.path.join(tmp_path, uuid.uuid4().hex + "_make_vid.avi")
    cmd="ffmpeg -y -r 30 -loop 1 -i {} -i {} -shortest -flags global_header -pix_fmt yuv420p -vcodec libx264 -c copy {}".format(image,sound,output)
    os.popen(cmd).read()
    os.remove(image)
    os.remove(sound)
    return output

def mergvid(arr_vid,tmp_path,output=None,is_delete=True):
    if output ==None:
        output = os.path.join(tmp_path, uuid.uuid4().hex + ".avi")
    file_merg_path=os.path.join(tmp_path, uuid.uuid4().hex + ".txt")
    fileV=open(file_merg_path,"w")
    for vid in arr_vid:
        fileV.write("file '"+os.path.basename(vid)+"'\n")
    fileV.close()
    cmd = "ffmpeg -y -f concat -auto_convert 1 -safe 0 -i "+file_merg_path.replace("\\","/")+" -codec copy "+output
    os.popen(cmd).read()
    for vid in arr_vid:
        try:
            if is_delete:
                os.remove(vid)
            #print(vid)
        except:
            pass
    os.remove(file_merg_path)
    return output
def make_sound_null(time,tmp_path):
    output = os.path.join(tmp_path, uuid.uuid4().hex + "_null_sound.wav")
    cmd="ffmpeg -y  -f lavfi -i anullsrc=channel_layout=mono:sample_rate=24000 -t {} {}".format(time,output)
    os.popen(cmd).read()
    return output
def dup_sound(sound_bg,duration_vid,tmp_path):
    dup_bg = os.path.join(tmp_path, uuid.uuid4().hex + ".wav")
    output = os.path.join(tmp_path, uuid.uuid4().hex + "_dup_sound.wav")
    file_merg_path = os.path.join(tmp_path, uuid.uuid4().hex + ".txt")
    copyfile(sound_bg,dup_bg)
    dur_bg=duration(dup_bg)
    if(dur_bg<duration_vid):
        times=math.ceil(duration_vid/dur_bg)
        file_merg_path = os.path.join(tmp_path, uuid.uuid4().hex + ".txt")
        fileV = open(file_merg_path, "w")
        i=0
        while i<times:
            fileV.write("file '" + os.path.basename(dup_bg) + "'\n")
            i+=1
        fileV.close()
        cmd = "ffmpeg -y -f concat -safe 0 -i " + file_merg_path.replace("\\", "/") + " -codec copy " + output
        os.popen(cmd).read()
        os.remove(dup_bg)
        os.remove(file_merg_path)
    else:
        output=dup_bg
    return output
def mix_sound_bg(vid,sound_bg,tmp_path,output):
    #output = os.path.join(tmp_path, uuid.uuid4().hex + ".avi")
    new_sound_bg= dup_sound(sound_bg,duration(vid),tmp_path)
    cmd="ffmpeg -y -i {} -i {} -filter_complex \"[0:a][1:a]amerge=inputs=2,pan=stereo|c0<c0+c2|c1<c1+c2[a]\" -c:v copy -map 1:v -map \"[a]\" -shortest {}".format(new_sound_bg,vid,output)
    os.popen(cmd).read()
    os.remove(vid)
    os.remove(new_sound_bg)
    print(output)

