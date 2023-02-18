import platform
import cv2
import numpy as np
import os
import time
import multiprocessing

TimeToRecord = 10
def rescale_frame(frame_in, percent):
	width = int(frame_in.shape[1]* percent)
	height = int(frame_in.shape[0]* percent)
	dim = (width, height)
	return cv2.resize(frame_in, dim, interpolation = cv2.INTER_AREA)

video = cv2.VideoCapture(0)
if(video.isOpened() == False):
	print("Error reading camera")
	exit()


#Percent of original video size
percent = 0.25
#temp image holder for video
container = []
#records how long recording images for
runTime = 0
startTime = time.time()
###gather all images to make video
while (True):
	runTime = time.time() - startTime	
	ret, frame = video.read()
	
	if ret == True:
		rescaled_frame = rescale_frame(frame,percent)
		container.append(rescaled_frame)
		
		if (runTime >= TimeToRecord):
			break
	else:
		break
#calculate FPS
FPS = int((len(container)/runTime))
height = int(video.get(4) * percent)
width = int(video.get(3) * percent)
#create video container
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
finVid = cv2.VideoWriter('TestVid.mp4', fourcc, FPS, (width, height))
print("recorded at: " + str(FPS) + " FPS")
#create video
for i in container:
	finVid.write(i)


finVid.release()
video.release()
cv2.destroyAllWindows()
