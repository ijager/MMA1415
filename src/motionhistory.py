import numpy as np
import cv2
import matplotlib.pyplot as plt
from video_tools import *
import feature_extraction as ft
from scikits.talkbox.features import mfcc

# Path to video file to analyse 
video = '../Educational_Videos/jeugdjournaal2014-12-01.mp4'
video = '../Educational_Videos/jeugdjournaal2014-12-11.mp4'
#video = '../Educational_Videos/BlackKnight.avi'
#video = '../test_videos/video_09.mp4'
#video = '../Educational_Videos/Launch1.mp4'

# Retrieve frame count. We need to add one to the frame count because cv2 somehow 
# has one extra frame compared to the number returned by avprobe.
frame_count = get_frame_count(video) + 1
frame_rate = get_frame_rate(video)

# create an cv2 capture object
cap = cv2.VideoCapture(video)

# initialize a figure to do interactive plotting
plt.figure()
plt.ion()
plt.show()
# store previous frame
prev_frame = None
alpha = 0.8
beta = 34
np.set_printoptions(threshold=np.nan)
s = np.zeros(frame_count)
i = 0
while(cap.isOpened()):

    # 
    retVal, frame = cap.read()
    # 
    if retVal == False:
        break

    #== Do your processing here ==#
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if prev_frame == None:
        prev_frame = np.zeros(gray.shape)
        prev_MHI = np.zeros(gray.shape)
    diff = np.abs(prev_frame.astype('int8') - gray.astype('int8'))
    I = (diff) > beta
    MHI = I + alpha*prev_MHI
    s[i] = np.sum(diff[:])
    i += 1
    #
    res = frame.copy()
    for i in range(3): 
        res[:,:,i] = frame[:,:,i]*MHI
    g = (MHI < 3)[0] * gray
    color_gray = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
    cv2.imshow('Video', res+color_gray/4)

    # 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    prev_MHI = MHI 
    prev_frame = gray
# clean up after ourselves
cap.release()
cv2.destroyAllWindows()
