# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np # linear algebr a
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/Users/arvin/Desktop/Drone Image Processing/New_folder'):
    for filename in filenames:
        print(os.path.join(dirname, filename))
# You can write up to 20GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All" 
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import psutil
def warpImages(img1, img2, H):
    rows1, cols1 = img1.shape[:2]
    rows2, cols2 = img2.shape[:2]
    
    list_of_points_1 = np.float32([
        [0,0], 
        [0,rows1],
        [cols1,rows1], 
        [cols1,0]
    ])
    list_of_points_1 = list_of_points_1.reshape(-1,1,2)

    temp_points = np.float32([
        [0,0], 
        [0,rows2], 
        [cols2,rows2],
        [cols2,0]
    ])
    temp_points = temp_points.reshape(-1,1,2)
   
    list_of_points_2 = cv2.perspectiveTransform(temp_points, H)
    
    list_of_points = np.concatenate((list_of_points_1, list_of_points_2), axis=0)
    
    ##Define boundaries:
    [x_min, y_min] = np.int32(list_of_points.min(axis=0).ravel() - 0.5)
    [x_max, y_max] = np.int32(list_of_points.max(axis=0).ravel() + 0.5)
    
    translation_dist = [-x_min,-y_min]
    
    H_translation = np.array([[1, 0, translation_dist[0]], [0, 1, translation_dist[1]], [0,0,1]])

    output_img = cv2.warpPerspective(img2, 
                                     H_translation.dot(H), 
                                     (x_max - x_min, y_max - y_min))
    ## Paste the image:
    output_img[translation_dist[1]:rows1+translation_dist[1], 
               translation_dist[0]:cols1+translation_dist[0]] = img1
    
    return output_img
def warp(img1, img2, min_match_count = 10):
    sift = cv2.SIFT_create()
 
    # Extract the keypoints and descriptors
    keypoints1, descriptors1 = sift.detectAndCompute(img1, None)
    keypoints2, descriptors2 = sift.detectAndCompute(img2, None)
    
    # Initialize parameters for Flann based matcher
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
   
    # Initialize the Flann based matcher object
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    
    # Compute the matches
    matches = flann.knnMatch(descriptors1, descriptors2, k=2)
    
    # Store all the good matches as per Lowe's ratio test
    good_matches = []
    for m1,m2 in matches:
        if m1.distance < 0.9*m2.distance:
            good_matches.append(m1)
            
    if len(good_matches) > min_match_count:
        src_pts = np.float32([ keypoints1[good_match.queryIdx].pt
                              for good_match in good_matches ]).reshape(-1,1,2)
        
        dst_pts = np.float32([ keypoints2[good_match.trainIdx].pt 
                              for good_match in good_matches ]).reshape(-1,1,2)
        
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        result = warpImages(img2, img1, M)
        return result
    else:
        print ("We don't have enough number of matches between the two images.")
        print ("Found only " + str(len(good_matches)) + " matches.")
        print ("We need at least " + str(min_match_count) + " matches.")
def save_image(directory, file_name, image):
#     check directory is exist and create if not exit
    if not os.path.exists(directory):
            os.makedirs(directory)
    cv2.imwrite(directory+'\\'+file_name, image)
def printMemoryInfo():
    print("Memory available is {:,.2f}GB({:,.2f}%)".format(getMemory(), getMemoryPercentage()))
    
def getMemory():
    return  psutil.virtual_memory().available/(1024.0 ** 3)

def getMemoryPercentage():
    return  psutil.virtual_memory().available * 100 / psutil.virtual_memory().total

def img_list(file_path, filenames):
    origDir = os.getcwd()
    os.chdir(file_path)
    imgList=[]
    fileOrder = []
    file_list = os.listdir()
    for files in file_list:
        #print("taking in: " + str(files))
        if files.endswith(".jpg") or files.endswith(".jpeg") or files.endswith(".JPG"):
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
                filenames[j],filenames[j+1] = filenames[j + 1], filenames[j]
                sorted = False

        if sorted:
            break

    print(fileOrder)

    return filenames

def stitch_image_in_sub_directory(input_directory, output_directory):
    image_collage = {}
    file_name = 'final_image_stitched.jpg'
    print("Reaches")
    try:
        if (os.path.isdir(input_directory)== True):
            print("Reaches 2")
            for dirname, _, filenames in os.walk(input_directory):
                # sort file name in a directory
                filenames = img_list(input_directory, filenames)
                print(filenames)
                print('Stitching is start...')
                print('---------------------------------')
                image_collage = cv2.imread(os.path.join(dirname, filenames[0]))
                previous_image = filenames[0]
                temp_num = 1
                
                for index, item in enumerate(filenames):
                    if index == 0: 
                        continue

                    printMemoryInfo()
                    main_image  = cv2.imread(os.path.join(dirname, filenames[index]))

                    # check memory available for next stitching or not
                    if getMemoryPercentage() < 40:
                        print('Reaching limit')
                        file_name = 'temp_image_stitched_'+str(temp_num).zfill(4)+".jpg"
#                         save_image(output_directory, file_name, image_collage)
                        showplt(image_collage)
                        print(os.path.join(output_directory, file_name))
                        image_collage = main_image

                        temp_num += 1
                        print('---------------------------------')
                        continue

                    print('{}. Stitching {} AND {} in process'.format(index, previous_image, filenames[index]))
                    print('---------------------------------')
                    image_collage = warp(image_collage, main_image)  
                    previous_image = filenames[index]
            # Save final Image
            showplt(image_collage)
#             save_image(output_directory, file_name, image_collage)  
    except:
      save_image(output_directory, file_name, image_collage)
#####

   
input_directory = "/Users/arvin/Desktop/Drone Image Processing/New_folder/"
output_directory = "/Users/arvin/Desktop/Drone Image Processing/New_folder1/"
stitch_image_in_sub_directory(input_directory, output_directory)