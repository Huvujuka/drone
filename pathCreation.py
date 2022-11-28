import math
import matplotlib.pyplot as plt
#A & B are the coordinates passed in from the user
#W & H are the width and height of the camera frame
#Over lap is the percent that the edges of each images overlap 
        #larger makes image stitching easier, however it takes the drone much much longer to fly
        #Value must range between .2 - .8


#Given the altitude, determine the width and height of the camera frame
def find_WH(altitude):
    #Pix width of camera
    pix_w = 2592
    #Pix height of camera
    pix_h = 1944
    theta = 75.7 * math.pi/180
    theta_base = math.atan(pix_h/pix_w)

    d=2*altitude*math.tan(theta/2)

    W = d * math.cos(theta_base)
    H = d * math.sin(theta_base)
    #print("Camera Width/Height: " + str(W) + "/" + str(H))
    return W, H


def LatToFeet(lat):
    return lat*364000

def FeetToLat(feet):
    return feet/364000

def LongToFeet(long):
    return long*288200

def FeetToLong(feet):
    return feet/288200

#Determine what delta Latitude or Longitude is in degrees
def detDeltaLatLong(A, B, W, H, overlap):
    if abs(A[0]-B[0]) >= abs(A[1]-B[1]):
        dLat = FeetToLat(H - (H * overlap))
        dLong = FeetToLong(W - (W * overlap))
    else:
        dLat = FeetToLat(W - (W * overlap))
        dLong = FeetToLong(H - (H * overlap))
    if(A[0] - B[0] < 0):
        dLat = - dLat
    if(A[1] - B[1] < 0):
        dLong = -dLong
    return dLat, dLong

##Create a single dimension check for if the point is within the space provided
def WithinBounds(dAB, X, dLatLong, LatLong):
    Lat = 0
    Long = 1
    retVal = False
    LatLong_ = 0
    if LatLong == Lat:
        LatLong_ = Long
    else:
        LatLong_ == Lat

    #Determining initial return value
    ##If the delta is zero and the X is also zero, it is on the line provided
    if dAB[LatLong] == 0:
        if X[LatLong] == 0:
            retVal = True
        else: retVal = False
    ##If the delta is negative
    elif dAB[LatLong] < 0:
        if dAB[LatLong] < X[LatLong] < 0:
            retVal = True
        
        elif X[0] == X[1] == 0: retVal = True

        else: 
            if (X[LatLong] == 0 & abs(dLatLong[LatLong_] <= abs(dLatLong[LatLong]))):
                retVal = True
            else:    
                retVal = False
    
    #If the coordinate deltas are positive
    else:
        if 0 < X[LatLong] < dAB[LatLong]:
            retVal = True
        
        elif X[0] == X[1] == 0: retVal = True

        else: 
            if (X[LatLong] == 0 & abs(dLatLong[LatLong_] <= abs(dLatLong[LatLong]))):
                retVal = True
            else:    
                retVal = False


    return retVal

def stitch(A, delta):
    path = [[],[]]
    for i in range(len(delta[0])):
        
        X = A[0] - delta[0][i]
        Y = A[1] - delta[1][i]
        path[0].append(X)
        path[1].append(Y)

    return path

def createPath(A, B, altitude, overlap):
    WH = find_WH(altitude)
    dLatLong = detDeltaLatLong(A, B, WH[0], WH[1], overlap)
    dAB = [A[0] - B[0], A[1] - B[1]]
    
    delta = [[], []]
    X = [0,0]
    Lat = 0
    Long = 1
    #If A & B are the same
    if dAB[Lat] == dAB[Long] == 0:
        delta[Lat].append(X[Lat])
        delta[Long].append(X[Long])
    #If a dimension is smaller than a camera spacing
    elif ((abs(dAB[Lat])< abs(dLatLong[Lat])) or (abs(dAB[Long]) < abs(dLatLong[Long]))):
        #determines Lat or Long to loop over
        check = 2
        #Both dimensions smaller than camera spacings
        if ((abs(dAB[Lat])< abs(dLatLong[Lat])) and (abs(dAB[Long]) < abs(dLatLong[Long]))):
            delta[0][0] = (1/2) * dAB[Lat] 
            delta[1][0] = (1/2) * dAB[Long]
        #One dimension smaller than camera spacing
        elif abs(dAB[Lat]) < abs(dLatLong[Lat]):
            X[Lat] = dAB[Lat] / 2
            delta[Lat].append(X[Lat])
            delta[Long].append(X[Long])
            check = 1
        else:
            #print("Longitudes for A & B are close")
            X[Long] = dAB[Long] / 2
            delta[Lat].append(X[Lat])
            delta[Long].append(X[Long])
            check = 0
        #Goes into loop if one delta is smaller than the size of the camera area
        if not(check == 2):
            while (WithinBounds(dAB, X, dLatLong, check)):
                tempX = X[:]
                tempX[check] = tempX[check] + 1/2 * dLatLong[check]
                X[check] += dLatLong[check]
                if not(WithinBounds(dAB, tempX, dLatLong, check)):
                    break
                delta[Lat].append(X[Lat])
                delta[Long].append(X[Long])
    #Points are far apart
    else:
        delta[Lat].append(X[Lat])
        delta[Long].append(X[Long])
        #Sees if lat or long is larger to decide which to loop over
        check = 0
        if abs(dLatLong[Lat]) < abs(dLatLong[Long]):
            check = 1
        while WithinBounds(dAB, X, dLatLong, 0) or WithinBounds(dAB, X, dLatLong, 1):
            #Checks half step up to see if U-turn needed
            tempX = X[:]
            tempX[check] = tempX[check] + 1/2 * dLatLong[check]
                
            if WithinBounds(dAB, tempX, dLatLong, check):
    
                X[check] += dLatLong[check]
                
            
                delta[Lat].append(X[Lat])
                delta[Long].append(X[Long])
            
            else:
                if check == 0:
                    
                    X[Long] += dLatLong[Long]
                    tempX = list(X)
                    not_Check = int(bool(not(bool(check))))
                    tempX[not_Check] = tempX[not_Check] + 1/2 * dLatLong[not_Check]
                    if not(WithinBounds(dAB, tempX, dLatLong, Long)):
                        #print("breaks loop")
                        break
                    delta[Lat].append(X[Lat])
                    delta[Long].append(X[Long])
                    dLatLong_ = list(dLatLong)
                    dLatLong_[check] = dLatLong_[check] * -1
                    dLatLong = tuple(dLatLong_)
                    X[check] += dLatLong[check]
                    delta[Lat].append(X[Lat])
                    delta[Long].append(X[Long])
                
                else:
                    tempX = list(X)
                    not_Check = int(bool(not(bool(check))))
                    tempX[not_Check] = tempX[not_Check] + 1/2 * dLatLong[not_Check]
                    X[Lat] += dLatLong[Lat]
                    if not(WithinBounds(dAB, tempX, dLatLong, Lat)):
                        break
                    delta[Lat].append(X[Lat])
                    delta[Long].append(X[Long])
                    dLatLong_ = list(dLatLong)
                    dLatLong_[check] = dLatLong_[check] * -1
                    dLatLong = tuple(dLatLong_)
                    X[check] += dLatLong[check]
                    delta[Lat].append(X[Lat])
                    delta[Long].append(X[Long])
    path = stitch(A, delta)
    return path




    
