import freenect
import numpy as np
import cv
import cv2

import frame_convert
import cmath
import math
import csv
import sys
import os
#import calibrate

import hashlib
import functools
import scipy.stats as stats

class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y


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

    imfilter = cv2.dilate(imfilter,0.5*kernel)
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

def group_contours(contours):
	if len(contours):
		items = []
		found = False
		#seeds = []
		#seed[0] = contours[0]
		for cnt in contours:
			M = cv2.moments(cnt)
			cx = int(M['m10']/M['m00'])
			cy = int(M['m01']/M['m00'])
			if len(items):
				for i in items:
					for i_cnt in i:
						iM = cv2.moments(i_cnt)
						icx = int(iM['m10']/iM['m00'])
						icy = int(iM['m01']/iM['m00'])
						d = np.sqrt(math.pow(icx-cx, 2)+ math.pow(icy-cy, 2))
						if d < 110:
							i.append(cnt)
							found = True
							break
					if found:
						break
				if not found:
					n = []
					n.append(cnt)
					items.append(n)
			else:
				n = []
				n.append(cnt)
				items.append(n)
		return items
	else:
		return np.array([])

#calibrate.calibrate(os.getcwd())

cam = cv2.VideoCapture(0)
width = int(cam.get(3))
height = int(cam.get(4))
outvid = cv2.VideoWriter()
outvid.open("test.avi", cv2.cv.CV_FOURCC('M','P','E','G'), 1,(width,height))
print outvid.isOpened()

last_num_items = 0
last_d = 1000
if __name__ == "__main__":
	low, high = get_colour(sys.argv[1])
	while 1:
		try:
			imbgr = cam.read()[1]
			imbgr = cv2.flip(imbgr, 1)
			imgray = cv2.cvtColor(imbgr,cv.CV_BGR2GRAY)
			imycrcb = cv2.cvtColor(imbgr,cv.CV_BGR2YCrCb)
			imfilter = inRange(imycrcb, low, high)

			imfilter = blobSmoothing(imfilter)
			contours, hierarchy = cv2.findContours(imfilter,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

			goodcontours = []
			for cnt in contours:
				area = cv2.contourArea(cnt)
				if area > 100:
					goodcontours.append(cnt)

			items = group_contours(goodcontours)
			hull_centroids = []

			if items:
				num = len(items)
				for i in items:
					hull = get_hull(i)
					cv2.drawContours(imgray,[hull],-1,(255,0,0),2)
					x,y,w,h = cv2.boundingRect(hull)
					cx = x+(w/2)
					cy = y+(h/2)
					hull_centroids.append(Point(cx, cy))

			if len(hull_centroids) == 2:
				last_d = np.sqrt(math.pow(hull_centroids[0].x-hull_centroids[1].x, 2)+ math.pow(hull_centroids[0].y-hull_centroids[1].y, 2))
			elif len(hull_centroids) == 1 and last_d < 200:
				cv2.putText(imgray, "CLAP!", (hull_centroids[0].x - 20, hull_centroids[0].y), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,0,0), 5)
				last_d = 1000
			else:
				last_d = 1000
					#cv2.rectangle(imgray,(x,y),(x+w,y+h),(0,255,0),2) 
					#cv2.circle(imgray, ((x+(w/2)), (y+(h/2))), 10, (0,0,255))
			#hull = get_hull(goodcontours)

			#cv2.drawContours(imgray,goodcontours,-1,(255,0,0),2)
			outvid.write(imgray)
			cv2.imshow("Test",imgray)


		except KeyboardInterrupt:
			outvid.release()
			break
		if cv.WaitKey(10) == 32:
			outvid.release()
			break
