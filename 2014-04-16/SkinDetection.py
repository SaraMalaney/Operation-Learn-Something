import cv
import cv2
import numpy as np 
from PIL import Image
 
# load the c1lassifiers
haarFace = cv.Load('haarcascade_frontalface_default.xml')
haarEyes = cv.Load('haarcascade_eye.xml')        

def blobSmoothing(immask):
    imfilter = cv2.medianBlur(immask,7)
    imfilter = cv2.medianBlur(imfilter,5)
    imfilter = cv2.medianBlur(imfilter,3)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))

    imfilter = cv2.dilate(imfilter,kernel)
    imfilter = cv2.erode(imfilter,kernel)
    return imfilter

def skinColour(im, pointA, pointB):
    r = []
    g = []
    b = []

    for i in range(pointA[0], pointB[0]):
        for j in range(pointA[1], pointB[1]):
            r.append(im[i,j,0])
            g.append(im[i,j,1])
            b.append(im[i,j,2])

    rmean = np.mean(r)
    gmean = np.mean(g)
    bmean = np.mean(b)
    rstd = np.std(r)
    gstd = np.std(g)
    bstd = np.std(b)
    
    means = (rmean, gmean, bmean)
    stds = (rstd, gstd, bstd)
    
    return means, stds

def faceFind(im, imycrcb, detectedEyes, detectedFace):
    num_eyes = 0
    eyes_in_face = []
    actual_eyes = []
 
    if detectedFace:
        for face in detectedFace:
     
            #only take eyes in face
            for eye in detectedEyes:
                if eye[0][0] >= face[0][0] and eye[0][1] >= face[0][1] and (eye[0][0] + eye[0][2]) <= (face[0][0]+face[0][2]) and (eye[0][1] + eye[0][3]) <= (face[0][1]+face[0][3]):
                    eyes_in_face.append(eye)
                    num_eyes += 1
     
            #If more than two eyes are found, find the pair of eyes closest in size, ignore other eyes
            if len(eyes_in_face) > 2:
                diffs = []
                index_1 = []
                index_2 = []
                for e in range(0, len(eyes_in_face) - 1):
                    for x in range(e+1, len(eyes_in_face)):
                        diff = abs(eyes_in_face[e][0][2] - eyes_in_face[x][0][2])
                        index_1.append(e)
                        index_2.append(x)
                        diffs.append(diff)
                i = diffs.index(min(diffs))
                actual_eyes.append(eyes_in_face[index_1[i]])
                actual_eyes.append(eyes_in_face[index_2[i]])
            else:
                actual_eyes = eyes_in_face
     
            if num_eyes > 0:
                user_face = face
                user_eyes = actual_eyes
                break
       
            eyes_in_face = []
            actual_eyes = []
        if user_eyes:
            eye = user_eyes[0]
            #pointA = (int(eye[0][0] + (0.25*eye[0][2])), int(eye[0][1] + eye[0][3]))
            #pointB = (int(eye[0][0] + (0.75*eye[0][2])), int(eye[0][1] + (1.5*eye[0][3])))
            pointA = (int(eye[0][0]), int(eye[0][1] + eye[0][3]))
            pointB = (int(eye[0][0] + (eye[0][2])), int(eye[0][1] + (2*eye[0][3])))
            cv.Rectangle(im,pointA,pointB, cv.RGB(155, 55, 200),2)
            means, stds = skinColour(imycrcb, pointA, pointB)
        else:
            means = 0
            stds = 0
    else:
            means = 0
            stds = 0
    return means, stds

im = cv.LoadImage('gradball.jpg')
imColor = cv2.imread('gradball.jpg')
winName = "Skin Detection"
cv2.namedWindow(winName, cv2.CV_WINDOW_AUTOSIZE)

means = 0
stds = 0
delta = 2

# running the classifiers
storage = cv.CreateMemStorage()
detectedFace = cv.HaarDetectObjects(im, haarFace, storage)
detectedEyes = cv.HaarDetectObjects(im, haarEyes, storage)

imycrcb = cv2.cvtColor(imColor,cv.CV_RGB2YCrCb)
means, stds = faceFind(im, imycrcb, detectedEyes, detectedFace)

low = (means[0]-stds[0]*2*delta, means[1]-stds[1]*2*delta, means[2]-stds[2]*2*delta)
high = (means[0]+stds[0]*2*delta, means[1]+stds[1]*2*delta, means[2]+stds[2]*2*delta)

#imgray = cv2.cvtColor(imColor, cv2.COLOR_RGB2GRAY)

imycrcb_bw = cv2.inRange(imycrcb, low, high)
imycrcb_bw  = blobSmoothing(imycrcb_bw)
contours, hierarchy = cv2.findContours(imycrcb_bw,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(imycrcb, contours, -1,(255,0,0),2)

cv2.imshow( winName, imycrcb)
cv.ShowImage('Face Detection', im)

#cv.ShowImage(winName, im)
cv.WaitKey()