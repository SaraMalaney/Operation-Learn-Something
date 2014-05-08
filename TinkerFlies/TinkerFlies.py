import featureExtraction as fe
import numpy as np 
import frame_convert
import os
import sys
import cv2
import time
#import cv
import csv
import time
import copy
import math
import threading
import random

def lay_out_game():
	title = Displayer(0) #title
	title.play()
	findCamera = Displayer(1) #setting up webcam
	findCamera.play()
	calibrate = Displayer(2) #calibration
	calibrate.play()
	game = Displayer(3) #game
	game.play()

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

#Normalize a 2D vector and multiply by norm_val
def normalize(x, y, norm_val):
	return norm_val*x/np.sqrt(math.pow(x,2)+math.pow(y,2)),  norm_val*y/np.sqrt(math.pow(x,2)+math.pow(y,2))

#cam = cv2.VideoCapture(0)
cam = None
escapekey = 27
continuekey = 32
tickCount = 0
currentDisplayer = None

#These are set up when the webcam loads (Displayer called with 1 as arg)
width = 0
height = 0

class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y

class Fly:
	def __init__(self):
		#Choose a random value r that is between 0 and the length of the perimeter
		r = random.randint(0, 2*width + 2*height)
		#Set velocity of all flies
		self.v = 10
		v = self.v
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
		self.vx, self.vy = normalize(vx, vy, self.v)

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
			self.vy = self.vy + gravity
			self.y = self.y+self.vy

	#Cause fly to curve towards frame centre
	def swarm(self):
		#Set curvature
		c = 0.01

		#may need to check for 0s
		self.vx += (width/2 - self.x)*c
		self.vy += (height/2 - self.y)*c

		self.vx, self.vy = normalize(self.vx, self.vy, self.v)

	#Cause fly to have a wiggly flying pattern
	def wiggle(self):
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
		
class Upgrade:
	def __init__(self):
		self.x = random.randint(0, width)
		self.y = random.randint(0, height)
		self.vy = 0
		self.phase = 0
		self.type = 0 #assign to a random once they do something and there are multiple types
		self.living = True
		
	def draw_upgrade(self, img):
		p = self.phase
		color = []
		if self.living:
			self.phase = self.phase + 1
			#add an if statement for these once there are multiple types
			color[0] = int(127*math.sin(p/10)+127)
			color[1] = int(127*math.sin(p/10-2)+127)	#close enough to 2pi/3
			color[1] = int(127*math.sin(p/10-4)+127)	#close enough to 4pi/3
		else:
			self.vy = self.vy + gravity
			self.y += self.vy
			color = [0, 0, 0]
		radius = int((p-2/3)(p-15)(p-15)/30+5) if p < 20 else 10*math.sin((p-20)/2)+20
		cv2.circle(img, self.x, self.y, radius, (color[0], color[1], color[2]), -1)


# class Ticker(threading.Thread):
	# def __init__(self, tickrate):
		# threading.Thread.__init__(self)
		# self.tickrate = tickrate
		
	# def run(self):
		# global tickCount
		# while 1:
			# print "hello!"
			# tickCount +=1
			# time.sleep(1/tickrate)
			# if cv2.waitKey(10) == escapekey:		#This might be part of the problem but it's certainly not all of it. Do I need a queue?
					# break
					
#Apparently in Notepad++, ctrl-Q comments out large sections. Cool.


class Displayer:

	def __init__(self, type):
		self.type = type
		self.currentFrame = cv2.imread('nullFrameError.png')
		self.lastFrameTime = 0
		global currentDisplayer
		currentDisplayer = self
		
#	def draw_circle(self, x, y, rad, color)
#		#Eventually check self.width and self.height to make sure it can contain it probably
#		cv2.circle(self.currentFrame, x, y, rad, color, -1)

	def play(self):

		windowname = "TinkerFlies (flies_hands rewritten for Owen's stupid computer using Owen's stupid methods)"
		
		if self.type is 0: #title
			self.baseFrame = cv2.imread('title.png')
		elif self.type is 1:
			cv2.imshow(windowname, cv2.imread('title.png')) #I'll make a loading image later.
			#Do I need a dummy displayer or something to show it? It's showing the title with the fps meter! It DOES know the dimensions, though
			global cam
			cam = cv2.VideoCapture(0)
			ret, imbgr = cam.read()
			count = 0
			while not ret and count < 10:
				ret, imbgr = cam.read()
				if count < 5:
					print "Warming up the webcam..."+("("+str(count+1)+")" if count is not 0 else "")
				elif count%2 is 0:
					print "Hmm. Let's keep trying for a bit, but there might be a problem. ("+str(count/2+3)+")"
				count += 1
				time.sleep(1)
			if ret:
				global width
				global height
				width = int(cam.get(3))
				height = int(cam.get(4))
			else:
				sys.exit("Drat! No camera input was found.")
		elif self.type is 3:
			#ticker = Ticker(30)
			#Does not work
			count = 0
			flies = []
			upgrades = []
			time_0 = time.clock()
			display_smoosh = 0
			
			flies_caught = 0
			
			low, high = get_colour("calibration.csv")
			last_num_items = 0
			last_d = 1000
			
		self.width = self.currentFrame.shape[1]
		self.height = self.currentFrame.shape[0]

		while 1: 
			if self.type is 1: #webcam loading - already done
				break
			fps = round(1/(time.clock()-self.lastFrameTime), 2) #I think time.clock() resets when you break from this for some reason
			self.lastFrameTime = time.clock()
			if self.type is 0:
				self.currentFrame = copy.copy(self.baseFrame)
				cv2.putText(self.currentFrame, str(fps)+" fps", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1)
				if cv2.waitKey(10) == continuekey:
					break
			elif self.type is 3: #game - 1 will be camera loading, 2 will be calibration.
				if time.clock() - time_0 > 1:
					newfly = Fly()
					flies.append(newfly)
					time_0 = time.clock()
			
				nextFrame = cv2.flip(cam.read()[1], 1)
				
				if len(flies): 
					for fly in flies:
						fly.update_loc()
						fly.draw_fly(nextFrame)
						
				if len(upgrades):
					for upgrade in upgrades:
						upgrade.draw_upgrade(nextFrame)
				
				imfilter = cv2.inRange(nextFrame, low, high)
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
						cv2.drawContours(nextFrame,[hull],-1,(255,0,0),2)
						x,y,w,h = cv2.boundingRect(hull)
						cx = x+(w/2)
						cy = y+(h/2)
						hull_centroids.append(Point(cx, cy))
				if len(hull_centroids) == 2:
					last_d = np.sqrt(math.pow(hull_centroids[0].x-hull_centroids[1].x, 2)+ math.pow(hull_centroids[0].y-hull_centroids[1].y, 2))
				elif len(hull_centroids) == 1 and last_d < 150+int(500/fps):
					cv2.putText(nextFrame, "CLAP!", (hull_centroids[0].x - 20, hull_centroids[0].y), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,0,0), 5)
					if len(upgrades): #Upgrades must be checked before upgrades.append in the fly checker
						for upgrade in upgrades:
							if upgrade.x < hull_centroids[0].x+rad and upgrade.x > hull_centroids[0].x-rad and upgrade.y < hull_centroids[0].y+rad and upgrade.y > hull_centroids[0].y-rad and upgrade.living:
								upgrade.living = False
								#This is where to put or call any benefit code from an upgrade
					if len(flies): 
						for fly in flies:
							if fly.x < hull_centroids[0].x+rad and fly.x > hull_centroids[0].x-rad and fly.y < hull_centroids[0].y+rad and fly.y > hull_centroids[0].y-rad and fly.living:
								flies_caught += 1
								fly.living = False
								if flies_caught%10 == 0:
									upgrade = Upgrade()
									upgrades.append(upgrade)
					display_smoosh += 1
					if display_smoosh > 4:
						last_d = 0
				else:
					last_d = 1000
				cv2.putText(nextFrame, str(fps)+" fps", (560, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
				cv2.putText(nextFrame, str(flies_caught), (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 3)
				self.currentFrame = nextFrame
				#print tickCount
				if cv2.waitKey(10) == escapekey:
					break
			else:
				if cv2.waitKey(10) == continuekey:
					break
			cv2.imshow(windowname,self.currentFrame)

		#cam.release()


if __name__ == "__main__":
	lay_out_game()