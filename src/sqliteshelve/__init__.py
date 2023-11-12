# sqliteshelve module
import os
import pickle
import shelve
import sqlite3


class Shelf(shelve.Shelf):
    """Hackified Shelf class with sqlite3"""

    def __init__(self, dbpath):
        """Opens or creates an existing sqlite3_shelf"""

        self.db = sqlite3.connect(dbpath)
        # create shelf table if it doesn't already exist
        cursor = self.db.cursor()
        cursor.execute(
            "select * from sqlite_master where type = 'table' and tbl_name = 'shelf'"
        )
        rows = cursor.fetchall()
        if len(rows) == 0:
            cursor.execute(
                "create table shelf (id integer primary key autoincrement, key_str text, value_str text, unique(key_str))"
            )
        cursor.close()

    def __setitem__(self, key, value):
        """Sets an entry for key to value using pickling"""
        pdata = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
        curr = self.db.cursor()
        curr.execute(
            "insert or replace into shelf (key_str,value_str) values (:key,:value)",
            {"key": key, "value": sqlite3.Binary(pdata)},
        )
        curr.close()

    def get(self, key, default_value):
        """Returns an entry for key"""
        curr = self.db.cursor()
        curr.execute("select value_str from shelf where key_str = :key", {"key": key})
        result = curr.fetchone()
        curr.close()
        if result:
            return pickle.loads(str(result[0]))
        else:
            return default_value

    def __getitem__(self, key):
        """Returns an entry for key"""
        curr = self.db.cursor()
        curr.execute("select value_str from shelf where key_str = :key", {"key": key})
        result = curr.fetchone()
        curr.close()
        if result:
            return pickle.loads(result[0])
        else:
            raise (KeyError, "Key: %s does not exist." % key)

    def keys(self):
        """Returns list of keys"""
        curr = self.db.cursor()
        curr.execute("select key_str from shelf")
        keylist = [row[0] for row in curr]
        curr.close()
        return keylist

    def __contains__(self, key):
        """
        implements in operator
        if <key> in db
        """
        return key in self.keys()

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        """Returns number of entries in shelf"""
        return len(self.keys())

    def __delitem__(self, key):
        """Deletes an existing item."""
        curr = self.db.cursor()
        curr.execute("delete from shelf where key_str = '%s'" % key)
        curr.close()

    def close(self):
        """
        Closes database and commits changes
        """
        self.db.commit()


def open(dbpath):
    """Creates and returns a Shelf object"""
    return Shelf(dbpath)


def close(db):
    """
    commits changes to the database
    """
    db.close()
