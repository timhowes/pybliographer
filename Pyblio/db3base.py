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
        Storage.DBaseI.__init__(self, path, "DB3")

        if path:
            self.open (path)
        if new_item:
            self.new_item = new_item
        else:
            from Pyblio import Base
            self.new_item = Base.Entry2
            
    def open (self, path):
        self.path = path
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
    
    def mk_index (self, name):
        c = self.connectx (name)
       
        idx = Index (self, c[0], name, **c[1])
        return idx 

    def close (self):
        self._pdb.close()
        self._adb.close()
        self._kdb.close()
        self._ndb.close()
        self._rdb.close()
        self._tdb.close()
        self._cnf.close()
       
    def connectx (self, index):

        """Return an object that can be used to store index data.
        This is necessary, because the index update code should
        not know about the implementation of the index (which depends
        on the concrete db, anyway).

        XXX What is exactly returned ?
        """

        assoc = {
            'author': [self._adb, {} ],
            'title': [self._tdb, {}  ],
            'issn': [self._ndb, {
                'title': 'International Standard Serial Number',
                'subid': 22}],
            'isbn': [self._ndb, {
                'title': 'International Standard Book Number',
                'subid': 20}],
            'btxkey': [self._ndb, {'subid': '#'}],
            'citedref': [self._kdb, {'subid': '@'} ],
            }

        return assoc[index]

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
        key = self.mkkey(rid)
        data = ['B\0\0\0\0\0\0\0\0\0', str(item.key.key),
                str(item.type.name), item.dict]
        self._pdb[key] = cPickle.dumps(data)

        return

    def mkkey (self, rid) :
        return struct.pack ('L', rid)

    def get (self, rid, new_item=None):
        print self.read(rid)
        return self.load(rid, self.read(rid)) 
    
    def read (self, rid):
        key = self.mkkey(rid)
        return self._pdb[key]
    
    def load (self, item, rid, data, new_item=None):  

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

    def put (self, rid, *keys):
        
        print 'PUT %s INDEX %d %s' %(self.title, rid, keys)
        #assert type (rid) == type(1L)

        if type (keys) == types.StringType:
            keys = [keys]
        ret = None

        for k in map (self.modify, keys):
            print 'try add key:', k,
            numbers = self.get(k)
            if rid in numbers:
                pass
            else:
                #recheck!!!!
                for i in numbers:
                    if i == rid:
                        print "ERROR: %d in $s => %d, but $d found" %(
                            rid, numbers, (rid in numbers), i) 
                        break
                else: #### not found
                    numbers.append(rid)
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
        
    def pack (self, list):
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
        print '*Counter set:*', value, self.db[self.key]
        return value
    
    def _get (self, initial):
        if self.db.has_key(self.key):
            return struct.unpack('L', self.db[self.key])[0]
        else:
            return self._set(initial)
    

    

        

            

