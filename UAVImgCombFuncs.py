#Item calls
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def img_list(file_path):
    origDir = os.getcwd()
    os.chdir(file_path)
    imgList=[]
    fileOrder = []
    file_list = os.listdir()
    for files in file_list:
        #print("taking in: " + str(files))
        if files.endswith(".jpg") or files.endswith(".jpeg"):
            n = cv2.imread(files)
            #print(files[:-4])
            fileOrder.append(int(files[:-4]))
            imgList.append(n)

    
    for i in range(len(fileOrder)):
        sorted = True
        for j in range(len(fileOrder) - i - 1):
            if fileOrder[j] > fileOrder[j+1]:
                fileOrder[j], fileOrder[j+1] = fileOrder[j+1], fileOrder[j]
                imgList[j], imgList[j+1] = imgList[j+1], imgList[j]
                sorted = False

        if sorted:
            break

    #print(fileOrder)

    return imgList

def keyPoints(Img, MAX_NUM_FEATURES):

    #Greatly changes compute time:It is number of keypoints to find

    Img_grey = cv2.cvtColor(Img, cv2.COLOR_BGR2GRAY)    #orb needs greyscale image

    orb = cv2.ORB_create(MAX_NUM_FEATURES)              #Create orb keypoints and descriptors storage structure
    #keypoints, descriptors = orb.detectAndCompute(Img_grey, None) #Store keypoints and descriptors separatley
    #returns key points and descriptors
    return orb.detectAndCompute(Img_grey, None)


def matchPoints(descriptors1, descriptors2, PERCENT_GOOD_MATCHES):
    #matcher is base class for holding matching descriptors. orb stores in binary strings, hamming alg necessary. Bruteforce needed for homography
    matcher = cv2.BFMatcher_create(cv2.NORM_HAMMING)

    #matches stores matched data values
    matches = matcher.knnMatch(descriptors1, descriptors2, k=2)
    #Sort matches by match quality
    good = []
    for m, n in matches:
        if m.distance < 0.6 * n.distance:
            good.append(m)

    return good

def warpImages(Img1, Img2, H):
    #gather image shape
    rows1, cols1 = Img1.shape[:2]
    rows2, cols2 = Img2.shape[:2]

    listPoints1 = np.float32([[0,0], [0, rows1],[cols1,rows1],[cols1,0]]).reshape(-1,1,2)
    tempPoints = np.float32([[0,0], [0, rows2],[cols2,rows2],[cols2,0]]).reshape(-1,1,2)

    listPoints2 = cv2.perspectiveTransform(tempPoints, H)

    listPoints = np.concatenate((listPoints1, listPoints2), axis = 0)

    [x_min, y_min] = np.int32(listPoints.min(axis = 0).ravel() - 0.5)
    [x_max, y_max] = np.int32(listPoints.max(axis = 0).ravel() + 0.5)

    translationDist = [-x_min, -y_min]
    H_translation = np.array([[1, 0, translationDist[0]], [0, 1, translationDist[1]], [0,0,1]])
    imgOut =cv2.warpPerspective(Img2, H_translation.dot(H), (x_max-x_min, y_max-y_min))
    imgOut[translationDist[1]: rows1+translationDist[1], translationDist[0]:cols1+translationDist[0]] = Img1
    return imgOut


def homography(Img1, Img2, keypoints1, keypoints2, matches):
    #src_pts = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
    #dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1,1,2)
    #M, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    #resultImg = warpImages(Img1, Img2, M)
    #return resultImg


    points1 = np.zeros((len(matches), 2), dtype = np.float32)
    points2 = np.zeros((len(matches), 2), dtype = np.float32)
    #Loops through points
    for i, match in enumerate(matches):
        points1[i, : ] = keypoints1[match.queryIdx].pt
        points2[i, : ] = keypoints2[match.trainIdx].pt

    #h is homography, it is the placeholder for the image
    h, mask = cv2.findHomography(points2, points1, cv2.RANSAC)
    return warpImages(Img1, Img2, h)
    #warp image
    #height, width, channels = Img1.shape
    #return cv2.warpPerspective(Img2, h, (width, height))"""
