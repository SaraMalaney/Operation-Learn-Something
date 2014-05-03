import freenect
import numpy as np
import cv
import cv2

import frame_convert
import cmath
import math
import random
import csv
import sys
import os
import time
#import calibrate

import hashlib
import functools
import scipy.stats as stats

cam = cv2.VideoCapture(0)
width = int(cam.get(3))
height = int(cam.get(4))

def get_video():
    return frame_convert.video_cv(freenect.sync_get_video()[0])

def normalize(x, y, norm_val):
	return norm_val*x/np.sqrt(math.pow(x,2)+math.pow(y,2)),  norm_val*y/np.sqrt(math.pow(x,2)+math.pow(y,2))

class Fly:

	def __init__(self):

		r = random.randint(0, 2*width + 2*height)
		self.v = 10

		if r < width:
			self.set_loc(r, 0)
			self.set_vel(random.randint(-10, 10), random.randint(1, 10))
		elif r < (width+height):
			self.set_loc(width, r-width)
			self.set_vel(random.randint(-10, -1), random.randint(-10, 10))
		elif r < (2*width+height):
			self.set_loc(r-width-height, height)
			self.set_vel(random.randint(-10, 10), random.randint(-10, -1)) 
		else:
			self.set_loc(0, r-height-2*width)
			self.set_vel(random.randint(1, 10),random.randint(-10, 10)) 

		#print "x: " + str(self.x) + " y: " + str(self.y)

	def set_loc(self, x, y):
		self.x = x
		self.y = y

	def set_vel(self, vx, vy):
		self.vx = 5*vx/np.sqrt(math.pow(vx, 2) + math.pow(vy, 2))
		self.vy = 5*vy/np.sqrt(math.pow(vx, 2) + math.pow(vy, 2))

	def draw_fly(self, img):
		cv2.circle(img, (int(self.x), int(self.y)), 5, (255, 0, 0), -1)

	def update_loc(self):

		if (self.x + self.vx) <=0 or (self.x + self.vx) >=width:
			self.vx = -self.vx
		if (self.y + self.vy) <=0 or (self.y + self.vy) >=height:
			self.vy = -self.vy

		self.x = self.x + self.vx
		self.y = self.y + self.vy

	def update_loc_curve(self):
		c = 0.01

		#may need to check for 0s
		self.vx += (width/2 - self.x)*c
		self.vy += (height/2 - self.y)*c

		self.vx, self.vy = normalize(self.vx, self.vy, self.v)

		#self.update_loc()

	def update_loc_wiggle(self):
		randx = 0
		randy = 0
		if self.x == 0:
			randx = random.randint(1, 10)
		elif self.x == width:
			randx = random.randint(-10, -1)
		else:
			while randx == 0:
				randx = random.randint(-10, 10)


		if self.y == 0:
			randy = random.randint(1, 10)
		elif self.y == height:
			randy = random.randint(-10, -1)
		else:
			while randy == 0:
				randy = random.randint(-10, 10)

		self.vx, self.vy = normalize(self.vx + 0.75*randx, self.vy + 0.75*randy, self.v)

		self.update_loc_curve()

		self.update_loc()

count = 0
flies = []
time_0 = time.clock()
if __name__ == "__main__":
		while 1:
			try:
				imbgr = cam.read()[1]
				imbgr = cv2.flip(imbgr, 1)
				imgray = cv2.cvtColor(imbgr,cv.CV_BGR2GRAY)

				time_now = time.clock()

				if time_now - time_0 > 1:
					newfly = Fly()
					flies.append(newfly)
					time_0 = time.clock()

				if len(flies): 
					for fly in flies:
						fly.update_loc_wiggle()
						fly.draw_fly(imgray)

				cv2.imshow("Flies",imgray)

			except KeyboardInterrupt:
				outvid.release()
				break
			if cv.WaitKey(10) == 32:
				outvid.release()
				break