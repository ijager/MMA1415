# -*- coding: utf-8 -*-
import math
import numpy as np
import scipy.cluster.hierarchy as h_cluster
from scipy.cluster.hierarchy import linkage as h_linkage
import scipy.spatial.distance as ssd
from geopy.distance import vincenty


def has_geotag(d):
	# geotag is at position 1, has zero value if geotag was not found included
	return d[1] != 0

def lonlat_to_decimal(geo):
	# example ([52, 0, 36], 'N', [4, 21, 36], 'E', 'delft')
	result = [geo[0][0] + geo[0][1] / 60.0 + geo[0][2]/3600.0, geo[2][0] + geo[2][1] / 60.0 + geo[2][2]/3600.0]	
	
	if geo[1] == 'S':
		result[0] = -result[0]
	if geo[3] == 'W':
		result[1] = -result[1]
		
	return (result[0], result[1])	
		
def compute_geographic_distance(m1,m2):
	geographical_dist = -1
	if not has_geotag(m1) or not has_geotag(m2):
		# can't do geographic distance
		geographical_dist = 0		
	else:
		geo1 = lonlat_to_decimal(m1[1])
		geo2 = lonlat_to_decimal(m2[1])
		
		geographical_dist = vincenty(geo1,geo2)
	return geographical_dist.meters

def compute_predefined_tags_distance(m1,m2):
	'''
	format is:
	vvv_y_xx_z_w_tag.jpg
	vvv 	name code													[name] 0
	y		tourist (t), student (r), unknown (y)						[perspective] 1
	xx		Oude Jan (oj), Nieuwe Kerk (nk), Raadhuis (rh), Other (xx)	[object] 2 
	z		Positive (p), Negative (n), None (z)						[mood] 3
	w		Depicts water (w), Doesn't depict water (m)					[water] 4
	tag		Tag of choice												[tag] 5
	'''
	tagsA = m1[0][:4]
	tagsB = m2[0][:4]
	distance = 0
	
	# if the tags are known and different, add score
	# if both are 'unknown', do not consider them to be different
	
	# we only have three cases, but if we'd had more we might need to make 
	# the code a bit more generalized	
	if not (tagsA[0] == tagsB[0] and tagsA[0] != 'y'):
		distance += 1
		
	if not(tagsA[1] == tagsB[1] and tagsA[1] != 'xx'):
		distance += 1
		
	# we consider two None tags as the same
	if not (tagsA[2] == tagsB[2]):
		distance += 1
		
	if not (tagsA[3] == tagsB[3]):
		distance += 1	
		
	return distance
	
	
def metadata_ranking(list_of_metadata, query_metadata):
	'''
	idea: 
	When is geotagging a good measure for similarity?
	If two queries are really close together.
	What does it mean to be 'close'?
	Limburg and Texel are 'close' compared to Los Angeles and New York.
	Limburg and Texel are not 'close' compared to Oude Jan and Nieuwe Kerk
	
	Use hierarchical clustering of all data on distance to query image
	Sort the cluster that is closest on distance. Find standard deviation of 
	the cluster. Define ties as those clusters within one standard deviation 
	of eachother. Rank the ties based on predefined tag similarities.
	If we still have ties, rank based on levenstein of title
	
	If we still have ties, the differences are probably not worth mentioning.
	
	Is this justifiable?
	'''
	geotagged_images = []
	not_geotagged_images = []
	
	if has_geotag(query_metadata):
		geotagged_images.append(query_metadata) # query is the first element
		for m in list_of_metadata:
			if has_geotag(m):
				geotagged_images.append(m)
			else:
				not_geotagged_images.append(m)
	
	(clusters, clus_avg_distances) 	= rank_by_geocluster(geotagged_images)	
	top_predef_candidates 			= rank_by_predef_tags(query_metadata, geotagged_images, clusters, clus_avg_distances)
	final_ranking 					= rank_by_free_tags(query_metadata, geotagged_images, top_predef_candidates)
	# !!! now WTF to do with the images that do not have a geotag !!!
	
	for c in final_ranking:
		# print rank, friendly name
		print c[0] , c[1][0][4]	
	
	
	

#delft = ([52, 0, 36], 'N', [4, 21, 36], 'E', 'delft')
#fiji = ([17, 11, 9.6], 'S', [178, 39, 32], 'E', 'fiji')
#newyork = ([40, 39, 51], 'N', [73, 56, 19], 'W', 'newyork')
#moskow = ([55, 45, 0], 'N', [37, 37, 12], 'E', 'moscow')
#santiago = ([33, 27, 36], 'S', [70,38,24], 'W', 'santiago')
#lagos = ([6,0,27],'N',[3,28,12],'E','lagos')
#bergen = ([60,22,48],'N',[5,20,24],'E','bergen')

#foo = [delft, fiji, newyork, moskow, santiago, lagos, bergen]
#for a in foo:
	#for b in foo:
		#if a[4] != b[4]:
			#print(a[4] + " to " + b[4]+ ": " + str(compute_geographic_distance(a,b)) +"m") 







