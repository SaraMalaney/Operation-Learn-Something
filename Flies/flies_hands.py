#Imports
import cv
import cv2
import frame_convert 
import numpy as np
import math
import random
import time
import csv
import sys
import os
import hashlib
import functools
import scipy.stats as stats

#Start webcam and get camera frame dimensions
cam = cv2.VideoCapture(0)
width = int(cam.get(3))
height = int(cam.get(4))
v = 10 #velocity of flies

#Retrieve a frame
def get_video():
    return frame_convert.video_cv(freenect.sync_get_video()[0])

#Normalize a 2D vector and multiply by norm_val
def normalize(x, y, norm_val):
	return norm_val*x/np.sqrt(math.pow(x,2)+math.pow(y,2)),  norm_val*y/np.sqrt(math.pow(x,2)+math.pow(y,2))

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

class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y

class Upgrade:
	def __init__(self):
		self.x = random.randint(0, width)
		self.y = random.randint(0, height)
		
	def draw_upgrade(self, type):
		cv2.circle(img, (int(self.x), int(self.y)), 25, (0, 0, 0), -1)

class Fly:
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

	def draw_fly(self, img):
		if self.living:
			cv2.circle(img, (int(self.x), int(self.y)), 5, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), -1)
		else:
			cv2.circle(img, (int(self.x), int(self.y)), 5, (0, 0, 0), -1)


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

			self.swarm()
			self.wiggle()
		else:
			if (self.y > height):
				flies.remove(self)
			self.vy = self.vy + 1
			self.y = self.y+self.vy

	#Cause fly to curve towards frame centre
	def swarm(self):
		#Set curvature
		c = 0.01

		#may need to check for 0s
		self.vx += (width/2 - self.x)*c
		self.vy += (height/2 - self.y)*c

		self.vx, self.vy = normalize(self.vx, self.vy, v)

	#Cause fly to have a wiggly flying pattern
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

		self.vx, self.vy = normalize(self.vx + 0.75*randx, self.vy + 0.75*randy, v)

count = 0
flies = []
time_0 = time.clock()
flies_caught = 0
rad = 100

last_num_items = 0
last_d = 1000

display_smoosh = 0


if __name__ == "__main__":
	low, high = get_colour(sys.argv[1])
	while 1:
		try:
			imbgr = cv2.flip(cam.read()[1], 1)

			imycrcb = cv2.cvtColor(imbgr,cv.CV_BGR2YCrCb)
			imfilter = inRange(imycrcb, low, high)

			time_now = time.clock()

			if display_smoosh and display_smoosh < 5:
				cv2.putText(imbgr, "SQUISH!", (smoosh_loc.x, smoosh_loc.y), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 4)
				display_smoosh += 1

			#New fly every 1 second
			if time_now - time_0 > 1:
				newfly = Fly()
				flies.append(newfly)
				time_0 = time.clock()

			#Update and draw flies
			if len(flies): 
				for fly in flies:
					fly.update_loc()
					fly.draw_fly(imbgr)

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
					#cv2.drawContours(imbgr,[hull],-1,(255,0,0),2)
					x,y,w,h = cv2.boundingRect(hull)
					cx = x+(w/2)
					cy = y+(h/2)
					hull_centroids.append(Point(cx, cy))

			if len(hull_centroids) == 2:
				last_d = np.sqrt(math.pow(hull_centroids[0].x-hull_centroids[1].x, 2)+ math.pow(hull_centroids[0].y-hull_centroids[1].y, 2))
			elif len(hull_centroids) == 1 and last_d < 200:
				#cv2.putText(imbgr, "CLAP!", (hull_centroids[0].x - 20, hull_centroids[0].y), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,0,0), 5)
				if len(flies): 
					for fly in flies:
						if fly.x < hull_centroids[0].x+rad and fly.x > hull_centroids[0].x-rad and fly.y < hull_centroids[0].y+rad and fly.y > hull_centroids[0].y-rad and fly.living:
							flies_caught += 1
							fly.living = False
							#cv2.putText(imbgr, "SQUISH!", (hull_centroids[0].x - 20, hull_centroids[0].y), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 4)
							smoosh_loc = Point( hull_centroids[0].x - 20, hull_centroids[0].y)
							display_smoosh = 1
					
				last_d = 1000
			else:
				last_d = 1000
			cv2.putText(imbgr, str(flies_caught), (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 3)
			cv2.imshow("Flies",imbgr)

		#Exit with CTRL+C
		except KeyboardInterrupt:
			break
		if cv.WaitKey(10) == 32:
			break