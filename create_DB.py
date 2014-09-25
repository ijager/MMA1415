import feature_extraction as feat
import glob

image_path = "test_images/"
types = ('*.jpg', '*.JPG', '*.png')

image_list = []
for type_ in types:
	files = image_path + type_
	image_list.extend(glob.glob(files))	

print image_list[0:4]

sift_features = feat.get_sift_features(image_list[0:8])
print sift_features
