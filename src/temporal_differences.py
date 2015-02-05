import numpy as np
import cv2
import matplotlib.pyplot as plt
from video_tools import *
import feature_extraction as ft
from scikits.talkbox.features import mfcc

# Path to video file to analyse 
video = '../test_videos/clip_09.mp4'

# Retrieve frame count. We need to add one to the frame count because cv2 somehow 
# has one extra frame compared to the number returned by avprobe.
frame_count = get_frame_count(video) + 1
frame_rate = get_frame_rate(video)

# create an cv2 capture object
cap = cv2.VideoCapture(video)

# initialize a figure to do interactive plotting
fig1 = plt.figure()
ax1 = plt.gca()
fig2 = plt.figure()
ax2 = plt.gca()
plt.ion()
plt.show()
# store previous frame
prev_frame = None
sod = []
sod2 = []
cd = []
while(cap.isOpened()):

    # 
    retVal, frame = cap.read()
    # 
    if retVal == False:
        break

    #== Do your processing here ==#
    # You might want to write separate functions and call those here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.blur(frame, (11,11))
    if prev_frame is not None: 
        prev_hist = ft.colorhist(prev_frame)
        hist = ft.colorhist(frame)
        cd.append((np.abs(prev_hist - hist)))

        diff = np.abs(prev_frame.astype('int8') - frame.astype('int8'))
        normalized_diff = diff/(255.0)
        t = 0.2
        thresholded_diff = (normalized_diff > t) * normalized_diff
        sod2.append(np.sum(normalized_diff/np.prod(diff.shape)))
        sod.append(np.sum(thresholded_diff)/np.prod(diff.shape)) 
        ax1.cla()
        ax2.cla()
        ax1.plot(sod)
        ax1.plot(sod2)
        ax2.plot(cd[-1])
        fig1.canvas.draw()
        fig2.canvas.draw()
    
    #
    cv2.imshow('Video', gray)

    # 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    prev_frame = frame

# clean up after ourselves
cap.release()
cv2.destroyAllWindows()
