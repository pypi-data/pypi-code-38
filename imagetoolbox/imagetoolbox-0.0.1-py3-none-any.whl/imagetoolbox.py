import cv2
def impixelinfo(img):
    def pix(event,x,y,f,p):
        if event==cv2.EVENT_MOUSEMOVE:
            if len(img.shape)==3:
                pinfo="["+str(y)+","+str(x)+"]=>("+str(img[y][x][0])+"-"+str(img[y][x][1])+"-"+str(img[y][x][2])+")"
                cv2.setWindowTitle("wn",pinfo)
            else:
                pinfo="["+str(y)+","+str(x)+"]=>("+str(img[y][x])+")"
                cv2.setWindowTitle("wn",pinfo)
    cv2.namedWindow("wn")
    cv2.setMouseCallback("wn",pix)
    cv2.imshow("wn",img)
    cv2.waitKey(0)
