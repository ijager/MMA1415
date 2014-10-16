#!/usr/bin/env python

import argparse
import pickle
import cv2
import matplotlib.pyplot as plt
import numpy as np
import feature_extraction as ft
import sys
import image_search
import os.path

# Command line parsing is handled by the ArgumentParser object

features = ['sift', 'colorhist', 'harris', 'meta', 'all']

parser = argparse.ArgumentParser(description="Query tool to query the database created by the database tool (dbt.py). Retrieve images based on image content and metadata.")
parser.add_argument("database", help="Path to the database to execute the query on.")
parser.add_argument("query", help="Query image")
parser.add_argument("feature", help="The type of feature to get results on. Chose from "+str(features))
parser.add_argument("--prefix","-p",  help="prefix path to database directory, default = 'db/'", default="db/")

args = parser.parse_args()

# Get file name without extension and prefix
base=os.path.basename(args.database).split('.')[0]


def feature_active(name):
    """ Check if feature 'name' is active
    
    i.e. the feature has been selected via a command line option to be used for processing"""
    return (args.feature == name or args.feature == 'all')




# Starting point of the script
# =======================================

if __name__ == '__main__':
   
    print '\nMulti Media Analysis Query Tool'
    print '================================\n'
    print "Query the database with [", args.query, "] for [", args.feature, "] features..."
    db_name = args.database
    search = image_search.Searcher(db_name)
    if feature_active('sift'):
        print 'Loading SIFT vocabulary ...'
        fname = args.prefix + base + '_sift_vocabulary.pkl'
        with open(fname, 'rb') as f:
            sift_vocabulary = pickle.load(f)

        sift_query = ft.get_sift_features([args.query])[args.query]
        image_words = sift_vocabulary.project(sift_query)
        print 'Query database with a histogram...'
        candidates = search.query_iw('sift', image_words)
        print candidates[0:10]
        for cand in candidates[0:10]:
            print search.get_filename(cand[1])

    if feature_active('harris'):
        print 'Loading Harris vocabulary ...'
        fname = args.prefix + base + '_harris_vocabulary.pkl'
        with open(fname, 'rb') as f:
            harris_vocabulary = pickle.load(f)

        harris_query = ft.get_harris_features([args.query])[args.query]
        image_words = harris_vocabulary.project(harris_query)
        print 'Query database with a histogram...'
        candidates = search.query_iw('harris', image_words)
        print candidates[0:10]
        for cand in candidates[0:10]:
            print search.get_filename(cand[1])


    if feature_active('colorhist'):
        print 'Load colorhist features ..'
        fname = args.prefix + base + '_colorhist.pkl'
        with open(fname, 'rb') as f:
            colorhist_features = pickle.load(f)
        
        colorhist_query = ft.get_colorhist([args.query])[args.query]
        candidates = search.candidates_from_colorhist(colorhist_query, colorhist_features)
        print candidates[0:10]
