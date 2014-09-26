sqlite-shelve
=============

* Implements a shelve-like store in SQLite
* Applications incorporating this module can utilize the interfaces of SQLiteShelve class just like they do the Shelve class
* In most ordinary use cases, applications that use the builtin shelve module can switch to SQLiteShelve with the followng:

```
import sqliteshelve as shelve

d = shelve.open(filename) # opens existing SQLite3 database if it exists. Creates a new one if it does not 

d[key] = data   # store data at key (overwrites old data if
                # using an existing key)
data = d[key]   # retrieve a COPY of data at key (raise KeyError if no
                # such key)
del d[key]      # delete data stored at key (raises KeyError
                # if no such key)
flag = d.has_key(key)   # true if the key exists
klist = d.keys() # a list of all existing keys

d.close() #commits changes to Sqlite3 shelve store

```


* data, like in dbm, or BerkeleyDB-based storage libraries, is pickled with cpickle, but pickles with HIGHEST_PROTOCOL. 

contains a script called shelve-tool, which is both a useful utility and provides an example for how sqlite-shelve can be used like the shelve module
