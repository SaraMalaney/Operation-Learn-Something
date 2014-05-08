import featureExtraction as fe
import numpy as np 
#import freenect
import frame_convert
import os
import sys
import cv2
#import cv
import csv
import time

#def get_video():
#	return frame_convert.video_cv(freenect.sync_get_video()[0])

delta = 10
cam = cv2.VideoCapture(0)

class Sampler:

    def __init__(self,image):
        self.img = image
        self.pt1 = None
        self.pt2 = None
        self.filter = None
        self.displayImage = image
        self.gotRoi = False

    def applyFilter(self):
		#imycrcb = cv2.cvtColor(self.img,cv.CV_BGR2YCrCb)
		imycrcb = self.img
		lowx = min(self.pt1[0],self.pt2[0])
		highx = max(self.pt1[0],self.pt2[0])
		lowy = min(self.pt1[1],self.pt2[1])
		highy = max(self.pt1[1],self.pt2[1])
		y = []
		cr = []
		cb = []

		for i in range(lowx,highx+1):
			for j in range(lowy,highy+1):
				y.append(imycrcb[i,j,0])
				cr.append(imycrcb[i,j,1])
				cb.append(imycrcb[i,j,2])

		ymean = np.mean(y)
		crmean = np.mean(cr)
		cbmean = np.mean(cb)
		ystd = np.std(y)
		crstd = np.std(cr)
		cbstd = np.std(cb)

		print (ymean,crmean,cbmean)
		print (ystd,crstd,cbstd)

		self.filter = fe.colourFilter((ymean-ystd*2*delta,crmean-crstd*delta,cbmean-cbstd*delta),(ymean+ystd*2*delta,crmean+crstd*delta,cbmean+cbstd*delta))
		hull = self.filter.getColourHull(self.img)
		print self.filter.low
		print self.filter.high

		imgray = cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)
		cv2.drawContours(imgray,[hull],-1,(255,0,0),2)
		self.displayImage = imgray



def callback(sampler):

    def onmouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if not sampler.gotRoi:
                sampler.pt1 = (y,x)
        elif event == cv2.EVENT_LBUTTONUP:
            if not sampler.gotRoi and sampler.pt1 is not None:
                sampler.pt2 = (y,x)
                sampler.applyFilter()
                sampler.gotRoi = True
        elif event == cv2.EVENT_RBUTTONDOWN:
            if sampler.gotRoi:
                pt1 = None
                pt2 = None
                sampler.gotRoi = False
                sampler.displayImage = sampler.img

    return onmouse

def getColourRange(imbgr,writer,colour):
    sampler = Sampler(imbgr)
    windowname = "Select " + colour

    cv2.namedWindow(windowname,1)
    cv2.setMouseCallback(windowname, callback(sampler))

    while 1: 
        cv2.imshow(windowname,sampler.displayImage)
        if cv2.waitKey(10) == 27:
            break

    writer.writerow(sampler.filter.low)
    writer.writerow(sampler.filter.high)

def calibrate(folderpath):

	ret, imbgr = cam.read()
	count = 0

	while not ret and count < 20:
		time.sleep(1)
		ret, imbgr = cam.read()
		count += 1
		
	with open(os.path.join(folderpath,'calibration.csv'),'w') as csvfile:
		writer = csv.writer(csvfile)
		getColourRange(imbgr,writer,"Colour")

    #cam.release()


if __name__ == "__main__":
    calibrate(os.getcwd())
