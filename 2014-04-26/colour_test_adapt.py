import freenect
import numpy as np
import cv
import cv2

import frame_convert
import cmath
import math
import csv
import sys

import hashlib
import functools
import scipy.stats as stats

import serial
import time

connected = False

cam = cv2.VideoCapture(0)
print cam.get(3)
L = cam.get(3)/4
R = 3*cam.get(3)/4
print

#ser = serial.Serial("/dev/ttyUSB0", 9600)

def get_video():
    return frame_convert.video_cv(freenect.sync_get_video()[0])

def get_colour(calibration):
    with open(calibration) as csvfile:
            reader = csv.reader(csvfile)
            low = [ float(x) for x in reader.next()]
            high = [ float(x) for x in reader.next()]
    return tuple(low), tuple(high)

def inRange(im, low, high):
    imfilter = cv2.inRange(im,low,high)
    return imfilter

def blobSmoothing(immask):
    imfilter = cv2.medianBlur(immask,7)
    imfilter = cv2.medianBlur(imfilter,5)
    imfilter = cv2.medianBlur(imfilter,3)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))

    imfilter = cv2.dilate(imfilter,kernel)
    imfilter = cv2.erode(imfilter,kernel)
    return imfilter

def get_hull(contours):
    if len(contours):
        mergeContour = contours[0]
        for i in contours[1:]:
            mergeContour = np.concatenate((mergeContour,i))

        return cv2.convexHull(mergeContour)
    else:
        return np.array([])

def calc_time_diff(last_time, curr_time):
    diff = curr_time - last_time
    if diff < 1:
        return 1
    else:
        return 0

def hull_means(imycrcb, hull):
    im_channels = cv2.split(imycrcb)
    y = im_channels[0]
    cr = im_channels[1]
    cb = im_channels[2]

    y_mask = np.zeros(y.shape,np.uint8)
    cr_mask = np.zeros(cr.shape,np.uint8) 
    cb_mask = np.zeros(cb.shape,np.uint8)
    
    cv2.drawContours(mask,[cnt],0,255,-1)
    pixelpoints = np.transpose(np.nonzero(mask))

last_time = time.clock()


last_dir = " "

if __name__ == "__main__":
    low, high = get_colour(sys.argv[1])
    while 1:
        try:
            #imbgr = np.array(get_video())

            imbgr = cam.read()[1]
            imbgr = cv2.flip(imbgr, 1)
            imgray = cv2.cvtColor(imbgr,cv.CV_BGR2GRAY)
            #imdepth = np.array(fe.get_depth())
            imycrcb = cv2.cvtColor(imbgr,cv.CV_BGR2YCrCb)
            imfilter = inRange(imycrcb, low, high)
            imfilter = blobSmoothing(imfilter)
            contours, hierarchy = cv2.findContours(imfilter,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            hull = get_hull(contours)

           #while not connected:
            #    serin = ser.read()
             #   connected = True
            #ser = serial.Serial("/dev/ttyUSB0", 9600)

            

            if len(hull) == 0 and last_dir != "no colour":
                last_dir = "no colour"
                print last_dir
            else:
                if len(hull) != 0:
                    x,y,w,h = cv2.boundingRect(hull)
                    cv2.rectangle(imgray,(x,y),(x+w,y+h),(0,255,0),2) 
                    cv2.circle(imgray, ((x+(w/2)), (y+(h/2))), 10, (0,0,255))
                    cv2.drawContours(imgray,[hull],-1,(255,0,0),2)
                    if (x+(w/2))<L and last_dir != "Left":
                        last_dir = "Left"
                        print last_dir
                    elif (x+(w/2)) > R and last_dir != "Right":
                        last_dir = "Right"
                        print last_dir
                    elif (x+(w/2))>L and (x+(w/2))<R and last_dir != "Straight":
                        last_dir = "Straight"
                        print last_dir

            #ser.close()
            #connected = False

            

            cv2.imshow("Test",imgray)
     
        except KeyboardInterrupt:
            break
        if cv.WaitKey(10) == 32:
            break
