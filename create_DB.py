import feature_extraction as feat
import glob
import Vocabulary
import pickle

image_path = "test_images/"
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

	print image_list[0:4]

	sift_features = feat.get_sift_features(image_list[0:10])
	pickle.dump(sift_features, sift_file)

	print sift_features

voc = Vocabulary.Vocabulary('visual')
voc.train(sift_features)

with open('vocabulary.pkl', 'wb') as f: 
	pickle.dump(voc,f)
print 'vocabulary is:', voc.name, voc.nbr_words
