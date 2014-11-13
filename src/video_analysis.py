import numpy as np
import cv2
import matplotlib.pyplot as plt
from video_tools import *

# Path to video file to analyse 
video = '../test_videos/clip_02A.mp4'

frame_count = get_frame_count(video, util='ffprobe')
frame_rate = get_frame_rate(video, util='ffprobe')
print 'number of frames:', frame_count
print 'frame rate:', frame_rate

# create an cv2 capture object
cap = cv2.VideoCapture(video)

# initialize a figure to do interactive plotting
fig = plt.figure(1)
plt.ion()
plt.show()

# store previous frame
prev_frame = None

while(cap.isOpened()):

    # grab next video frame
    retVal, frame = cap.read()
    # break out of loop when reading is unsuccessful
    if retVal == False:
        break

    #== Do your processing here ==#



    # show frame
    cv2.imshow('Video', frame)


    # break out of loop by pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    prev_frame = frame


# clean up after ourselves
cap.release()
cv2.destroyAllWindows()
