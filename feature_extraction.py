import cv2
import numpy as np
import progressbar

def get_harris_features(im_list):
	total = len(im_list)
	bar = progressbar.ProgressBar(maxval=total, \
		widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
	print 'Generating Harris features for [', total, '] images ...'
	bar.start()
	features = {}
	count = 0
	for im_name in im_list:
		im = cv2.imread(im_name)
		dst = cv2.cornerHarris(im, 2, 3, 0.04)


def get_colorhist(im_list):
	total = len(im_list)
	bar = progressbar.ProgressBar(maxval=total, \
		widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
	print 'Generating ColorHist features for [', total, '] images ...'
	bar.start()
	features = {}
	count = 0
	for im_name in im_list:
		im = cv2.imread(im_name)
		chans = cv2.split(im)
		color_hist = np.zeros((256,3))
		chan_nbr = 0
		for chan in chans:
			color_hist[:,chan_nbr] = cv2.calcHist([chan], [0], None, [256], [0, 256])[0] / (chan.shape[0] * chan.shape[1]);
			chan_nbr += 1
		features[im_name] = color_hist
		bar.update(count)
		count += 1
	print 'Finished\n'
	return features

def get_sift_features(im_list):
	"""get_sift_features accepts a list of image names and computes the sift descriptos for each image. It returns a dictionary with descriptor as value and image name as key """
	sift = cv2.SIFT()
	features = {}
	total = len(im_list)
	bar = progressbar.ProgressBar(maxval=total, \
		widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
	count = 0
	print 'Generating SIFT features for [', total, '] images ...'
	bar.start()
	for im_name in im_list:
		bar.update(count)
		im = cv2.imread(im_name, 0)
		kp, desc = sift.detectAndCompute(im, None)
		features[im_name] = desc
		count += 1
	bar.update(count)
	print 'Finished\n'
	
	return features
