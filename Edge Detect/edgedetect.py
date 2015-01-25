import cv2
import numpy as np
from matplotlib import pyplot as plt

img = cv2.imread('lena512.bmp',0)

img_smoothed = cv2.GaussianBlur(img, (5,5), 0)
#img_sobel = cv2.Sobel(img_smoothed, -1, 1, 1)
#sobelx = cv2.Sobel(img_smoothed,-1,1,0,ksize=3)
#sobely = cv2.Sobel(img_smoothed,-1,0,1,ksize=3)
#cv2.imshow('test', sobelx)
#cv2.waitKey()
edges = cv2.Canny(img,100,200)

plt.subplot(121),plt.imshow(img,cmap = 'gray')
plt.title('Original Image'), plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(edges,cmap = 'gray')
plt.title('Edge Image'), plt.xticks([]), plt.yticks([])

plt.show()
