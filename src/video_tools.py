import subprocess
import re
from fractions import Fraction


def get_frame_rate(video, util='avprobe'):
    cmd = util + ' -show_streams ' + video
    process = subprocess.Popen(cmd.split(), stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    out, err = process.communicate()
    pattern = 'codec_type\=video.*?avg_frame_rate\=(\d+[\/\d.]*|\d)'
    result = re.search(pattern, out, re.DOTALL).group(1)
    return float(Fraction(result))

def get_frame_count(video, util='avprobe'):
    cmd = util + ' -show_streams ' + video
    process = subprocess.Popen(cmd.split(), stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    out, err = process.communicate()
    pattern = 'codec_type\=video.*?nb_frames\=([0-9]+)'
    result = re.search(pattern, out, re.DOTALL)
    return int(result.group(1))


