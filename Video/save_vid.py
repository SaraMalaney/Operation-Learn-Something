import cv2
import cv
import sys
import time
import datetime
import thread

cam = cv2.VideoCapture(0)

im = cam.read()[1]
#height , width , layers =  im.shape

#video = cv2.VideoWriter('video.avi',-1,1,(width,height))

vidList = []
num_vids = 0
print num_vids

def recordNew():
	print 'This is working'
	global num_vids
	#name = 'vid_' + str(num_vids)
	#vars()[name] = []
	#print name
	newVid = []

	for i in range (0, 30):
		im = cam.read()[1]
		time.sleep(0.1)
		newVid.append(im)
		print i

	vidList.append(newVid)
	num_vids += 1

def showVids():
	while 1:
		try:
			winNames = []
			if vidList:
				for v in vidList:
					#name = 'Sample_' + str(vidList.index(v))
					winNames.append('Sample_' + str(vidList.index(v)))
					cv2.namedWindow('Sample_' + str(vidList.index(v)))

				for i in range (0, 30):
					for v in vidList:
						cv2.imshow(winNames[vidList.index(v)], v[i])
					time.sleep(0.1)
		except KeyboardInterrupt:
			break


try:
	thread.start_new_thread(showVids, ())
except:
	print "Error: unable to start thread"

while 1:
	try:

		im = cam.read()[1]
		cv2.imshow('Test', im)
	except KeyboardInterrupt:
		break
	if cv.WaitKey(10) == 32:
		thread.start_new_thread(recordNew, ())

	
	#cv.WriteFrame(writer, im)

	#video.write(im)
	#ts = time.time()
	#st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H:%M:%S')
	#cv2.imwrite(st+'.png',imbgr)
	#time.sleep(1)

#cv2.destroyAllWindows()
#video.release()

#del writer # this makes a working AVI