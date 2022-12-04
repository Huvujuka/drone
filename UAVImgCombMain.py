#Item calls
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from UAVImgCombFuncs import *


def alignImgEdges(Img1, Img2):
#Adjustable Variables
    MAX_NUM_FEATURES = 2000
    PERCENT_GOOD_MATCHES = 0.3
    MIN_MATCH_COUNT = 5


    #gather points that describe items in picture
    keypoints1, descriptors1 = keyPoints(Img1, MAX_NUM_FEATURES)
    keypoints2, descriptors2 = keyPoints(Img2, MAX_NUM_FEATURES)
    #get keypoint matches
    matches = matchPoints(descriptors1, descriptors2, PERCENT_GOOD_MATCHES)
#If there arent enough matches, abort the operation
    if len(matches) > MIN_MATCH_COUNT:
        FinImg = homography(Img1, Img2, keypoints1, keypoints2, matches)

    return FinImg

def loopImgs():
    file_path = "/home/odroid/Desktop/Demo/TestImages/Generic/"
    Images = img_list(file_path)
    track = 1
    while True:
        print("pops images")
        Img1 = Images.pop(0)
        cv2.imwrite("/home/odroid/Desktop/Demo/CompletedImages/IntermediateComb/" + str(track) + ".jpg", Img1)
        Img2 = Images.pop(0)
        Img3 = alignImgEdges(Img1,Img2)
        #cv2.imshow("Current Img3", Img3)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows
        
        Images.insert(0, Img3)
        if len(Images) == 1:
            break
        track += 1

    cv2.imwrite("/home/odroid/Desktop/Demo/CompletedImages/" + "Combination.jpg", Img3)


loopImgs()