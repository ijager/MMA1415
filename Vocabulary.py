from scipy.cluster.vq import *
import numpy as np


class Vocabulary(object):

	def __init__(self, name):
		self.name = name
		self.voc = []
		self.idf = []
		self.trainingdata = []
		self.nbr_words = 0

	def train(self, features, k=100, subsampling=10):
		""" Train a vocabulary from a dictionary of features 
			using k-means with k number of words. Subsampling 
			of training data can be used for speedup. """
			
		nbr_desc = len(features)
		#stack all features for k-means
		descriptors = np.array([], dtype=np.float32).reshape(0,128)
		for feat in features.values():
			descriptors = np.vstack((descriptors, feat))

		#k-means
		self.voc, distortion = kmeans(descriptors[::subsampling,:],k,1)
		self.nbr_words = self.voc.shape[0]
		print 'voc:', self.voc
		print 'voc:', self.nbr_words
		# go through all training images and project on vocabulary
		imwords = np.zeros((nbr_desc, self.nbr_words))
		for desc in features.values():
			imwords = self.project(desc)
		print 'imwords[0]:',imwords[0]
		print 'imwords[1]:',imwords[1]

		nbr_occurences = np.sum( (imwords > 0) * 1, axis=0)
		self.idf = np.log( (1.0*nbr_desc) / (1.0* nbr_occurences+1) )
		self.trainingdata = features



	def project(self, descriptors):
		""" project descriptors on the vocabulary
			to create a histogram of words"""
		imhist = np.zeros((self.nbr_words))
		words, distance = vq(descriptors, self.voc)
		for w in words:
			imhist[w] += 1
		return imhist
