import pickle
import numpy as np
from pysqlite2 import dbapi2 as sqlite


class Indexer(object):

	def __init__(self, db):
		self.con = sqlite.connect(db)

	def __del__(self):
		self.con.close()
	
	def db_commit(self):
		self.con.commit()
	
	def create_tables(self):
		self.con.execute('create table imlist(filename)') 
		self.con.execute('create index im_idx on imlist(filename)') 

		self.con.execute('create table sift_imwords(imid,wordid,vocname)') 
                self.con.execute('create index sift_imid_idx on sift_imwords(imid)') 
		self.con.execute('create index sift_wordid_idx on sift_imwords(wordid)') 

		self.con.execute('create table sift_imhistograms(imid,histogram,vocname)') 
		self.con.execute('create index sift_imidhist_idx on sift_imhistograms(imid)') 

		self.con.execute('create table colorhists(imid, hist)')
		self.con.execute('create index colorhist_idx on colorhists(imid)') 

		self.con.execute('create table harris_imwords(imid,wordid,vocname)') 
                self.con.execute('create index harris_imid_idx on harris_imwords(imid)') 
		self.con.execute('create index harris_wordid_idx on harris_imwords(wordid)') 

		self.con.execute('create table harris_imhistograms(imid,histogram,vocname)') 
		self.con.execute('create index harris_imidhist_idx on harris_imhistograms(imid)') 


		self.db_commit()

	def add_to_index(self, type, imname, descr, voc):
		""" Take an image with feature descriptors, 
			project on vocabulary and add to database. """

		print 'indexing', imname

		# get the imid
		imid = self.get_id(imname)

		#get the words
		imwords = voc.project(descr)
		nbr_words = imwords.shape[0]

		# link each word to image
		for i in range(nbr_words):
			word = imwords[i]
			# wordid is the word number itself
			self.con.execute("insert into "+type+"_imwords(imid,wordid,vocname) values (?,?,?)", (imid,word,voc.name))

		# store word histogram for image
		# use pickle to encode NumPy arrays as strings
		self.con.execute("insert into "+type+"_imhistograms(imid,histogram,vocname) values (?,?,?)", (imid,pickle.dumps(imwords), voc.name))

	def add_to_colorhist_index(self, imname, hist):

		print 'indexing', imname

		# get the imid
		imid = self.get_id(imname)

		self.con.execute("insert into colorhists(imid, hist) values (?,?)", (imid, pickle.dumps(hist)))

	def is_indexed(self, imname):
		""" Returns True is imname has been indexed. """

		im = self.con.execute("select rowid from imlist where filename='%s'" % imname).fetchone()
		return im != None

	def get_id(self, imname):
		""" Get an entry id and add if not present. """

		cur = self.con.execute("select rowid from imlist where filename='%s'" % imname)
		res = cur.fetchone()
		if res == None:
			cur = self.con.execute("insert into imlist(filename) values ('%s')" % imname)
			return cur.lastrowid
		else:
			return res[0]

	

class Searcher:

	def __init__(self, db, voc):
		self.con = sqlite.connect(db)
		self.voc = voc

	def __del__(self):
		self.con.close()

	def candidates_from_word(self, imword):
		""" Get list of images containing imword/ """

		im_ids = self.con.execute(
				"select distinct imid from imwords where wordid=%d" % imword).fetchall()
		return [i[0] for i in im_ids]


	def color_hist_distance(hist1, hist2):
		return np.sum((hist1-hist2)**2)

	def candidates_from_colorhist(self, hist, features):
		result = []
		names = []
		for key in features.keys():
			d = np.sum((hist-features[key])**2)
			result.append(d)
			names.append(key)
		i = np.argsort(result)
		return np.array(names)[i]

	def candidates_from_histogram(self, imwords):
		""" Get list of images wth similar words. """

		# get the word ids
		words = imwords.nonzero()[0]
		# find candidates
		candidates = []
		for word in words:
			c = self.candidates_from_word(word)
			candidates += c
		
		# take all unique words and reverse sort on occurence
		tmp = [(w, candidates.count(w)) for w in set(candidates)]
		tmp.sort(cmp=lambda x, y:cmp(x[1],y[1]))
		tmp.reverse()

		# return sorted list, best matches first
		return [w[0] for w in tmp]

	def get_colorhist(self, imname):
		""" Return the color histogram for an image. """
		im_id = self.con.execute(
				"select rowid from imlist where filename='%s'" % imname).fetchone()
		s = self.con.execute(
				"select hist from colorhists where rowid='%d'" % im_id).fetchone()

		# use pickle to decode NumPy arrays from string
		return pickle.loads(str(s[0]))


	
	def get_imhistogram(self, imname):
		""" Return the word histogram for an image. """

		im_id = self.con.execute(
				"select rowid from imlist where filename='%s'" % imname).fetchone()
		s = self.con.execute(
				"select histogram from imhistograms where rowid='%d'" % im_id).fetchone()

		# use pickle to decode NumPy arrays from string
		return pickle.loads(str(s[0]))

	def query(self, imname):
		""" Find a list of matching images for imname"""

		h = self.get_imhistogram(imname)
		candidates = self.candidates_from_histogram(h)

		matchscores = []
		for imid in candidates:
			# get the name
			cand_name = self.con.execute(
					"select filename from imlist where rowid=%d" % imid).fetchone()
			cand_h = self.get_imhistogram(cand_name)
			cand_dist = np.sqrt( np.sum( (h-cand_h)**2 ) ) #use L2 distance
			matchscores.append( (cand_dist, imid) )

			#return a sorted list of distances and databse ids
			matchscores.sort()
		return matchscores


	def get_filename(self,imid):
		""" Return the filename for an image id"""
		s = self.con.execute(
				"select filename from imlist where rowid='%d'" % imid).fetchone()
		return s[0]
