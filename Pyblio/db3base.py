# This file is part of pybliographer
# 
# Copyright (C) 2002, Peter Schulte-Stracke
# Email : peter.schulte-stracke@t-online.de
# 	   
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2 
# of the License, or (at your option) any later version.
#   
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# 
# $Id$

"""
      ##################################################
      #                                                #
      #           E X P E R I M E N T A L              #
      #                                                #
      ##################################################

"""
import array, cStringIO, cPickle, os.path, string, struct, sys, types
import warnings
from  bsddb3 import db, dbobj, dbshelve

from Pyblio import Storage


VERSION = 1


class DBase (Storage.DBaseI):

    """Concrete database class using BSD DB3 library.
  
    Comprises several files in a dictionary self.path, given here
    with the associated attribute names:
    pdb PDB01 main object storage
    cnf CNF01 configuration objects (dict.)
    adx AUT01 person index
    tdx TIT01 title index
    rdx REF01 various references ... 
    
    
    newid (): rid_t       return the rid (number) of new entry
    store (rid, item)     store the item's data
    load (rid, into)      load the data for record rid ...
    remove (rid)          remove record (perhaps flag only)

    connectx (index)     returns an index storage object 
    
    
    """
    def __init__ (self, path=None, new_item=None):
        self.path = path
        self._idx = {}
        Storage.DBaseI.__init__(self, path, "DB3")

        if path:
            self.open (path)
        if new_item:
            self.new_item = new_item
        else:
            from Pyblio import Base
            self.new_item = Base.Entry2
            
            
    def open (self, path, purge=0):
        self.path = path
        if purge:
            self.purge_database()
        print 'DB3OPEN: path=%s contains %s' %(path, os.listdir(path))
        
        self._pdb = self.db3open('PDB01', db.DB_BTREE)
        self._adb = self.db3open('AUT01', db.DB_BTREE)
        self._kdb = self.db3open('KEY01', db.DB_BTREE)
        self._ndb = self.db3open('NUM01', db.DB_BTREE)
        self._rdb = self.db3open('REF01', db.DB_BTREE)
        self._tdb = self.db3open('TIT01', db.DB_BTREE)
        self._cnf = self.db3open('CNF01', db.DB_HASH)
        self.sysid = Counter(self._cnf, 'SYS', 1)
        self.tmpid = Counter (self._cnf, 'TMP', 999000000)
        self.syscnt = Counter(self._cnf, 'SZS', 0)
        self.tmpcnt = Counter(self._cnf, 'SZT', 0)
        return
    
    def iterator (self):
        return CursorSet(parent=self, file=self._pdb)

    def get_index (self, name):
        if self._idx.has_key(name):
            return self._idx[name]
        else:
            return self.mk_index(name)
        
    def close (self):
        self._pdb.close()
        self._adb.close()
        self._kdb.close()
        self._ndb.close()
        self._rdb.close()
        self._tdb.close()
        self._cnf.close()
        print 'ALL CLOSED'
        
    def purge_data_base(self):

        if os.path.isdir(self.path):
            for i in os.listdir(self.path):
                print i, '*del*', os.path.join(self.path,i)
                os.remove(os.path.join(self.path,i))
        else:
            os.mkdir(self.filepath)

    def check_database(self):
        if os.path.isdir(self.path):
            if 'CNF01' in os.listdir(self.path):
                return 1


    def connectx (self, index):

        """Return an object that can be used to store index data.
        This is necessary, because the index update code should
        not know about the implementation of the index (which depends
        on the concrete db, anyway).

        XXX What is exactly returned ?
        """

        assoc = {
            'author': [None, self._adb, {} ],
            'title': [None, self._tdb, {}  ],
            'issn': [None, self._ndb, {
                'title': 'International Standard Serial Number',
                'subid': 22}],
            'isbn': [None, self._ndb, {
                'title': 'International Standard Book Number',
                'subid': 20}],
            'btxkey': [None, self._ndb, {'subid': '#'}],
            'citedref': [None, self._kdb, {'subid': '@'} ],
            }

        return assoc[index]

    def mk_index (self, name):
        c = self.connectx (name)
        Klasse = c[0] or Index
        idx = Klasse (self, c[1], name, **c[2])
        return idx 

    def newid (self, temp=0):
        
        if temp:
            return self.tmpid.next()
        else:
            return self.sysid.next()

    def newitem (self):
        return self.new_item()
    
    def store (self, rid, item):
        """Store the item with key rid in  the database.
        This  implementation uses cPickle to do so.
        
        """
        dico = {}
        for i in item.dict.keys():
            dico[i] = str(item.dict[i])
            #assert  i != 'date' or type(dico[i]) != type('')
                
        key = self.mkkey(rid)
        data = ['B\0\0\0\0\0\0\0\0\0', str(item.key.key),
                str(item.type.name), dico]#item.dict]
        self._pdb[key] = cPickle.dumps(data)

        return

    def mkkey (self, rid) :
        return struct.pack ('L', rid)

    def get (self, rid, new_item=None):

        return self.load(rid, self.read(rid)) 
    
    def read (self, rid):
        key = self.mkkey(rid)
        data = self._pdb[key]
        #print data [0:30]
        return data
    
    def load (self, rid, data, new_item=None):  

        if type(data) != type(''):
            return data
        if new_item:
            item = new_item()
        else:
            item = self.newitem()
        item._id = rid
        a, b, c, d = cPickle.loads(data)

        item._attr = a
        if a[0] != 'B':
            print 'wrong record type for the moment: %s' %(data[0])
        
        item.set_bibtex (b, c)
        item.dict = d
        return item
    
    def remove (self, rid):      ## abstract ##
        key = self.mkkey(rid)
        self._pdb.delete(key)
        return


    def db3open (self, filename, filetype, mode=0666,
                 flags=0, dbenv=None, dbtype=db.DB):
        name = os.path.join(self.path, filename)
        #print '**', filename, '**', self.path, '**', name
        dbfile = dbtype(dbenv)
        dbfile.open(name, filetype, mode=mode,
                    flags=flags | db.DB_CREATE)
        return dbfile



#             Index
#--------------------------------------------------


class Index (Storage.DBIndexI) :
    """A standard (secondary) index implementation for db3"""

    dbmode = db.DB_BTREE

    def __init__ (self, base, db, name, title='', subid=None,
                  modify=None, *args, **argh):
        self.db = db
        self.subid = subid
        if modify == 1:
            self.modify = self.mkkey
        else:
            self.modify = modify
        Storage.DBIndexI.__init__(
            self, base, name, title, *args, **argh)
        
        return

    def mkkey (self, value) :
        """Use this function to modify the key (e.g. by adding
        subclass ids (if this is not already done)."""
        return value

    def put (self, db_id, *keys):
        
        #assert type (db_id) == type(1L)

        if type (keys) == types.StringType:
            keys = [keys]
        ret = None

        for k in map (self.modify, keys):

            numbers = self.get(k)
            if db_id in numbers:
                pass
            else:
                #recheck!!!!
                for i in numbers:
                    if i == db_id:
                        print "ERROR: %d in $s => %d, but $d found" %(
                            db_id, numbers, (db_id in numbers), i) 
                        break
                else: #### not found
                    numbers.append(db_id)
                    numbers.sort()
                    ret = self.db.put(k, self.pack(numbers))
                    if ret:
                        print "WARNING: return code from self.db.put is %s"%(
                            `ret`)
            print numbers
        return


    def get(self, key, *args, **kw):
        # We do it with *args and **kw so if the default value wasn't
        # given nothing is passed to the extension module.  That way
        # an exception can be raised if set_get_returns_none is turned
        # off. [Taken verbatim from bsddb3 dist.- ptr]

        data_bin = apply(self.db.get,[key] +  list(args), kw)
        return self.unpack(data_bin)

    def remove (self, db_id, keys): 
        print 'Remove %s Index %d %s' %(self.title, db_id, keys)
        #assert type (db_id) == type(1L)

        if type (keys) == types.StringType:
            keys = [keys]
        ret = None

        for k in map (self.modify, keys):
            numbers = self.get(k)
            try:
                numbers.remove(db_id)
            except ValueError:
                warnings.warn("Attempt to remove inexisting id")
                print numbers
            
            ret = self.db.put(k, self.pack(numbers))
            if ret:
                print "WARNING: return code from self.db.put is %s"%(
                    `ret`)
            print numbers

    def has_key (self, key):
        return self.db.has_key (key)
        
    def pack (self, list):
        if list:
            data = array.array('L', list)
            return data
        
    
    def unpack(self, rec):
        """Unpack index lists. Return empty list if given None."""
        if rec :
            data = array.array('L', rec)
            return map (int, data.tolist())
        else:
            return []



#             Counter
#--------------------------------------------------


class Counter (Storage.CounterI):

    """An implementation of the Counter interface.
    
    """

    def __init__(self, db, name, initial=0):

        Storage.CounterI.__init__(self, db, name, initial)

    def _set (self, value):
        self._value = value
        self.db[self.key] = struct.pack('L', value)
        return value
    
    def _get (self, initial):
        if self.db.has_key(self.key):
            return struct.unpack('L', self.db[self.key])[0]
        else:
            return self._set(initial)
    

    

#             Cursor Set
#--------------------------------------------------


class CursorSet (Storage.DBCursorSet):

    def __init__ (self, parent=None, file=None):
        assert parent and file, 'Missing parameter'
        self._db = parent
        self.dbfile = file
        self.cursor = self.dbfile.cursor()
        
    def load_from_cursor(self, pair):
        if pair:
            db_id = struct.unpack('L', pair[0])[0]
            item = self._db.new_item()
            item._id = db_id
            item = self._db.load (item, db_id, pair[1])
            return item
        else:
           self.close()
           return None

    def first (self):
        p = self.cursor.first()
        return self.load_from_cursor(p)

    def next (self):
        p = self.cursor.next()
        return self.load_from_cursor(p)

    

    

