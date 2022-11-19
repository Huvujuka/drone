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
    print("Camera Width/Height: " + str(W) + "/" + str(H))
    return W, H


def LatToFeet(lat):
    return lat*364000

def FeetToLat(feet):
    return feet/364000

def LongToFeet(long):
    return long*288200

def FeetToLong(feet):
    return feet/288200

def Uturn(deltaAB, X, Lat0Long1):
    if(Lat0Long1):
        if bool(X == [0,0]):
            return False
        else:
            if deltaAB[1] < 0.0:
                return bool(not(deltaAB[1] < X[1] < 0.0))
            else:
                return bool(not(0 < X[1] < deltaAB[1]))
    else:
        if bool(X == [0,0]):
            return False
        else:
            if deltaAB[0] < 0.0:
                return bool(not(deltaAB[0] < X[0] < 0.0))
            else:
                return bool(not(0 < X[0] < deltaAB[0]))

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


def WithinBounds(deltaAB, X, Lat0Long1, dLatLong):
    if deltaAB[Lat0Long1] < 0:
        if deltaAB[Lat0Long1] < X[Lat0Long1] < 0:
            return True
        else:
            if X[0] == X[1] == 0:
                return True
            else: 
                return False
    else:
        if 0 < X[Lat0Long1] < deltaAB[Lat0Long1]:
            return True
        else: 
            return False

def stitchPath(deltaLat, deltaLong, A):
    path= [[],[]]
    for i in range(len(deltaLat)):
        path[0][i] = A[0] + deltaLat[i] 
        path[1][i] = A[1] + deltaLong[i]
        
def createPath(A,B, altitude, overlap):
    rnd = 5
    path = []
    deltaLat = []
    deltaLong = []
    deltaAB = [A[0]-B[0], A[1]-B[1]]

    W, H = find_WH(altitude)
    dLat, dLong = detDeltaLatLong(A, B, W, H, overlap)
    dLatLong = [dLat, dLong]
    print(deltaAB)
    print("[" + str(dLat) + "," + str(dLong) + "]")
    X = [0,0]
    
#######################         A & B are the same ######################################3
    if(A == B):
        print("SAME")
        deltaLat.append(X[0])
        deltaLong.append(X[1])
        #return stitchPath(deltaLat, deltaLong, A)
        return deltaLat, deltaLong #testing return statement
#######################         A & B have a displacement that is less than the width of the camera frame #############################

    elif(bool(abs(deltaAB[0]) < dLat)  or  bool(abs(deltaAB[1]) < dLong)):
        print("ONE DIM SAME")
        if abs(deltaAB[0])>abs(deltaAB[1]):
            X[1] = deltaAB[1]/2
            print(str(X[1]))
            deltaLat.append(X[0])
            deltaLong.append(X[1])
            while(WithinBounds(deltaAB, X, 0, dLatLong)):
                X[0] += dLat
                deltaLat.append(X[0])
                deltaLong.append(X[1])
        else:
            X[0] = deltaAB[0]/2
            deltaLat.append(X[0])
            deltaLong.append(X[1])
            while(WithinBounds(deltaAB, X, 1, dLatLong)):
                X[1] += dLong
                deltaLat.append(X[0])
                deltaLong.append(X[1])

        #return stitchPath(deltaLat, deltaLong, A)
        return deltaLat, deltaLong #testing return statement
##################### Non special case A&B, just any other A&B that this code can handle. 
    else:
        print("ALL DIFF")
        deltaLat.append(X[0])
        deltaLong.append(X[1])
        if(abs(deltaAB[0]) >= abs(deltaAB[1])):
            while bool((((abs(deltaAB[0]) > abs(X[0])) & (abs(X[0]) >= 0.0)) or ((abs(deltaAB[1]) > abs(X[1])) & (abs(X[1]) >= 0.0))) or (X[0] == X[1] == 0)):
                if bool(Uturn(deltaAB, X, 0)):
                    #if (abs(X[1] + dLong/2) > abs(deltaAB[1])):
                    #    break
                    #else:
                        X[1] += dLong
                        deltaLat.append(X[0]) 
                        deltaLong.append(X[1])
                        dLat = -dLat
                        X[0] += dLat
                        deltaLat.append(X[0])
                        deltaLong.append(X[1])
                        
                else: 
                    X[0] += dLat
                    deltaLat.append(X[0])
                    deltaLong.append(X[1])
                #print("X[0] = " + str(X[0]) + "         X[1] = " + str(X[1]))

        else:
            while bool((((abs(deltaAB[0]) > abs(X[0])) & (abs(X[0]) >= 0.0)) or ((abs(deltaAB[1]) > abs(X[1])) & (abs(X[1]) >= 0.0))) or (X[0] == X[1] == 0)):
                if bool(Uturn(deltaAB, X, 1)):
                    #if (abs(X[0] + dLat/2) > abs(deltaAB[0])):
                    #    break
                    #else:
                        
                        X[0] += dLat
                        deltaLat.append(X[0]) 
                        deltaLong.append(X[1])
                        dLong = -dLong
                        X[1] += dLong
                        deltaLat.append(X[0])
                        deltaLong.append(X[1])
                        
                else: 
                    X[1] += dLong
                    deltaLat.append(X[0])
                    deltaLong.append(X[1])
                #print("X[0] = " + str(X[0]) + "         X[1] = " + str(X[1]))





altitude = 40
A = [30.617344, -96.332644]

B = [30.617244, -96.332538]
overlap = .4
c,d= createPath(A, B, altitude, overlap)
print("Path is " + str(len(c)) + " points")

plt.plot(c, d, 'b*')
plt.plot(A[0]-B[0],A[1]-B[1], "r+" )
plt.plot(0,0, "r+")
plt.show()