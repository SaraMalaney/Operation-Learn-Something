import cv2
import cv
import numpy as np

# load the c1assifiers
haarFace = cv.Load('haarcascade_frontalface_default.xml')
haarEyes = cv.Load('haarcascade_eye.xml') 

cam = cv2.VideoCapture(0)

class Face:
	def __init__(self, x, y, w):
		self.x = x
		self.y = y
		self.w = w

def draw_hat(im, x, y, width):
	height = int(width/3)
	y = int(y - width/5)
	cv2.rectangle(im,(x, y), (x+width, y+height) ,(0,0,0),-1)
	cv2.rectangle(im, (int(x + width/4), int(y - .25*width)), (int(x + 3*width/4), y), (0, 0, 0), -1) 

def face_find(im):
	num_eyes = 0
	eyes_in_face = []
	actual_eyes = []

	r = 0.4

	small = cv2.resize(im, (0,0), fx = r, fy = r)
	imsmall = cv.fromarray(small)

	# running the classifiers
	storage = cv.CreateMemStorage()
	detectedFace = cv.HaarDetectObjects(imsmall, haarFace, storage)
	#detectedEyes = cv.HaarDetectObjects(im, haarEyes, storage)

	faces = []
	if detectedFace:
		for face in detectedFace:
			newface = Face(int(1/r*face[0][0]), int(1/r*face[0][1]), int(1/r*face[0][2]))
			faces.append(newface)
		return faces
	else:
		return np.array([])

if __name__ == "__main__":
		while 1:
			try:
				imbgr = cam.read()[1]
				imbgr = cv2.flip(imbgr, 1)

				faces = face_find(imbgr)
				if faces:
					for face in faces:
						draw_hat(imbgr, face.x, face.y, face.w)

				cv2.imshow("Hat",imbgr)

			except KeyboardInterrupt:
				break
			if cv.WaitKey(10) == 32:
				break