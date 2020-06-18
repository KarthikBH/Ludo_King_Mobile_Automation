import cv2
import sys
import numpy as np

def nothing(x):
    pass

# Load in image
image = cv2.imread('pic.jpg')

# Create a window
cv2.namedWindow('image')
cv2.namedWindow('colors')

# create trackbars for color change
cv2.createTrackbar('HMin','colors',0,179,nothing) # Hue is from 0-179 for Opencv
cv2.createTrackbar('SMin','colors',0,255,nothing)
cv2.createTrackbar('VMin','colors',0,255,nothing)
cv2.createTrackbar('HMax','colors',0,179,nothing)
cv2.createTrackbar('SMax','colors',0,255,nothing)
cv2.createTrackbar('VMax','colors',0,255,nothing)

# Set default value for MAX HSV trackbars.
cv2.setTrackbarPos('HMax', 'colors', 179)
cv2.setTrackbarPos('SMax', 'colors', 255)
cv2.setTrackbarPos('VMax', 'colors', 255)

# Initialize to check if HSV min/max value changes
hMin = sMin = vMin = hMax = sMax = vMax = 0
phMin = psMin = pvMin = phMax = psMax = pvMax = 0

output = image
wait_time = 33

while(1):

    # get current positions of all trackbars
    hMin = cv2.getTrackbarPos('HMin','colors')
    sMin = cv2.getTrackbarPos('SMin','colors')
    vMin = cv2.getTrackbarPos('VMin','colors')

    hMax = cv2.getTrackbarPos('HMax','colors')
    sMax = cv2.getTrackbarPos('SMax','colors')
    vMax = cv2.getTrackbarPos('VMax','colors')

    # Set minimum and max HSV values to display
    lower = np.array([hMin, sMin, vMin])
    upper = np.array([hMax, sMax, vMax])

    # Create HSV Image and threshold into a range.
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    output = cv2.bitwise_and(image,image, mask= mask)

    # Print if there is a change in HSV value
    if( (phMin != hMin) | (psMin != sMin) | (pvMin != vMin) | (phMax != hMax) | (psMax != sMax) | (pvMax != vMax) ):
        print("(hMin = %d , sMin = %d, vMin = %d), (hMax = %d , sMax = %d, vMax = %d)" % (hMin , sMin , vMin, hMax, sMax , vMax))
        phMin = hMin
        psMin = sMin
        pvMin = vMin
        phMax = hMax
        psMax = sMax
        pvMax = vMax

    # Display output image
    cv2.imshow('image',output)

    # Wait longer to prevent freeze for videos.
    if cv2.waitKey(wait_time) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()