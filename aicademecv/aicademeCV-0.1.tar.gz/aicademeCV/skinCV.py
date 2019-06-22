


import cv2 
import numpy as np

class skinseperator(object):

        #class constructor
        def __init__(self, imageName, newimageName):
                self.image = cv2.imread(imageName)   
                if self.image is None:
                        print("IMAGE NOT FOUND")
                        exit(1)                          
                #self.image = cv2.resize(self.image,(600,600),cv2.INTER_AREA)   
                self.HSV_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
                self.YCbCr_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2YCR_CB)
                self.binary_mask_image = self.HSV_image
                self.imageName = newimageName
#================================================================================================================================
        #function to process the image and segment the skin using the HSV and YCbCr colorspaces, followed by the Watershed algorithm
        def find_skin(self):
                self.__color_segmentation()
                self.__region_based_segmentation()

#================================================================================================================================
        #Apply a threshold to an HSV and YCbCr images, the used values were based on current research papers along with some
        # empirical tests and visual evaluation
        def __color_segmentation(self):
                lower_HSV_values = np.array([0, 40, 0], dtype = "uint8")
                upper_HSV_values = np.array([25, 255, 255], dtype = "uint8")

                lower_YCbCr_values = np.array((0, 138, 67), dtype = "uint8")
                upper_YCbCr_values = np.array((255, 173, 133), dtype = "uint8")


                #A binary mask is returned. White pixels (255) represent pixels that fall into the upper/lower.
                mask_YCbCr = cv2.inRange(self.YCbCr_image, lower_YCbCr_values, upper_YCbCr_values)
                mask_HSV = cv2.inRange(self.HSV_image, lower_HSV_values, upper_HSV_values) 

                self.binary_mask_image = cv2.add(mask_HSV,mask_YCbCr)

#================================================================================================================================
        #Function that applies Watershed and morphological operations on the thresholded image
        def __region_based_segmentation(self):
                lower_red = np.array([0,0,0], dtype = "uint8")
                upper_red = np.array([179,255,50],  dtype = "uint8")

                #morphological operations
                image_foreground = cv2.erode(self.binary_mask_image,None,iterations = 3)        #remove noise

                dilated_binary_image = cv2.dilate(self.binary_mask_image,None,iterations = 3)   #The background region is reduced a little because of the dilate operation
                ret,image_background = cv2.threshold(dilated_binary_image,1,128,cv2.THRESH_BINARY)  #set all background regions to 128

                image_marker = cv2.add(image_foreground,image_background)   #add both foreground and backgroud, forming markers. The markers are "seeds" of the future image regions.
                image_marker32 = np.int32(image_marker) #convert to 32SC1 format

                cv2.watershed(self.image,image_marker32)
                m = cv2.convertScaleAbs(image_marker32) #convert back to uint8 

                #bitwise of the mask with the input image
                ret,image_mask = cv2.threshold(m,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
                output = cv2.bitwise_and(self.image,self.image,mask = image_mask)
                

                #show the images
                #self.show_image(self.image)
                #self.show_image(image_mask)
                #mask = cv2.inRange(output, lower_red, upper_red)
                #h, s, gray = cv2.split(mask)
                #gray = cv2.cvtColor(mask, cv2.COLOR_HSV2GRAY)
                gray = image_mask
                gray = 255-gray
                ret, thresh = cv2.threshold(gray, 225, 255, cv2.THRESH_BINARY_INV)
                contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
                #frame = cv2.drawContours(output, contours, -1,(0,0,255),3)
                if len(contours) != 0:
                        cv2.drawContours(output, contours, -1, 255, 3)
                        #c = max(contours, key = cv2.contourArea)
                        #cv2.drawContours(output, contours, -1,(0,0,255),3)
                        c = max(contours, key = cv2.contourArea)
                        x,y,w,h = cv2.boundingRect(c)
                        # draw the book contour (in green)
                        cv2.rectangle(output,(x,y),(x+w,y+h),(0,255,0),2)
                        roi = self.image[y:y+h, x:x+w]
                import os
                if not os.path.exists('positive'):
                        os.makedirs('positive')
                if not os.path.exists('negative'):
                        os.makedirs('negative')
                if w>50 and h>50:
                        cv2.imwrite('positive/'+self.imageName, roi)
                else:
                        cv2.imwrite('negative/'+self.imageName, roi)
                print(x,y,w,h)
                       
                
                #cv2.imshow('mask',output) 
                #self.show_image(output)
                #return(output)
#================================================================================================================================
        def show_image(self, image):
                cv2.imshow("Image",image)
                cv2.waitKey(0)
                cv2.destroyWindow("Image")
#================================================================================================================================
