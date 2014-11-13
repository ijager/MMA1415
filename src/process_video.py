#!/usr/bin/env python

import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
import argparse
import pickle
import glob
import feature_extraction as ft    
from scipy.io.wavfile import read
from video_tools import *


parser = argparse.ArgumentParser(description="Video Processing tool extracts features for each frame of video and for its corresponding audio track")
parser.add_argument("training_set", help="Path to training videos and wav files")

args = parser.parse_args()


video_types = ('*.mp4', '*.MP4')
audio_types = ('*.wav', '*.WAV')


# grab all video file names
video_list = []
for type_ in video_types:
    files = args.training_set + '/' +  type_
    video_list.extend(glob.glob(files))	

def frame_to_audio(frame_nbr, frame_rate, fs, audio):
    start_index = frame_nbr / frame_rate * fs
    end_index = (frame_nbr+1) / frame_rate * fs
    return audio[start_index:end_index]



# Processing of videos


colorhist_features = {}
sum_of_diff_features = {}
for video in video_list:

    print 'processing:', video
    cap = cv2.VideoCapture(video)
    frame_rate = get_frame_rate(video) 

    # get corresponding audio file
    filename, fileExtension = os.path.splitext(video)
    audio = filename + '.wav'
    fs, wav_data = read(audio)

    colorhists = []
    sum_of_differences = []

    prev_frame = None
    frame_nbr = 0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if frame == None:
            break
        audio_frame = frame_to_audio(frame_nbr, frame_rate, fs, wav_data)
        power = np.sum(audio_frame**2)
       
        # calculate sum of differences
        if not prev_frame == None:
            diff = np.absolute(prev_frame - frame)
            sum = np.sum(diff.flatten()) / (diff.shape[0]*diff.shape[1]*diff.shape[2])
            sum_of_differences.append(sum)

        colorhists.append(ft.colorhist(frame))
        prev_frame = frame
        frame_nbr += 1

    colorhist_features[video] = colorhists
    sum_of_diff_features[video] = sum_of_differences


fname = 'video_colorhists.pkl'
with open(fname, 'wb') as f:
    pickle.dump(colorhist_features, f)

fname = 'video_sumofdiff.pkl'
with open(fname, 'wb') as f:
    pickle.dump(np.array(sum_of_diff_features), f)

