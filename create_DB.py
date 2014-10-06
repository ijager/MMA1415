import feature_extraction as feat
import glob
import Vocabulary
import pickle
import image_search

#image_path = "test_images/"
image_path = "ukbench/full/"
types = ('*.jpg', '*.JPG', '*.png')
sift_features = None

nbr_images = 500

# SIFT Features

try:
	sift_file = open('sift.pkl', 'rb')
	sift_features = pickle.load(sift_file)
except:
	print 'Generating sift features'

if sift_features == None:
	sift_file = open('sift.pkl', 'wb')
	image_list = []
	for type_ in types:
		files = image_path + type_
		image_list.extend(glob.glob(files))	

	sift_features = feat.get_sift_features(image_list[0:nbr_images])
	pickle.dump(sift_features, sift_file)




try:
	with open('vocabulary.pkl', 'rb') as f:
		voc = pickle.load(f)
except:
	print 'Creating vocabulary ... \n'
	voc = Vocabulary.Vocabulary('visual')
	voc.train(sift_features, 125, 100)
	with open('vocabulary.pkl', 'wb') as f: 
		pickle.dump(voc,f)
	print 'vocabulary is:', voc.name, voc.nbr_words


# Colorhist features

try:
	with open('colorhist.pkl', 'rb') as f:
		colorhist_features = pickle.load(f)
except:
	print 'Generating Colorhist features ... \n'
	with open('colorhist.pkl', 'wb') as f:
		image_list = []
		for type_ in types:
			files = image_path + type_
			image_list.extend(glob.glob(files))	

		colorhist_features = feat.get_colorhist(image_list[0:nbr_images])
		pickle.dump(colorhist_features, f)




print 'Creating database ... \n'

# create indexer
indx = image_search.Indexer('test.db',voc) 
indx.create_tables()

keys = sift_features.keys()
# go through all images, project features on vocabulary and insert
for i in range(nbr_images):
	indx.add_to_index(keys[i], sift_features[keys[i]])
	indx.add_colorhist_to_index(keys[i], colorhist_features[keys[i]])
	
# commit to database
indx.db_commit()

print 'Done ...\n'
