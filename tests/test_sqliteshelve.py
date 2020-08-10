import unittest
import os
import pickle
import sqlite3
import sys
sys.path.append('../')

import sqliteshelve as shelve

class SQLiteShelfTestCase(unittest.TestCase):

    def setUp(self):
        self.db = shelve.open('test_shelf')
        

    def test_new_shelf(self):
        """ Ensures Shelf instance is created as expected """
        self.assertIsInstance(self.db, shelve.Shelf)
        self.assertEqual(len(self.db), 0 )

    def test__setitem__(self):
        """Ensure's a Shelf item can be assigned a key value"""
        key = "MN"
        self.db[key] = "Minnesota"
        cursor = self.db.db.cursor()
        cursor.execute("select value_str from shelf where key_str = :key", {'key': key})
        result = cursor.fetchone()
        cursor.close()
        result_str = pickle.loads(result[0])
        self.assertEqual(result_str, "Minnesota")
            
    def tearDown(self):
        if os.path.exists('test_shelf'):
            os.remove('test_shelf')         

