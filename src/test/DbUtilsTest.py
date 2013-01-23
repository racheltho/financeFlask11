'''
Created on Jan 21, 2013

@author: rthomas
'''
import unittest
from db_utils import find_rep_db
from models import db

class Test(unittest.TestCase):

    def testRepFind(self):
        s = db.session
        pairs = {'Brown, Brittney': ['Brown', 'Brittney A.'], 'Whitson, Jake': ['Whitson', 'Jacob A.'], 'Chuang, Chris': ["Chuang","Chris"]}
        for a,b in pairs.iteritems():
            res = find_rep_db(a, s)
            self.assertEqual(b[0], res.last_name)
            self.assertEqual(b[1], res.first_name)
