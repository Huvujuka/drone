import platform
import cv2
import numpy as np
import os
import time
import multiprocessing

def takeBurst(Burst_Num):
    startTime = time.time()
    Img_Array = []
    currImg = cv2.VideoCapture(0)                                         #Initialize camera

    if not currImg.isOpened():                                          #Check if camera is open
        print("Cannot open camera. Exiting...")                         #Close if not
        exit()
        
    for img_count in range(Burst_Num):
        check, Img = currImg.read()                                     #Check allows a buffer for checking images load in properly
                                                                        #Img is the image trying to be saved

        if not check:                                                      #Check image loaded properly
            print("No frames recieved. Exiting...")
            exit()

        Img_Array.append(Img)

    for i in range(len(Img_Array)):
        cv2.imwrite("/home/odroid/Desktop/Demo/CompletedImages/Burst/Img" + str(i) + ".jpg", Img_Array[i])
    runTime = time.time() - startTime
    print("Took " + str(runTime))


num_Imgs = int(input("Number of pictures to take: "))
takeBurst(num_Imgs)

