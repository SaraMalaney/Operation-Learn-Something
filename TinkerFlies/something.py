
import cv2
import csv
import sys
import time

cam = cv2.VideoCapture(0)

#def get_colour(calibration):
#    with open(calibration) as csvfile:
#        reader = csv.reader(csvfile)
#        low = [ float(x) for x in reader.next()]
#        high = [ float(x) for x in reader.next()]
#    return tuple(low), tuple(high)

im = cv2.imread('48tyG-postshop.jpg')

ret, input = cam.read()
count = 0

while not ret and count < 20:
	time.sleep(1)
	ret, input = cam.read()
	count += 1
imbgr = cv2.flip(input[1], 1)

#low, high = get_colour(sys.argv[1])
#print low[1]
#imtest = cv2.inRange(imbgr, low, high)
while 1: 
	cv2.imshow("something",imbgr)
	if cv2.waitKey(10) == 27:
		break