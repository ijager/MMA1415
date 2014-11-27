import subprocess
import re
from fractions import Fraction

def video_info(video, util):
    cmd = util + ' -show_streams ' + video
    process = subprocess.Popen(cmd.split(), stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    out, err = process.communicate()
    return out

def get_duration(video, util='avprobe'):
    info = video_info(video, util)
    pattern = 'codec_type\=video.*?duration\=(\d+[\/\d.]*|\d)'
    result = re.search(pattern, info, re.DOTALL).group(1)
    return float(result)

def get_frame_rate(video, util='avprobe'):
    info = video_info(video, util)
    pattern = 'codec_type\=video.*?avg_frame_rate\=(\d+[\/\d.]*|\d)'
    result = re.search(pattern, info, re.DOTALL).group(1)
    return float(Fraction(result))

def get_frame_count(video, util='avprobe'):
    info = video_info(video, util)
    pattern = 'codec_type\=video.*?nb_frames\=([0-9]+)'
    result = re.search(pattern, info, re.DOTALL)
    return int(result.group(1))


