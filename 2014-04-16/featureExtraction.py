#!/usr/bin/env python
import freenect
import numpy as np
import cv
import cv2

import frame_convert
import cmath
import math
import csv

import hashlib
import functools
import scipy.stats as stats

smoothing_memory = 5

class memoize(object):
    def __init__(self, func):
       self.func = func
       self.cache = {}
       self.oldhash = None
    def __call__(self, *args):
        if not len(args) == 2 or not isinstance(args[1],np.ndarray):
            return self.func(*args)
        newhash = hashlib.sha1(np.array(args[1]).view(np.uint8)).hexdigest()
        if not newhash == self.oldhash:
            self.cache = {}
            self.oldhash = newhash
        if args[0] not in self.cache:
            self.cache[args[0]] = self.func(*args)
        return self.cache[args[0]]
    def __get__(self, obj, objtype):
        return functools.partial(self.__call__, obj)

def get_depth():
    return frame_convert.pretty_depth_cv(freenect.sync_get_depth()[0])


def get_video():
    return frame_convert.video_cv(freenect.sync_get_video()[0])

def toCVMat(im,channels):
    image = cv.CreateImage((im.shape[1], im.shape[0]),
                                 cv.IPL_DEPTH_8U,
                                 channels)
    cv.SetData(image, im.tostring(),
               im.dtype.itemsize * channels * im.shape[1])
    return image

class colourFilter: 

    def __init__(self,low,high):
        self.low = low
        self.high = high

    @memoize
    def getColourHull(self,imbgr):
        contours = self.getColourContours(imbgr)
        if len(contours):
            mergeContour = contours[0]
            for i in contours[1:]:
                mergeContour = np.concatenate((mergeContour,i))

            return cv2.convexHull(mergeContour)
        else:
            return np.array([])

    def getStartingPoint(self,imbgr):
        contours = self.getColourContours(imbgr) 
        if len(contours):
            moments = cv2.moments(contours[0])
            if moments['m00'] > 0:
                return (int(moments['m10']/moments['m00']),int(moments['m01']/moments['m00'])) 
        return tuple([])

    @memoize
    def inRange(self,imbgr):
        imycrcb = cv2.cvtColor(imbgr,cv.CV_BGR2YCrCb)
        imfilter = cv2.inRange(imycrcb,self.low,self.high)
        return imfilter

    def blobSmoothing(self,immask):
        imfilter = cv2.medianBlur(immask,7)
        imfilter = cv2.medianBlur(imfilter,5)
        imfilter = cv2.medianBlur(imfilter,3)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))

        imfilter = cv2.dilate(imfilter,kernel)
        imfilter = cv2.erode(imfilter,kernel)
        return imfilter

    @memoize
    def getColourContours(self,imbgr):
        imfilter = self.inRange(imbgr)
        imfilter = self.blobSmoothing(imfilter)

        contours, hierarchy = cv2.findContours(imfilter,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def getCombinedHull(self,imbgr,blue):
        imfilter = self.inRange(imbgr) + blue.inRange(imbgr)
        imfilter = self.blobSmoothing(imfilter)

        contours, hierarchy = cv2.findContours(imfilter,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        start = self.getStartingPoint(imbgr)

        if start:
            for cnt in contours:
                if cv2.pointPolygonTest(cnt,start,False) == 1:
                    break
            fingers = self.getColourContours(imbgr)
            for i in fingers:
                cnt = np.concatenate((cnt,i))
            return cv2.convexHull(cnt)
        return np.array([])        

    def getCombinedCentroid(self, imbgr, blue):
        imfilter = self.inRange(imbgr) + blue.inRange(imbgr)
        imfilter = self.blobSmoothing(imfilter)

        contours, hierarchy = cv2.findContours(imfilter,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        start = self.getStartingPoint(imbgr)

        if start:
            for cnt in contours:
                if cv2.pointPolygonTest(cnt,start,False) == 1:
                    break
            fingers = self.getColourContours(imbgr)
            for i in fingers:
                cnt = np.concatenate((cnt,i))
            moments = cv2.moments(cnt)
            if moments['m00'] > 0:
                return np.array([int(moments['m10']/moments['m00']),int(moments['m01']/moments['m00'])])
        return np.array([])


class FeatureExtractor:

    def __init__(self,calibration):
        self.markers = {}
        with open(calibration) as csvfile:
            reader = csv.reader(csvfile)
            low = [ float(x) for x in reader.next()]
            high = [ float(x) for x in reader.next()]
            self.markers['right'] = colourFilter(tuple(low),tuple(high))

            low = [ float(x) for x in reader.next()]
            high = [ float(x) for x in reader.next()]
            self.markers['glove'] = colourFilter(tuple(low),tuple(high))

            low = [ float(x) for x in reader.next()]
            high = [ float(x) for x in reader.next()]
            self.markers['left'] = colourFilter(tuple(low),tuple(high))
        self.features = np.array([])
        self.memory = np.array([])
        self.timeline = np.array([])

    def getHandPosition(self,imbgr,imdepth,hand):
        centroid = self.markers[hand].getCombinedCentroid(imbgr, self.markers['glove'])
        if centroid.size:
            return centroid
        return np.array([np.nan,np.nan])

    #this one is a bit hacky
    def getVelocity(self,centroid,hand):
        if not self.memory.size:
            return [np.nan,np.nan]

        time_diff = float(self.timeline[-1] - self.timeline[-2])
        lastcentroid = [np.nan,np.nan]
        if hand == 'left':
            lastcentroid = self.memory[-1,(14,15)]
        if hand == 'right':
            lastcentroid = self.memory[-1,(16,17)]

        position_diff = centroid-lastcentroid
        return position_diff / time_diff

    def getCentroidDistance(self,imbgr,hand):
        centroid = self.markers[hand].getCombinedCentroid(imbgr, self.markers['glove'])
        hull = self.markers[hand].getColourHull(imbgr)
        if centroid.size and len(hull):
            moments = cv2.moments(hull)
            finger_centroid = np.array([int(moments['m10']/moments['m00']),int(moments['m01']/moments['m00'])])
            return finger_centroid - centroid
        return np.array([np.nan,np.nan])

    def getCentralMoments(self,imbgr,hand):
        hull = self.markers[hand].getColourHull(imbgr)
        if len(hull):
            m = cv2.moments(hull)
            feature = [m['nu20'],m['nu11'],m['nu02'],m['nu30'],m['nu21'],m['nu12'],m['nu03']]
        else:
            feature = [0,0,0,0,0,0,0]
        return feature,hull

    def getCombinedMoments(self,imbgr,hand):
        hull = self.markers[hand].getCombinedHull(imbgr, self.markers['glove'])
        if len(hull):
            m = cv2.moments(hull)
            feature = [m['nu20'],m['nu11'],m['nu02'],m['nu30'],m['nu21'],m['nu12'],m['nu03']]
        else:
            feature = [0,0,0,0,0,0,0]
        return feature,hull

    def getHuMoments(self,imbgr,hand):
        hull = self.markers[hand].getColourHull(imbgr)
        if len(hull):
            m = cv2.moments(hull)
            hu = cv2.HuMoments(m)
            feature = []
            for i in hu:
                feature.append(i[0])
        else:
            feature = [0,0,0,0,0,0,0]
        return feature,hull

    def setStartPoint(self):
        self.features = np.array([])
        self.memory = np.array([])
        self.timeline = np.array([])

    #may eventually want some interface to specify which features to include
    def rawFeatureVector(self,imbgr,imdepth):
        v = np.array([])
        leftmoments,_ = self.getCentralMoments(imbgr,'left') #0-6
        rightmoments,_ = self.getCentralMoments(imbgr,'right') #7-13
        v = np.append(v,leftmoments)
        v = np.append(v,rightmoments)
        leftcentroid = self.getHandPosition(imbgr,imdepth,'left')
        rightcentroid = self.getHandPosition(imbgr,imdepth,'right')
        v = np.append(v,leftcentroid) #14-16 (14,15)
        v = np.append(v,rightcentroid) #17-19 (16,17)
        #leftmoments,_ = self.getCombinedMoments(imbgr,'left') 
        #rightmoments,_ = self.getCombinedMoments(imbgr,'right') 
        #v = np.append(v,leftmoments)
        #v = np.append(v,rightmoments)
        #v = np.append(v,self.getVelocity(leftcentroid,'left')) #20 (18,19)
        #v = np.append(v,self.getVelocity(rightcentroid,'right')) #21 (20,21)
        #v = np.append(v,self.getCentroidDistance(imbgr,'left')) #20 (18,19)
        #v = np.append(v,self.getCentroidDistance(imbgr,'right')) #21 (20,21)
        return v

    #keeping a memory of "smoothing_memory" frames for now
    # may attempt different types of smoothing in the future (eg. Kalman filter)
    def addPoint(self,timestamp,imbgr,imdepth):
        self.timeline = np.append(self.timeline,timestamp)
        v = self.rawFeatureVector(imbgr,imdepth)
        if self.memory.shape != (0,):
            self.memory = np.vstack((self.memory,v))
        else:
            self.memory = v[np.newaxis]
        if self.memory.shape[0] > smoothing_memory:
            self.memory = self.memory[-smoothing_memory:]

        #indexing here? (smooth only some features)
        smoothed = stats.nanmean(self.memory)

        if self.features.shape != (0,):
            self.features = np.vstack((self.features,smoothed))
        else:
            self.features = smoothed[np.newaxis]
        return smoothed

    def normalize(self,indices):
        if self.features.size:
            nanmin = np.nanmin(self.features[:,indices],0)
            nanmax = np.nanmax(self.features[:,indices],0)
            self.features[:,indices] = (self.features[:,indices] - nanmin)/(nanmax-nanmin)

    def getFeatures(self):
        self.normalize([14,15,16,17])
        return self.features
