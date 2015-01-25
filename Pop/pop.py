#Imports
import cv
import cv2
import numpy as np
import math
import random
import time

#Start webcam and get camera frame dimensions
# cam = cv2.VideoCapture(0)
# width = int(cam.get(3))
# height = int(cam.get(4))

# if __name__ == "__main__":
# 	while 1:
# 		try:
# 			imbgr = cam.read()[1]
# 			imbgr = cv2.flip(imbgr, 1)

# 			cv2.imshow("Test",imbgr)


# 		#Exit with CTRL+C
# 		except KeyboardInterrupt:
# 			break
# 		if cv.WaitKey(10) == 32:
# 			break

def diffImg(t0, t1, t2):
	d1 = cv2.absdiff(t2, t1)
	d2 = cv2.absdiff(t1, t0)
	return cv2.bitwise_and(d1, d2)

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

#Normalize a 2D vector and multiply by norm_val
def normalize(x, y, norm_val):
	return norm_val*x/np.sqrt(math.pow(x,2)+math.pow(y,2)),  norm_val*y/np.sqrt(math.pow(x,2)+math.pow(y,2))

class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y

class Bubble:
	def __init__(self):
		#Choose a random value r that is between 0 and the length of the perimeter
		r = random.randint(0, 2*width + 2*height)
		self.living = True
		#Initialize location and velocity based on r
		if r < width:
			self.set_loc(r, 0)
			self.set_vel(random.randint(-v, v), random.randint(1, v))
		elif r < (width+height):
			self.set_loc(width, r-width)
			self.set_vel(random.randint(-v, -1), random.randint(-v, v))
		elif r < (2*width+height):
			self.set_loc(r-width-height, height)
			self.set_vel(random.randint(-v, v), random.randint(-v, -1)) 
		else:
			self.set_loc(0, r-height-2*width)
			self.set_vel(random.randint(1, v),random.randint(-v, v)) 

	#Set fly location
	def set_loc(self, x, y):
		self.x = x
		self.y = y

	#Set fly velocity (normalized)
	def set_vel(self, vx, vy):
		self.vx, self.vy = normalize(vx, vy, v)

	def draw_bubble(self, img):

		overlay = img.copy()
		if self.living:
			cv2.circle(overlay, (int(self.x), int(self.y)), 50, (255,255,255), -1)
		else:
			cv2.circle(overlay, (int(self.x), int(self.y)), 50, (0, 0, 0), -1)
		opacity = 0.4
		cv2.addWeighted(overlay, opacity, img, 1 - opacity, 0, img)


	#Update fly location based on last location and velocity
	def update_loc(self):
		if self.living:
			#Reverse velocity if fly hits edge of frame
			if (self.x + self.vx) <=0 or (self.x + self.vx) >=width:
				self.vx = -self.vx
			if (self.y + self.vy) <=0 or (self.y + self.vy) >=height:
				self.vy = -self.vy

			#Update location
			self.x = self.x + self.vx
			self.y = self.y + self.vy
			self.wiggle()
		else:
			if (self.y > height):
				bubbles.remove(self)
			self.vy = self.vy + 1
			self.y = self.y+self.vy

	#Cause bubble to have a wiggly flying pattern
	def wiggle(self):
		randx = 0
		randy = 0
		
		if self.x == 0:
			randx = random.randint(1, v)
		elif self.x == width:
			randx = random.randint(-v, -1)
		else:
			while randx == 0:
				randx = random.randint(-v, v)

		if self.y == 0:
			randy = random.randint(1, v)
		elif self.y == height:
			randy = random.randint(-v, -1)
		else:
			while randy == 0:
				randy = random.randint(-v, v)

		self.vx, self.vy = normalize(self.vx + 0.25*randx, self.vy + 0.25*randy, v)

cam = cv2.VideoCapture(0)
width = int(cam.get(3))
height = int(cam.get(4))
v = 10 #velocity of bubbles
winName = "Movement Indicator"
cv2.namedWindow(winName, cv2.CV_WINDOW_AUTOSIZE)
guilty_contours = []
# Read three images first:
t_minus = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)
t = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)
t_plus = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)
display_img = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)
bubbles = []
time_0 = time.clock()

while True:
	im= diffImg(t_minus, t, t_plus)
	thresh = 30
	im_bw = cv2.threshold(im, thresh, 255, cv2.THRESH_BINARY)[1]
	im_filter = blobSmoothing(im_bw)
	time_now = time.clock()
	popText = False

	contours, hierarchy = cv2.findContours(im_filter,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	goodcontours = []
	for cnt in contours:
		area = cv2.contourArea(cnt)
		if area > 100:
			goodcontours.append(cnt)

	#New bubble every 5 seconds
	if time_now - time_0 > 3:
		newBubble = Bubble()
		bubbles.append(newBubble)
		time_0 = time.clock()

	#Update and draw flies
	if len(bubbles): 
		for bubble in bubbles:
			bubble.update_loc()
			bubble.draw_bubble(display_img)
			for cnt in goodcontours:
				if (bubble.living and cv2.pointPolygonTest(cnt, (int(bubble.x), int(bubble.y)), False) > 0 ):
					bubble.living = False
					popText = True
					#print("GOT ONE")
					#guilty_contours.append(cnt)
					break

	display_img = cv2.flip(display_img,1)
	if (popText):
		cv2.putText(display_img, "POP!!", (int(bubble.x), int(bubble.y)), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 4)
	#cv2.drawContours(display_img,guilty_contours,-1,(255,0,0),-1)
	cv2.imshow( winName, display_img)

	# Read next image
	t_minus = t
	t = t_plus
	t_plus = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)
	display_img = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)

	key = cv2.waitKey(10)
	if key == 27:
		cv2.destroyWindow(winName)
		break

print "Goodbye"