import cv2
import progressbar

def get_sift_features(im_list):
	"""get_sift_features accepts a list of image names and computes the sift descriptos for each image. It returns a dictionary with descriptor as value and image name as key """
	sift = cv2.SIFT()
	features = {}
	total = len(im_list)
	bar = progressbar.ProgressBar(maxval=total, \
		widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
	count = 0
	print 'Generating SIFT features for [', total, '] images...'
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
