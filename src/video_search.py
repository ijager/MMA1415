import pickle
import numpy as np
from pysqlite2 import dbapi2 as sqlite

class Searcher:

    def __init__(self, db):
        self.con = sqlite.connect(db)

	def __del__(self):
		self.con.close()
     
	def get_filename(self,vidid):
		""" Return the filename for a video id"""
		s = self.con.execute("select filename from vidlist where rowid='%d'" % vidid).fetchone()
		return s[0]

    def get_features_for(self, vid_name):
        t = self.con.execute("select vidid from colorhists").fetchone()
        vidid = self.con.execute("select rowid from vidlist where filename='%s'" % vid_name).fetchone()
        query = "select hists from colorhists where vidid="+str(vidid[0])
        s = self.con.execute(query).fetchone()
		# use pickle to decode NumPy arrays from string
        return pickle.loads(str(s[0]))
