# -*- coding: utf-8 -*-
import exifread
import glob

# extract tags
def extract_tags(filename):
	'''
	format is:
	vvv_y_xx_z_w_tag.jpg
	vvv 	name code													[name] 0
	y		tourist (t), student (r), unknown (y)						[perspective] 1
	xx		Oude Jan (oj), Nieuwe Kerk (nk), Raadhuis (rh), Other (xx)	[object] 2 
	z		Positive (p), Negative (n), None (z)						[mood] 3
	w		Depicts water (w), Doesn't depict water (m)					[water] 4
	tag		Tag of choice <= 12 letters									[tag] 5
	'''
	words = filename.split('_')
	result = 0
	if len(words) != 6:
		print('Improperly formatted tags')
		result = 1	
	
	if not words[1] in ('t', 'r', 'y'):
		print('Invalid tag for perspective: ' + words[1])
		result = 1
		
	if not words[2] in ('oj', 'nk', 'rh', 'xx'):
		print('Invalid tag for object: ' + words[2])
		result = 1
		
	if not words[3] in ('p', 'n', 'z'):
		print('Invalid tag for mood: ' + words[3])
		result = 1
		
	if not words[4] in ('w', 'm'):
		print('Invalid tag for water: ' + words[4])
		result = 1
		
	if len(words[5]) > 12:
		print('Title is too long: ' + words[5])
		result = 1
		
	if result == 0:
		result = words
	
	return result
		

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
			
			friendly_name = str(longitude[0]) + '° ' + str(longitude[1]) +'\' ' + str(longitude[2]) +'\'\' ' + longRef 
			friendly_name += ', ' + str(latitude[0]) + '° ' + str(latitude[1]) +'\' ' + str(latitude[2]) +'\'\' ' + latRef 
			
			return (longitude, longRef, latitude, latRef, friendly_name)
			
		
	return 0

extract_exif('../DelftImages/agi_r_xx_n_w_gracht.jpg')



