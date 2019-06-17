import sys,os,dlib,glob,numpy
#pip install scikit-image
from skimage import io
import cv2
import os
import time
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from os.path import dirname
Package_Dir = dirname(__file__)
#載入字型
_FONT = ImageFont.truetype(Package_Dir+"\\kaiu.ttf",20,index=0)
# 載入人臉檢測器
_detector = dlib.get_frontal_face_detector()
# 載入人臉特徵點檢測器
__sp = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
#shape_predictor_68_face_landmarks.dat has to download by user

# 載入人臉辨識檢測器
_facerec = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")
#dlib_face_recognition_resnet_model_v1.dat  has to download by user


DB={}
#一張圖片中，取rect區域當作人臉得到特徵向量   
def getFeatureVector(img,rect=None):
    if not rect:
        try:
            rect=_detector(img, 1)[0] #如果沒有傳入rect取第一個檢測到的臉區域
        except:return None
    shape = _sp(img,rect) #找出特徵點位置
    #由圖片中特徵點位置(shape)擷取出特徵向量(128維特徵向量)
    face_descriptor = _facerec.compute_face_descriptor(img, shape)
    # 轉換numpy array格式
    return numpy.array(face_descriptor)

def _createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' +  directory)
        
def predictFromDB(VTest,db=DB):
    minD = sys.float_info.max
    minK=''
    for k in DB:
        dist=numpy.linalg.norm(VTest-DB[k])
        if dist<minD:
            minK=k
            minD=dist
    return minK,minD

def addText2Img_cv2(img_cv2,text,font=_FONT,position=(20,20),fill=(255,0,0)):
    img_PIL = Image.fromarray(cv2.cvtColor(img_cv2,cv2.COLOR_BGR2RGB))#cv2.COLOR_BGR2RGB cv2.COLOR_RGB2BGR
    draw = ImageDraw.Draw(img_PIL)
    draw.text(position, text, font=font, fill=fill)
    img_cv2 = cv2.cvtColor(numpy.asarray(img_PIL),cv2.COLOR_RGB2BGR)# 转换回OpenCV格式
    img_PIL.close()
    return img_cv2

def LoadDB(db=DB,folder=Package_Dir+'\\train'):
    for D in os.listdir(folder):
        for r,d,f in os.walk(folder+"\\"+D):
            fname=folder+"\\"+D+"\\"+f[0]
            print("get Feature from:"+fname)
            img = io.imread(fname)
            DB[D]=getFeatureVector(img)
            break

#由webcam擷取訓練影像
def getPicFromCam(tag,folder=Package_Dir+"\\train"):
    ret = False
    cap = None
    for i in range(3):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            break
    if not cap:return False
    cv2.startWindowThread()
    # 載入人臉檢測器
    text="press p to take picture"
    num=0
    _createFolder(folder+"\\"+tag)

    while(True):
        if cap.isOpened():
            ret, frame = cap.read()
            # 顯示圖片
            if ret: 
                try:
                    rect=_detector(frame, 1)[0] #取第一個檢測到的臉區域# IndexError
                    if cv2.waitKey(1) & 0xFF == ord('p'):
                        im=cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        io.imsave(folder+"\\"+tag+"\\"+str(num)+".jpg",im)
                        num+=1
                        text=str(num)+" pictures saved..."
                        ret = True
                    cv2.rectangle(frame,(rect.left(),rect.top()),(rect.right(),rect.bottom()),(255,0,0),3)
                    cv2.putText(frame, text,(rect.left()-80, rect.top()-20), cv2.FONT_HERSHEY_SIMPLEX,1, (255, 0, 0), 2, cv2.LINE_AA)    
                    frame=addText2Img_cv2(frame,'tag='+tag,_FONT,(rect.left(), rect.top()-_FONT.size*2-5))   
                #except:pass 
                except IndexError:pass
                cv2.imshow('press esc to exit', frame)
            #若按下 esc 鍵則離開迴圈
            if cv2.waitKey(1) == 27: break
    cap.release()
    cv2.destroyAllWindows()
    return ret

def predictVedio(vedioPath,skipFranmes=50,db=DB):
    try:
        cv2.startWindowThread()
        #windowName = "My Image"
        #cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
        cap = cv2.VideoCapture(vedioPath)
        success,image = cap.read()
        count = 0
        while success:
            success,frame = cap.read()
            count+=1
            if count%skipFranmes!=0 :continue
            try:
                rects=_detector(frame, 1)
                for rect in rects:
                    V=getFeatureVector(frame,rect)
                    Tag,dist=predictFromDB(V,db)
                    cv2.rectangle(frame,(rect.left(),rect.top()),(rect.right(),rect.bottom()),(255,0,0),3)
                    text=Tag+":"+str(dist)
                    frame=addText2Img_cv2(frame,Tag+":"+str(round(dist,3)),
                                          _FONT,(rect.left(), rect.top()-_FONT.size-1))        
            except IndexError:pass    
            cv2.imshow("press esc to exit...", frame)
            if cv2.waitKey(10) == 27:                     # exit if Escape is hit
                break
    except Exception:print(Exception.args)
        
    cap.release()
    cv2.destroyAllWindows()
    
#取得影像檔之原始特徵向量(正規化：同除255)
def getPicRawFeature(fname):
    try:
        img = io.imread(fname)
        #img.tofile('test.txt',',')
        return img.flatten()/255.0
    except Exception:print(Exception.args)
    return None