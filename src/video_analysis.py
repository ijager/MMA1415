import numpy as np
import cv2
import matplotlib.pyplot as plt
from video_tools import *
import feature_extraction as ft

# Path to video file to analyse 
video = '../test_videos/clip_09.mp4'

# Retrieve frame count. We need to add one to the frame count because cv2 somehow 
# has one extra frame compared to the number returned by avprobe.
frame_count = get_frame_count(video) + 1
frame_rate = get_frame_rate(video)

# create an cv2 capture object
cap = cv2.VideoCapture(video)

# initialize a figure to do interactive plotting
fig = plt.figure(1)
plt.ion()
plt.show()

# store previous frame
prev_frame = None
x = np.zeros(frame_count)
index = 0
while(cap.isOpened()):

    # grab next video frame
    retVal, frame = cap.read()
    # break out of loop when reading is unsuccessful
    if retVal == False:
        break

    #== Do your processing here ==#
    hist = ft.colorhist(frame)
    plt.cla()
    plt.plot(hist)
    x[index] = index
    index += 1


    # show frame
    cv2.imshow('Video', frame)


    # break out of loop by pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    prev_frame = frame

# clean up after ourselves
cap.release()
cv2.destroyAllWindows()
