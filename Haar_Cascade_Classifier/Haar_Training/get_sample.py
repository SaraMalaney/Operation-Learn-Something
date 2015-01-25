import numpy as np
import cv
import cv2
import sys
import time
import datetime

cam = cv2.VideoCapture(0)


for i in range (0, 10):
	imbgr = cam.read()[1]
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H:%M:%S')
	cv2.imwrite(st+'.png',imbgr)
	print i
	time.sleep(1)






