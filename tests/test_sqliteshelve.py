import unittest
import os
import pickle
import sqlite3
import sys
sys.path.append('../src')

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
            
    def test__getitem__(self):
        """Ensures a Shelf item can be retrieved by key"""
        key = "MI"
        value = "Michigan"
        pdata = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
        curr = self.db.db.cursor()
        curr.execute("insert or replace into shelf (key_str, value_str) values (:key, :value)", {'key': key, 'value': sqlite3.Binary(pdata)})
        curr.close()
        state = self.db[key]
        self.assertEqual(state, "Michigan")

    def test_keys(self):
        """Ensures the keys method returns a list of keys in a shelf"""
        self.db["AL"] = "Alabama"
        self.db["CA"] = "California"
        self.db["MI"] = "Michigan"
        self.db["MN"] = "Minnesota"
        expected_keys = {"AL", "CA", "MI", "MN"}
        self.assertEqual(set(self.db.keys()), expected_keys)
        self.assertEqual(len(self.db.keys()), 4)
        
    def test___contains__(self):
        """Ensures in operator works on Shelf object"""
        self.db["AL"] = "Alabama"
        self.db["CA"] = "California"
        self.db["MI"] = "Michigan"
        self.db["MN"] = "Minnesota"
        self.assertIn("AL", self.db)
        self.assertIn("MN", self.db)
        self.assertIn("MI", self.db)
        self.assertIn("CA", self.db)
        self.assertNotIn("TX", self.db)

    def test__delitem__(self):
        """Ensures del works on a Shelf"""
        self.db["AL"] = "Alabama"
        self.db["CA"] = "California"
        self.db["MI"] = "Michigan"
        self.db["MN"] = "Minnesota"
        del self.db["AL"]
        self.assertEqual(len(self.db), 3)
        self.assertNotIn("AL", self.db)
    
    def test_contextmanager(self):
        """
        Ensures contextmanager works for sqliteshelve.Shelf
        """
        with shelve.open("ctx_shelve") as ctx_shelve:
            ctx_shelve["MN"] = "Minnesota"
            ctx_shelve["OR"] = "Oregon"
            ctx_shelve["CA"] = "California"

        with shelve.open("ctx_shelve") as ctx:
            keys = ctx.keys()
            self.assertIn("MN", keys)
            self.assertIn("OR", keys)
            self.assertIn("CA", keys)

    def tearDown(self):
        if os.path.exists('test_shelf'):
            os.remove('test_shelf')         

