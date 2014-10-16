import math
import numpy as np
import scipy.cluster.hierarchy as h_cluster
from scipy.cluster.hierarchy import linkage as h_linkage
import scipy.spatial.distance as ssd
from Levenshtein import distance as levenshtein_distance
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
		geo1 = lonlat_to_decimal(m1)
		geo2 = lonlat_to_decimal(m2)
		
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
	
def compute_freechoice_tag_distance(m1,m2):
	nameA = m1[0][-1].split('.')[0]
	nameB = m2[0][-1].split('.')[0]
	return levenshtein_distance(nameA,nameB)

def compute_distance(m1, m2):
	predefined_tags_dist	= compute_predefined_tags_distance(m1,m2)
	free_choice_tag_dist 	= compute_freechoice_tag_distance(m1,m2)
	geographical_dist 		= compute_geographic_distance(m1,m2)
	
	print(predefined_tags_dist)
	print(free_choice_tag_dist)
	print(geographical_dist)
		
		
	return predefined_tags_dist + free_choice_tag_dist + geographical_dist
	
def rank_by_geocluster(geotagged_images):
	N = len(geotagged_images)
	geodistance_matrix = np.zeros((N,N))
	if(N > 0):
		for i in range(0,N):
			for j in range(i+1,N):
				d = int(compute_geographic_distance(geotagged_images[i][1],geotagged_images[j][1]))
				geodistance_matrix[i,j] = d
				geodistance_matrix[j,i] = d
		
	L = h_linkage(ssd.squareform(geodistance_matrix))
	C = h_cluster.fcluster(L,0.8) # KB: I don't know what the 0.8 should be doing here :S. This is just a guess
	cluster_list = []
	for i in range(len(geotagged_images)):
		cluster_list.append((C[i],geotagged_images[i]))

	
	# rank the clusters based on distance to the query image
	# as a distance function, we just use the average distance to the 
	# cluster elements
	
	# for each cluster
		# for every image in that cluster
			# retrieve the distance to that image
			# add distance to sum
		# divide by nr of images in cluster
		# store average cluster distance
		
	clus_avg_distances = {}
	
	for k in range(1,max(C)+1):
		clus_avg_distances[k] = 0
		
	distances_to_query = geodistance_matrix[0,:]
	for clus_num in C:
		s = clus_avg_distances[clus_num]
		count = 0
		for i in range(N):
			if C[i] == clus_num:
				s += distances_to_query[i]
		s = s / list(C).count(clus_num)
		clus_avg_distances[clus_num] = s
	
	clus_avg_distances = clus_avg_distances.items()
	clus_avg_distances = sorted(clus_avg_distances, key=lambda x: x[1])
	return (C, clus_avg_distances)
	
def rank_by_predef_tags(query_metadata, geotagged_images, clusters, clus_avg_distances):
	# take the images in the highest ranked cluster
	# while there are less than 10 candidates, add whole clusters
	top_georanked_candidates = []
	clus_rank = 0 # use this later to know how many ranked clusters we end up with
	while(len(top_georanked_candidates) < 20): #assume there are at least 10 geotagged images!!!
		next_cluster_number = clus_avg_distances[clus_rank][0]
		# retrieve all images in the cluster with this number
		# add them to the top georanked candidates
		for i in range(len(geotagged_images)):
			if clusters[i] == next_cluster_number:
				top_georanked_candidates.append((clus_rank, geotagged_images[i]))
		
		clus_rank+=1
		
	# for i in range(len(top_georanked_candidates)):
	#	print (str(top_georanked_candidates[i][0]) + " " + str(top_georanked_candidates[i][1][0][4])) 
	
	# rank those in the highest cluster on predefined tag similarity
	# then go through the next clusters and rank those in the same way
	top_predef_candidates = []
	for rank in range(clus_rank):
		single_cluster = [x[1] for x in top_georanked_candidates if x[0] == rank]
		single_cluster_ranking = []
		for m in single_cluster:
			# add the rank to the distance so that a better cluster always has lower distance
			single_cluster_ranking.append((compute_predefined_tags_distance(m, query_metadata)+rank, m))
		single_cluster_ranking = sorted(single_cluster_ranking, key=lambda x: x[0])
		top_predef_candidates.extend(single_cluster_ranking)
	
	return top_predef_candidates
	
def rank_by_free_tags(query_metadata, geotagged_images, top_predef_candidates):
	# now rank ties based on free tag similarity
	final_ranking = []		
	worst_rank = max([x[0] for x in top_predef_candidates])
	worst_from_previous_cluster = 0
	for rank in range(worst_rank):
		tied_rank = [x[1] for x in top_predef_candidates if x[0] == rank]
		tiebreaker = []
		for m in tied_rank:
			tiebreaker.append((compute_freechoice_tag_distance(m, query_metadata)+worst_from_previous_cluster,m))
		tiebreaker = sorted(tiebreaker, key=lambda x: x[0])
		if len(tiebreaker) > 0:
			worst_from_previous_cluster = tiebreaker[-1][0]
		final_ranking.extend(tiebreaker) # note that if the freechoice distance is the same, this still contains ties
		
	return final_ranking
	
	
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







