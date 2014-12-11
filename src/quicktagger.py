import cv2
import glob
from PIL import Image
from time import gmtime, strftime
import re

import pyexiv2
import os




image_path = "../"
types = ('*.jpg', '*.JPG', '*.png')
numbered_file_regex = re.compile('.*\(\d*\)')
same_name_counter_regex = re.compile('\(\d*\)')

image_list = []

def process_tag_query(tag_type):
	# possible_types = ['name', 'perspective' , 'object', 'mood', 'water', 'choice']
	result = 0
	valid_input_given = False
	while not valid_input_given:
		query_string = ''
		if tag_type == 'name':
			query_string = 'Image name:\n'
		elif tag_type == 'perspective':
			query_string = 'Perspective tag. (t)ourist, (s)tudent, (y) unknown:\n'
		elif tag_type == 'object':
			query_string = 'Object tag. (oj) Oude Jan, (nk) Nieuwe Kerk (nk), (rh) Raadhuis, (xx) Other:\n'
		elif tag_type == 'mood':	
			query_string = 'Mood tag. (p)ositive, (n)egative, (z) none:\n'
		elif tag_type == 'water':
			query_string = 'Water tag. (w)ater, (m) no water:\n'
		elif tag_type == 'choice':
			query_string = 'Other tags. Separate by comma:\n'		
		
		user_input = raw_input(query_string)
		
		if len(user_input) == 0:
			print('No input read. Type \'exit\' to exit.')
			valid_input_given = False
			continue
		
		user_input = user_input.lower()
		invalid_reason = ''
		if tag_type == 'name':
			# just assume any text is valid as a name
			result = user_input
			valid_input_given = True
		
		elif tag_type == 'perspective':
			if user_input in ['t', 'tourist', '(t)ourist']:
				result = 'tourist_perspective'
				valid_input_given = True
			elif user_input in ['s', 'student', '(s)tudent']:
				result = 'student_perspective'
				valid_input_given = True
			elif user_input in ['y', 'unknown', '(u)nknown']:
				result = 'unknown_perspective'
				valid_input_given = True
			else:
				# no valid input found
				valid_input_given = False
				invalid_reason = 'No valid perspective tag found. Should be t, s, or y'
			
		elif tag_type == 'object':
			if user_input in ['oude jan', 'oudejan', 'oj', 'o']:
				result = 'Oude_Jan'
				valid_input_given = True
			elif user_input in ['nk', 'n', 'nieuwe kerk', 'nieuwekerk']:
				result = 'Nieuwe_Kerk'
				valid_input_given = True
			elif user_input in ['rh', 'r', 'raadhuis', 'raad huis']:
				result = 'Raadhuis'
				valid_input_given = True
			elif user_input in ['xx', 'x', 'other']:
				result = 'other_object'
				valid_input_given = True
			else:
				# no valid input found	
				valid_input_given = False
				invalid_reason = 'No valid perspective tag found. Should be oj, nk, rh, or xx'
		
		elif tag_type == 'mood':
			if user_input in ['(p)ositive', 'positive', 'p']:
				result = 'positive_mood'
				valid_input_given = True
			elif user_input in ['(n)egative', 'n', 'negative']:
				result = 'negative_mood'
				valid_input_given = True
			elif user_input in ['z', 'none']:
				result = 'no_mood'
				valid_input_given = True
			else:
				valid_input_given = False
				invalid_reason = 'No valid mood tag found. Should be p, n, or z'
				
		elif tag_type == 'water':
			if user_input in ['w', '(w)ater', 'water', 'yes']:
				result = 'water_present'
				valid_input_given = True
			elif user_input in ['m' , 'no water', 'no', 'none', 'n']:
				result = 'no_water'
				valid_input_given = True;
			else:
				valid_input_given = False
				invalid_reason = 'No valid water tag found. Should be w or m'
				
		elif tag_type == 'choice':
			# tags are separated by comma
			tags  = user_input.split(',')
			strip_tags = []
			for t in tags:
				stripped = t.strip()
				if len(stripped) > 0:
					strip_tags.append(stripped)
			valid_input_given = True
			result = strip_tags				
		
		# allow for quiting
		if user_input in ['exit', 'quit']:
			result = 'exit'
			valid_input_given = True
			
		if not valid_input_given:
			print('Input \'' +user_input+ '\' is invalid. '+ invalid_reason)	
	return result
		
	

for type_ in types:
	files = image_path + type_
	image_list.extend(glob.glob(files))	

print('Quicktagger v1.337')
print('To enter the prespecified tags, you can usually just enter the first letter, so \'n\' instead of \'nk\' or \'nieuwe kerk\'.')
print('If you\'ve made a mistake on an image, enter \'back\' after finishing the other tags of that image.')
print('Enter \'exit\' at any time to quit.')

window_name = 'Tag this image'
i = 0
keep_tagging = True
tagged_images = {}
while i < len(image_list) and keep_tagging:
	im_name = image_list[i]
	print im_name
	img = cv2.imread(im_name)
	
	cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
	cv2.resizeWindow(window_name, 800, 600)
	cv2.startWindowThread()
	cv2.imshow(window_name,img)

	print('\nEnter tags for: ' + im_name + ' ('+str(i+1)+'/'+str(len(image_list))+')')
	possible_types = ['name', 'perspective' , 'object', 'mood', 'water', 'choice']
	tag_dict = {}
	for t in possible_types:
		tags = process_tag_query(t)
		if tags == 'exit':
			keep_tagging = False
			break
		else:
			tag_dict[t] = tags
	
	if not keep_tagging:
		break
	
	print('FILE: ' + im_name +' has tags:')
	for key in possible_types[:5]:
		print(key.upper() +': ' + tag_dict[key])
	print('TAGS:')
	for tag in tag_dict['choice']:
		print('-'+tag+'-')
	print('Type \'exit\' to discard this image and exit.')
	print('Type \'save\' to save all tagged images so far.')
	print('Type \'back\' to redo this image if you have to correct a mistake.')
	correct = raw_input('Any other string to [continue]: ')
	if correct.lower() in ['exit', 'quit']:
		break
	elif correct.lower() == 'back':
		i = i - 1
	elif correct.lower() == 'save':
		keep_tagging = False
	
	tagged_images[im_name] = tag_dict
	i = i + 1
	
cv2.destroyWindow(window_name)

valid_input_given = False
while not valid_input_given:
	if i > 0:
		save_tagged_images = raw_input('('+str(i)+'/'+str(len(image_list))+') have been tagged. Create tagged images? [y]es/no: ')
		if save_tagged_images.lower() in ['', 'y', 'yes']:
			valid_input_given = True
			folder_name = 'tagged-images/tagged_images-'+strftime("%Y-%m-%d %H:%M:%S")
			if not os.path.exists(folder_name):
				os.makedirs(folder_name)
			print('Saving tagged images to /'+folder_name+'/')
			for im_name, tag_dict in tagged_images.iteritems():
				# load old image
				im_pil = Image.open(im_name)
				file_extension = os.path.splitext(im_name)[1].lower()
				
				fullpath = folder_name + '/' + tag_dict['name'] + file_extension
				print('Saving file: ' +fullpath) 
				# if name already taken, append an index number
				image_duplicate_nr = 1
				while os.path.exists(fullpath):
					print(fullpath +' already exists, saving as: ')
					s = fullpath.split('.')
					fullpath = ''.join(s[:len(s)-1]) 
					if numbered_file_regex.match(fullpath):
						# there is already a number in the filename
						m = same_name_counter_regex.search(fullpath)
						fullpath = fullpath[:-(m.end()-m.start())]
					fullpath = fullpath + '(' + str(image_duplicate_nr) +')' + file_extension
					print(fullpath)
					image_duplicate_nr += 1
				
				# save a copy of the image first
				im_pil.save(fullpath, exif=im_pil.info['exif'])
				
				# copy exif from old image
				exif_data = pyexiv2.ImageMetadata(fullpath)
				exif_data.read()
				exif_data['Exif.Image.DocumentName'] = tag_dict['name']
				# store other tags in usercomment				
				user_comment_tag = 	tag_dict['perspective'] +', ' \
									+tag_dict['object'] +', ' \
									+tag_dict['mood'] +', '\
									+tag_dict['water'] + ', '
				for tag in tag_dict['choice']:
					user_comment_tag += tag + ', '
				user_comment_tag = user_comment_tag[:-2] # remove last comma
				exif_data['Exif.Photo.UserComment'] = user_comment_tag
				exif_data.write()
				
		elif save_tagged_images.lower() in ['n', 'no']:
			valid_input_given = True
			print('Discarding tags.')
		else:
			valid_input_given = False
			print('It is just yes or no, how hard can it be?')
	else:
		valid_input_given = True # so we can exit
exit(0)


