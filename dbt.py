#!/usr/bin/env python

import sys
import argparse
import feature_extraction as ft
import glob
import Vocabulary
import image_search
import pickle
import os.path

def feature_active(name):
    return (args.feature == name or args.feature == 'all')


def load_features(name):
    fname = args.prefix + base + '_' + name + '.pkl'
    feat = None
    with open(fname, 'rb') as f:
        print 'Loading', fname
        feat = pickle.load(f)
    return feat 

def compute_features(image_list, name, feature_function):
    fname = args.prefix + base + '_' + name + '.pkl'
    if os.path.isfile(fname):
        compute = raw_input("Found existing features: " + fname + " Do you want to recompute them? ([Y]/N): ")
    else:
        compute = 'Y'
    if compute == 'Y' or compute == '':
        features = feature_function(image_list)
        with open(fname, 'wb') as f:
            print 'saving features to', fname , '...'
            pickle.dump(features, f)
    else:
        # load features
        features = load_features(name)
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

sift_features = None
sift_vocabulary = None
harris_features = None
colorhist_features = None
meta_features = None

# sift features
if feature_active('sift'):
    sift_features = compute_features(image_list, 'sift', ft.get_sift_features)

    # visual vocabulary
    
    fname = args.prefix + base + '_sift_vocabulary.pkl'
    if os.path.isfile(fname):
        compute = raw_input("Found existing vocabulary: " + fname + " Do you want to recompute it? ([Y]/N): ")
    else:
        compute = 'Y'
    if compute == 'Y' or compute == '':
	print 'Creating vocabulary ... \n'
        sift_vocabulary = Vocabulary.Vocabulary(base)
        sift_vocabulary.train(sift_features, args.clusters)
        fname = args.prefix + base + '_sift_vocabulary.pkl'
	with open(fname, 'wb') as f: 
            pickle.dump(sift_vocabulary,f)


if feature_active('colorhist'):
    colorhist_features = compute_features(image_list, 'colorhist', ft.get_colorhist)

if feature_active('harris'):
    harris_features = compute_features(image_list, 'harris', ft.get_harris_features)

#if feature_active('meta'):
#    meta_features = compute_features(image_list, 'meta', ft.get_meta_data)



print 'Creating database ... \n'

db_name = args.prefix + base + '.db'

#check if database already exists
new = False
if os.path.isfile(db_name):
    action = raw_input('Database already exists. Do you want to (r)emove, (a)ppend or (q)uit? ')
    print 'action =', action
else:
    action = 'c'

if action == 'r':
    print 'removing database', db_name , '...'
    os.remove(db_name)
    new = True

elif action == 'a':
    print 'appending to database ... '

elif action == 'c':
    print 'creating database', db_name, '...'
    new = True

else:
    print 'Quit database tool'
    sys.exit(0)



# create indexer
indx = image_search.Indexer(db_name) 
if new == True:
    indx.create_tables()


# Loading necessary features if not in memory yet. Then add features 
# to their corresponding database tables.
if feature_active('sift'): 
    if sift_vocabulary == None:
        sift_vocabulary = load_features('sift_vocabulary')
    if sift_features == None:
        sift_features = load_features('sift')

    print 'Adding sift features to database ... '
    for i in range(len(image_list)):
        indx.add_to_index('sift', image_list[i], sift_features[image_list[i]], sift_vocabulary)

if feature_active('colorhist'):
    if colorhist_features == None:
        colorhist_features = load_features('colorhist')

    print 'Adding colorhist features to database ... '
    for i in range(len(image_list)):
        indx.add_to_colorhist_index(image_list[i], colorhist_features[image_list[i]])

if feature_active('harris'):
    if harris_vocabulary == None:
        harris_vocabulary = load_features('harris_vocabulary')
    if harris_features == None:
        harris_features = load_features('harris')

    print 'Adding harris features to database ... '
    for i in range(len(image_list)):
        indx.add_to_index('harris', image_list[i], harris_features[image_list[i]], harris_vocabulary)

#if feature_active('meta'):
#    if meta_features == None:
#        meta_features = load_features('meta')

	
# commit to database
indx.db_commit()

print 'Done\n'
