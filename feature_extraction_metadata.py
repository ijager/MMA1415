# -*- coding: utf-8 -*-
import exifread
import pyexiv2
import glob
import os

# extract tags
def extract_tags(filename):
	exif_data = pyexiv2.ImageMetadata(filename)
	exif_data.read()
	tags = exif_data['Exif.Photo.UserComment'].value.split(',')
	tags = [t.strip() for t in tags]
	return tags

# extract exif
def extract_exif(filename):
	# find if there is a geolocation tag, and if so return it.
	# if geolocation was not turned on, return 'no-geotag'
	
	with open(filename) as f:
		exif_tags = exifread.process_file(f)
		if 'GPS GPSLongitude' in exif_tags:
			# assume that all other GPS tags are in there now
			'''
			GPS GPSLongitude [4, 21, 761/20]
			GPS GPSImgDirection 17621/362
			GPS GPSLatitude [52, 0, 1054/25]
			GPS GPSDate 2014:02:18
			Image GPSInfo 704
			GPS GPSLatitudeRef N
			GPS GPSImgDirectionRef T
			GPS GPSAltitudeRef 0
			GPS GPSTimeStamp [11, 56, 6]
			GPS GPSAltitude 3653/1134
			GPS GPSLongitudeRef E
			'''
			longitude 	= [x.num / x.den for x in exif_tags['GPS GPSLongitude'].values]
			latitude 	= [x.num / x.den for x in exif_tags['GPS GPSLatitude'].values]
			longRef		= exif_tags['GPS GPSLongitudeRef'].values
			latRef		= exif_tags['GPS GPSLatitudeRef'].values		
			
			friendly_name = str(longitude[0]) + 'd ' + str(longitude[1]) +'\' ' + str(longitude[2]) +'\'\' ' + longRef 
			friendly_name += ', ' + str(latitude[0]) + 'd ' + str(latitude[1]) +'\' ' + str(latitude[2]) +'\'\' ' + latRef 
			
			return (longitude, longRef, latitude, latRef, friendly_name)
			
		
	return 0

def extract_metadata(im_list):
	features = []
	for im_name in im_list:
		tags = extract_tags(im_name)
		geotags = extract_exif(im_name)
		features.append( (tags, geotags) )
		
	return features	
	



