import cv2
import cv
import numpy as np
from matplotlib import pyplot as plt
import sys
import csv

def get_colour(calibration):
	with open(calibration) as csvfile:
		reader = csv.reader(csvfile)
		low = [ float(x) for x in reader.next()]
		high = [ float(x) for x in reader.next()]
	return tuple(low), tuple(high)

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

#low, high = get_colour(sys.argv[1])

cam = cv2.VideoCapture(0)

if __name__ == "__main__":
	low, high = get_colour(sys.argv[1])
	while 1:
		try:
			ret, imbgr = cam.read()
			imbgr = cv2.flip(imbgr, 1)
			#imbgr = cv2.medianBlur(imbgr, 5)
			#imycrcb = cv2.cvtColor(imbgr,cv.CV_BGR2YCrCb)
			#imgray = cv2.cvtColor(imbgr, cv.CV_BGR2GRAY)

			imycrcb = cv2.cvtColor(imbgr,cv.CV_BGR2YCrCb)
			imfilter = cv2.inRange(imycrcb, low, high)
			imfilter = blobSmoothing(imfilter)
			contours, hierarchy = cv2.findContours(imfilter,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
			hull = get_hull(contours)
			if len(hull) != 0:
				x,y,w,h = cv2.boundingRect(hull)
				cv2.rectangle(imbgr,(x,y),(x+w,y+h),(0,255,0),2) 
			cv2.drawContours(imbgr,[hull],-1,(255,0,0),2)



			cv2.imshow("Test",imbgr)

		#Exit with CTRL+C
		except KeyboardInterrupt:
			break
		if cv.WaitKey(10) == 32:
			break
