import numpy as np
import cv2
import cv 
img = cv2.imread("maze_2.jpg")
#img_gray = cv2.cvtColor(img,cv.CV_BGR2GRAY)
#ret,thresh1 = cv2.threshold(img,100,255,cv2.THRESH_BINARY)
#img_bw = 255 - thresh1
#copy = img_bw


red = cv2.inRange(img,np.array((0,0,120)),np.array((30,30,255)))
#cv2.imshow("TEST",red)

contours,h = cv2.findContours(red,1,2)

for cnt in contours:
    apprqox = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
    print len(approx)
    if len(approx)==4:
        print "square"
        cv2.drawContours(img,[cnt],0,(0,0,255),-1)
    elif len(approx) > 15:
        print "circle"
        cv2.drawContours(img,[cnt],0,(0,255,255),-1)

cv2.imshow('img',img)
cv2.waitKey(0)
cv2.destroyAllWindows()

#contours, hierarchy = cv2.findContours(img_bw,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
#img_final = cv2.cvtColor(img_bw, cv.CV_GRAY2BGR)

#cv2.drawContours(img_final,contours,-1,(255,0,0),1)

#cnt = contours[0]
# for i in range (0,len(contours)-1):
# 	cnt = contours[i]
# 	cv2.drawContours(img_final,cnt,-1,(255,0,0),1)
# 	hull = cv2.convexHull(cnt,returnPoints = False)
# 	defects = cv2.convexityDefects(cnt,hull)
# 	print "defects: " + str(defects.size)

# 	cv2.imshow("Test", img_final)
# 	cv.WaitKey(0)