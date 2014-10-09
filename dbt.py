#!/usr/bin/env python

import argparse
import feature_extraction as ft
import glob
import Vocabulary
import image_search
import pickle
import os.path

def compute_features(image_list, output, feature_function):
    fname = output + '.pkl'
    if os.path.isfile(fname):
        compute = raw_input("Found existing features: " + fname + " Do you want to recompute them? ([Y]/N): ")
    else:
        compute = 'Y'
    if compute == 'Y' or compute == '':
        features = feature_function(image_list)
        with open(fname, 'wb') as f:
            print 'saving features to', fname , '...'
            pickle.dump(features, f)
    return features


features = ['sift', 'colorhist', 'harris', 'meta', 'all']
types = ('*.jpg', '*.JPG', '*.png')

parser = argparse.ArgumentParser(description="Database tool creates features and Visual Bag of Words database for a specified training set of images.")
parser.add_argument("feature", help="The type of features you want to generate. Chose from " + str(features))
parser.add_argument("training_set", help="Path to training images.")
parser.add_argument("--database", "-d", help="Optional output name for the database", default="MMA.db")
parser.add_argument("--prefix","-p",  help="prefix path to database directory, default = 'db/'", default="db/")
parser.add_argument("--clusters", "-c", help="Number of clusters for K-Means clustering algorithm'", default=100)

args = parser.parse_args()


print '\nMulti Media Analysis Database tool'
print '==================================\n'
print 'Creating', args.feature, 'features for', args.training_set ,'\n'


# retrieve image list

image_list = []
for type_ in types:
    files = args.training_set + type_
    image_list.extend(glob.glob(files))	

# Get file name without extension and prefix
base=os.path.basename(args.database).split('.')[0]

# sift features

sift_features = None
if args.feature == 'sift' or args.feature == 'all':
    compute_features(image_list, args.prefix + base + '_sift', ft.get_sift_features)

    # visual vocabulary
    
    fname = args.prefix + base + '_vocabulary.pkl'
    if os.path.isfile(fname):
        compute = raw_input("Found existing vocabulary: " + fname + " Do you want to recompute it? ([Y]/N): ")
    else:
        compute = 'Y'
    if compute == 'Y' or compute == '':
        if sift_features == None:
            fname = args.prefix + base +  '_sift.pkl'
            if os.path.isfile(fname):
                print 'loading sift features'
                with open(fname, 'rb') as f:
                    sift_features = pickle.load(f)
            else:
                print 'Error, please generate sift features first.'
	print 'Creating vocabulary ... \n'
        voc = Vocabulary.Vocabulary(base)
        voc.train(sift_features, args.clusters)
        fname = args.prefix + base + '_vocabulary.pkl'
	with open(fname, 'wb') as f: 
            pickle.dump(voc,f)


if args.feature == 'colorhist' or args.feature == 'all':
    compute_features(image_list, args.prefix + base + '_colorhist', ft.get_colorhist)

if args.feature == 'harris' or args.feature == 'all':
    compute_features(image_list, args.prefix + base + '_harris', ft.get_harris_features)

if args.feature == 'meta' or args.feature == 'all':
    compute_features(image_list, args.prefix + base + '_meta', ft.get_meta_data)
