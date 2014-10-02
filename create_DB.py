import feature_extraction as feat
import glob
import Vocabulary
import pickle

#image_path = "test_images/"
image_path = "ukbench/full/"
types = ('*.jpg', '*.JPG', '*.png')
sift_features = None

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

	sift_features = feat.get_sift_features(image_list[0:500])
	pickle.dump(sift_features, sift_file)

print 'Creating vocabulary ... \n'

voc = Vocabulary.Vocabulary('visual')
voc.train(sift_features, 1000, 100)

with open('vocabulary.pkl', 'wb') as f: 
	pickle.dump(voc,f)
print 'vocabulary is:', voc.name, voc.nbr_words
