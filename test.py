import image_search
import random
import numpy as np
import matplotlib.pyplot as plt
import pickle
import cv2

def compute_ukbench_score(src, imlist):
	""" Returns the average number of correct
	images on the top four results of queries."""
	nbr_images = len(imlist)
	pos = np.zeros((nbr_images, 4))
	# get first four results for each image
	for i in range(nbr_images):
		pos[i] = [w[1]-1 for w in src.query(imlist[i])[:4]]

	# compute score and return average 
	score = array([ (pos[i]//4)==(i//4) for i in range(nbr_images)])*1.0 
	return sum(score) / (nbr_images)

def plot_results(src,res):
	""" Show images in result list 'res'."""
	fig = plt.figure()
	nbr_results = len(res)
	for i in range(nbr_results):
		imname = src.get_filename(res[i]) 
		plt.subplot(1,nbr_results,i+1)
		plt.imshow(cv2.imread(imname))
		plt.axis('off') 
	fig.canvas.set_window_title('Visual BoW results')
	plt.show()

def plot_query(im):
	print 'query image = ', im
	plt.figure()
	plt.imshow(cv2.imread(im))
	plt.title('Query Image')
	plt.axis('off') 

print 'loading vocabulary ...'

# load vocabulary
with open('vocabulary.pkl', 'rb') as f: 
	voc = pickle.load(f)

print 'loading features ...'

# load feature set
with open('sift.pkl', 'rb') as f:
	features = pickle.load(f)

with open('colorhist.pkl', 'rb') as f:
	colorhist_features = pickle.load(f)
	
src = image_search.Searcher('test.db', voc)

key = random.choice(features.keys())
iw = voc.project(features[key])
#print 'ask using a histogram...'
#print src.candidates_from_histogram(iw)[:10]

print 'try a query...'
print src.query(key)[:10]

nbr_results = 6
res = [w[1] for w in src.query(key)[:nbr_results]] 
plot_query(key)

print 'colorhist query ...'
hist = src.get_colorhist(key)
candidates = src.candidates_from_colorhist(hist, colorhist_features)
fig = plt.figure()
i = 0
for candidate in candidates[0:6]:
	im = cv2.imread(candidate)
	plt.subplot(1,6,i+1)
	plt.imshow(im)
	plt.axis('off') 
	i+=1
fig.canvas.set_window_title('Colorhist results')
plot_results(src,res)

