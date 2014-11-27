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
        self.con.execute('create table vidlist(filename)')
        self.con.execute('create index vid_idx on vidlist(filename)')
        
        self.con.execute('create table colorhists(vidid,hists)')
        self.con.execute('create index colorhists_vidid_idx on colorhists(vidid)')
        
        self.con.execute('create table tempdiffs(vidid, diffs)')
        self.con.execute('create index tempdiffs_vidid_idx on tempdiffs(vidid)')
        
        self.con.execute('create table mfccs(vidid, coeffs)')
        self.con.execute('create index mfccs_vidid_idx on mfccs(vidid)')
        
        self.con.execute('create table audiopowers(vidid, powers)')
        self.con.execute('create index audiopowers_vidid_idx on audiopowers(vidid)')
            
    def add_to_index(self, vidname, descr):
        """ Take an video with feature descriptors, 
            add to database. """

        print 'indexing', vidname

        # get the imid
        vidid = self.get_id(vidname)

        # get features from descriptor
        mfccs = descr['mfcc'] # Nx13 np array (or however many mfcc coefficients there are)
        audio = descr['audio'] # Nx1 np array
        colhist = descr['colhist'] # Nx3x256 np array
        tempdif = descr['tempdif'] # Nx1 np array

        # store descriptor per video
        # use pickle to encode NumPy arrays as strings
        self.con.execute("insert into colorhists(vidid,hists) values (?,?)", (vidid,pickle.dumps(colhist)))
        self.con.execute("insert into tempdiffs(vidid,diffs) values (?,?)", (vidid,pickle.dumps(tempdif)))
        self.con.execute("insert into mfccs(vidid,coeffs) values (?,?)", (vidid,pickle.dumps(mfccs)))
        self.con.execute("insert into audiopowers(vidid,powers) values (?,?)", (vidid,pickle.dumps(audio)))
        
    def get_id(self, vidname):
        """ Get an entry id and add if not present. """

        cur = self.con.execute("select rowid from vidlist where filename='%s'" % vidname)
        res = cur.fetchone()
        if res == None:
            cur = self.con.execute("insert into vidlist(filename) values ('%s')" % vidname)
            return cur.lastrowid
        else:
            return res[0]
