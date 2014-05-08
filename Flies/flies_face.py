#Imports
import cv
import cv2
import frame_convert 
import numpy as np
import math
import random
import time

# load the c1assifiers
haarFace = cv.Load('haarcascade_frontalface_default.xml')
haarEyes = cv.Load('haarcascade_eye.xml') 

#Start webcam and get camera frame dimensions
cam = cv2.VideoCapture(0)
width = int(cam.get(3))
height = int(cam.get(4))
v = 10
#Retrieve a frame
def get_video():
    return frame_convert.video_cv(freenect.sync_get_video()[0])

#Normalize a 2D vector and multiply by norm_val
def normalize(x, y, norm_val):
	return norm_val*x/np.sqrt(math.pow(x,2)+math.pow(y,2)),  norm_val*y/np.sqrt(math.pow(x,2)+math.pow(y,2))

def face_centroid(im):
	num_eyes = 0
	eyes_in_face = []
	actual_eyes = []

	small = cv2.resize(im, (0,0), fx = 0.1, fy = 0.1)
	imsmall = cv.fromarray(small)

	# running the classifiers
	storage = cv.CreateMemStorage()
	detectedFace = cv.HaarDetectObjects(imsmall, haarFace, storage)
	#detectedEyes = cv.HaarDetectObjects(im, haarEyes, storage)

	if detectedFace:
		face = detectedFace[0]
		return 10*int(face[0][0] + 0.5*face[0][2]), 10*int(face[0][1] + 0.5*face[0][3])
	else:
		return int(width/2), int(height/2)

class Fly:
	def __init__(self):
		#Choose a random value r that is between 0 and the length of the perimeter
		r = random.randint(0, 2*width + 2*height)
		#Set velocity of all flies

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
		cv2.circle(img, (int(self.x), int(self.y)), 5, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), -1)

	#Update fly location based on last location and velocity
	def update_loc(self, img):

		#Reverse velocity if fly hits edge of frame
		if (self.x + self.vx) <=0 or (self.x + self.vx) >=width:
			self.vx = -self.vx
		if (self.y + self.vy) <=0 or (self.y + self.vy) >=height:
			self.vy = -self.vy

		#Update location
		self.x = self.x + self.vx
		self.y = self.y + self.vy

		self.swarm(img)
		self.wiggle()

	#Cause fly to curve towards frame centre
	def swarm(self, img):
		#Set curvature
		c = 0.1

		face_x, face_y = face_centroid(img)
		#cv2.circle(img, (face_x, face_y), 30, (255, 255, 255), -1)

		#may need to check for 0s
		self.vx += (face_x - self.x)*c
		self.vy += (face_y - self.y)*c

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

count = 0
flies = []
time_0 = time.clock()

if __name__ == "__main__":
		while 1:
			try:
				imbgr = cam.read()[1]
				imbgr = cv2.flip(imbgr, 1)

				time_now = time.clock()

				#New fly every 1 second
				if time_now - time_0 > 1:
					newfly = Fly()
					flies.append(newfly)
					time_0 = time.clock()

				#Update and draw flies
				if len(flies): 
					for fly in flies:
						fly.update_loc(imbgr)
						fly.draw_fly(imbgr)

				cv2.imshow("Flies",imbgr)

			#Exit with CTRL+C
			except KeyboardInterrupt:
				break
			if cv.WaitKey(10) == 32:
				break