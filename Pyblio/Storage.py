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

"""Database oriented storage. This module is included by the concrete
database modules like bsd3base.

Class Recordset  A set of records that is the interface to import readers,
                 and databases, ...
Class Database   A database interface, connects to DBaseI objects 


  ... to be deleted:
Class DBaseI     interface to a concrete storage substrate
Class DBObjectT  the code common to all item types
Class DBSetI     common interface to item lists or cursors/iterators



      ##################################################
      #                                                #
      #           E X P E R I M E N T A L              #
      #                                                #
      ##################################################

"""
import array, atexit, cStringIO, os.path, re
import string, struct, sys, types, warnings, weakref


from Pyblio import Fields, Key, Iterator, Types, Utils


VERSION = 1

_primary_data_base = None
_temporary_data_base = None

def primary_db (): return _primary_data_base
def temporary_db (*args, **argh):
    global _temporary_data_base
    if primary_db():
        return primary_db()
    else:
        if not _temporary_data_base:
            _temporary_data_base = temporary_database (*args, **argh)
        return _temporary_data_base

#
#             Storage Object 
#--------------------------------------------------

class DBObjectT:

    """A storable object. base class for Entry. Not much yet.
    """
    DB_ID = None
    DB = None
    _p_changed = 0
    _flg = 0

    def id (self):
        return self.DB_ID


    
class RSIterator: pass

#
#     Database
#---------------------------------------------------
#
    
class Database (Iterator.RecordSet):

    """The real database version of a result set.

    Also implements the Base.DatabaseI interface!

    
    """
    
    id = 'RealDB'
    name = 'undefined database'

    def __init__ (self, base=None, path=None, name='',
                  mk_database=temporary_db,
                  mk_record=None, control=None,
                  temp=0, primary=1, *args, **argh):

        """A Database for Pybliographer.
        Parameters:
           control       a Coco.DataBase object           
           base          database (implemenataion of DBaseI)
                         if None, a temporary will be used XXX
           path          filename/directory or other name of db
           name          for display
           mk_database   returns a DBaseI subclass instance
           mk_record     returns an item instance (used to store
                         record into)

        Usually, a database is opened (depending on backend used, then
        given to this class, which delegates much of the actual work.

        Opening the databse in this class is a problem because the
        implemenation must be (potentially) selected.

        
        """
        
        print 'STORAGE.DATABASE  BASE=%s, PATH=%s' %(base, path)
        global primary_db
        
        # default ``backend''
        self.base = base or mk_database(path=path,
                                control=control, mk_record=mk_record,
                                *args, **argh)

        if primary and not temp and not primary_db :
            primary_db = self
            print '\n ***** Primary Data Base %s ****\n' %(
                self.name)

        self.path = path or self.base.path
        
        #if path:
        self.open(path)
        
        
        self.control = control 
        self.new_entry = mk_record or self.new_entry
        self.name = 'Pybliographer Database %s' %(self.base.name)
        self.key  = self.name

        self.cache = weakref.WeakValueDictionary()
        
    def open (self, path):

        #self.base.open(path)
        self.author_ix = self.base.mk_index('author')
        self.title_ix = self.base.mk_index('title')
        self.issn_ix = self.base.mk_index('issn')
        self.isbn_ix = self.base.mk_index('isbn')
        self.citedref_ix = self.base.mk_index('citedref')
        self.btxkey_ix = self.base.mk_index('btxkey')

        print "OPEN DATABASE:%s opened " %(self.name)
        print_stats (self.base)
        print_stats (self.author_ix)
        print_stats (self.issn_ix)
        #print_stats (self.btxkey_ix)
        
        atexit.register(self.close)

        return 

    def close (self):
        if self.base:
            self.base.close()
        return
    
    def new_entry (self, type=None):
        import Base
        return Base.Entry2(type=type)

    def mk_item (self):
        return self.new_entry()


    #--------------------------------------------------
    #   Iterator interface

    def iterator (self, *args, **argh):

        return DBIterator (self)


    #--------------------------------------------------
    #   Database interface

    def add (self, item, temporary=0):
        """Add an item to the external database"""

        try:
            assert item.DB == None, 'Item already in database'
            assert item.DB_ID == None, 'Item already in database'
            #assert item.key != None, 'Item has no key'
        except AssertionError:
            warnings.warn(
                "Attempt to add existing record, use update_item",
                DeprecationWarning, 2)
            print item
        # last minute . . .    
        if not item.key:
            item.key = self.create_bibtex_key (
                item)#, self.btxkey_ix, self.name)

        if temporary:
            db_id = self.base.tmpid.next()
            self.base.tmpcnt.up()
        else:
            db_id = self.base.sysid.next()
            self.base.syscnt.up()

        # hook for subclassing
        checked_item = self.check_in (item)

        if self.base and checked_item:
            self.index_set = self.do_index(checked_item)
            self.base.store (db_id, checked_item)
            self.update_index(db_id, self.index_set)
            #self.add_x (db_id, checked_item)
            self.add_c (db_id, checked_item)
        self.cache_add(item)  
	return item

    def update_item(self, item, old=None):
        db_id = item.DB_ID
        if old == None:
            old = self.fetch(db_id)
        old_index = self.do_index(old)
        new_index = self.do_index(item)
        self.update_index (db_id, new_index, old_index)
        self.base.store(db_id, item)
        self.cache[db_id] = item
        del old
        return item

    def update_index (self, db_id, new, old=[]):

        remove = []
        for i in old:
            try:
                new.remove(i)
            except ValueError:
                remove.append(i)
        for i in remove:
            index, keys = i[0], i[1:]
            index.remove(db_id, *keys)
        for i in new:
            index, keys = i[0], i[1:]
            index.put(db_id, *keys)
        return


    def delete (self, item, purge=0):
        if isinstance(item, DBObjectT):
            db_id = item.DB_ID
        else:
            db_id = item
            item = self.base.get (db_id)
        if not item : ## flagged for deletion?
            print 'attempt to delete non-item'
            return
        for i in item.index_set():
            o, r = i[0], i[1:]
            o.delete(db_id, *r)
            
        if purge:
            self.base.delete(db_id)
        else:
            pass
        pass

    def update (self, sorting = None):
	''' Not applicable'''
        warnings.warn("ambigous call to update", UserWarning, 2)
        return


    def __setitem__ (self, key, value):
	''' Sets a key Entry '''
        k = key.key
        value.key = key
        warnings.warn("Setitem called for %s" %(value),
                      DeprecationWarning, 2)
        self.add (value)
        
    def fetch(self, db_id):
        data = self.base.get(db_id)
        item = self.base.load(db_id, data,   )
        self.cache_add(item)
        return item
    
    def get (self, db_id):
        if db_id:
            #print 'GET: db_id=%s, chache contains:%s' %(
            #    db_id, self.cache.get(db_id, '*NIX*'))
            return self.cache.get(db_id, self.fetch(db_id))

    def check_in (self, item):  ## hook ##
        return item

    def add_c (self, db_id, item): ## hook ##
       
        return

    def cache_add(self, item):

        try: item.DB_ID = item._id
        except AttributeError:
            print 'ITEM without _id: ', item
        db_id = item.DB_ID
        self.cache[db_id] = item

    def __len__ (self):
	''' Number of entries in the database '''
	return self.base.syscnt.get()
    
    #--------------------------------------------------
    #   Utilities

    def do_index (self, item):
        """
        Note (1) one possible change could be to store the method,
        not the class, faster and more flexible.
        (2) 
        """
        ind = []

                
        if item.dict.has_key('issn'):
            ind.append([self.issn_ix, str(item['issn'])])

        if item.dict.has_key('isbn'):
            ind.append([self.isbn_ix.put,  str(item['issn'])])

        if item.dict.has_key('title'):
            key =  normalise_string(str(item['title']))
            ind.append([self.title_ix] + key)

        if item.dict.has_key('author'):
            for aut in item['author']:
                autn = normalise_string('%s,%s\x01' %(aut.last, aut.first))
                ind.append([self.author_ix] +autn)
                
        # note: this is far too simple, needs more work
        # than could be done here  
        if item.dict.has_key('editor'):
            try:
                for aut in item['editor']:
                    autn = normalise_string('%s,%s\x01' %(aut.last, aut.first))
                    ind.append([self.author_ix] + autn)
            except: pass
        # XXX this is very ugly
        try:
            ind.append([self.btxkey_ix, item.key.key])
        except AttributeError:
            item.key = self.create_bibtex_key(item)

        if item.has_key('citedref'):
            t = str(item['citedref'])
            x = re.split("', '", t[2:-2])
            ind.append([self.citedref_ix] + x)

        return ind
    
    def add_x (self, db_id, item, db=None):
        
        """Updates the indices. --
        This is a generic routine. Which indices are to be
        updated is the responsibility of the item, and provided
        via a call to item.index_set()

        ad interim, we use the following:
        author, title, isbn, issn, bibtex key.
        """


##         indices = item.index_set()
##         for i in indices:
##             o, rest = i[0], i[1:]
##             o.put(item, *rest)
##         if not base: return

        return

    #--------------------------------------------------
    #   Utilities
    
    def create_bibtex_key(self, item):
        import Autoload, Config, Key
        if item.key is None:
            # call a key generator
            keytype   = Config.get ('base/keyformat').data
            return  Autoload.get_by_name (
                'key', keytype).data (item, self.btxkey_ix)
        else:
            prefix = item.key.key
            key = Key.Key ('DB', prefix)
            suffix = ord ('a')
            while self.btxkey_ix.has_key (key):
                key = Key.Key (self, prefix + '-' + chr (suffix))
                suffix = suffix + 1
            return key
    


    def make_key(self, item):
        key = struct.pack('L',item.id())
        print 'MY KEY:', key
        return key


    def has_key (self, key):
        """Wrapper.
        This is a problem.  In principle, we should not use this."""

        warnings.warn("Database.has_key -- old style",
                      DeprecationWarning, 2)
        # educated guess
        return self.btxkey_ix.has_key(key.key)
        


#--------------------------------------------------
#     Concrete Database Interface


class DBaseI:

    """Interface to concrete database classes, like SQLbase or,
    perhaps, XMLbase.
    
    newid (): db_id_t       return the db_id (number) of new entry
    store (db_id, item)     store the item's data
    load (db_id, into)      load the data for record db_id ...
    remove (db_id)          remove record (perhaps flag only)

    connectx (index)     returns an index storage object 
    
XXXXXXXXX much is missing -- rework needed    
    """
    
    def __init__ (self, name, dbtype):
        self.name = name
        self.type = dbtype
    
    def open (self, path, *args, **argh):      ## abstract ##
        """Open the database for a given path. Returns a Recordset."""
        raise NotImplementedError
    
    def get_recordset (self):
        return self.recordset

    def set_recordset (self, recordset):
        self.recordset = recordset
        
    def close (self, path):     ## abstract ##
        raise NotImplementedError

    def iterator (self, *args, **argh):
        return self.recordset.iterator()
    
    def newid (self):           ## abstract ##
        raise NotImplementedError
    def store (self, db_id, item): ## abstract ##
        raise NotImplementedError
    def read  (self, db_id) :      ## abstract ##
        raise NotImplementedError
    def load  (self, db_id, into): ## abstract ##
        raise NotImplementedError
    def remove (self, db_id):      ## abstract ##
        raise NotImplementedError
    def nothing (self): return 1
    def connect_x (self, index):
        """Returns an object that can be used to store index data.
        This is necessary, because the index update code should
        not know about the implementation of the index (which depends
        on the concrete db, anyway).

        XXX What is exactly returned ?
        """
        raise NotImplementedError
        
class DBIndexI:

    """An index."""

    def __init__ (self, base, name, title='', *args, **argh):
        self.base = base
        self.name = name
        self.title = title or name
        self.connect (base, name , *args, **argh)

        # 
        self.size = 100
        return

    def connect (self, base, name , *args, **argh):
        r = base.connectx (name,  *args, **argh)
        print '*connecting:*', `base`, name, r
        return

    def __str__(self):
        return self.title

    def __len__ (self):
        ## number of records: stat()['ndata'] (nkeys ?)
        return self.size
    
    #--------------------------------------------------
    #   user interface

# Needs work XXX
    def iterator (self):
        return iter(self)

    def __iter__ (self):
        return #IndexIterator(self)


# MUST GO AWAY XXX

    def iter (self, first=None, last=None, mask=None, reverse=0):
        self.reverse = reverse  ### NYI
        self.scanmask = mask
        self.cursor = self.db.cursor()
        
        return self

    def first (self, first=None):
        
        if first:
            rec = self.cursor.set(first)
        else:
            rec = self.cursor.first()
        while rec:
            if self.check_mask(rec):
                return rec[0], self.unpack(rec[1])
            else:
                rec = self.cursor.next()
        return rec[0], self.unpack(rec[1])

    def next (self, last=None):
        rec = self.cursor.next()
        while rec:
            if not rec or (last and rec[0] > last):
                self.cursor.close()
                return None
            if self.check_mask(rec):
                return rec[0], self.unpack(rec[1])
            else:
                rec = self.cursor.next()

    def check_mask(self, rec):
        return 1

    def close(self):
        if self.cursor:
            self.cursor.close()

    #--------------------------------------------------
    #

    def add (self, db_id, keys, **argh):
        self.put (db_id, *keys)

    def get (self, db_id):
        raise NotImplementedError

    def remove (self, db_id, keys):
        pass

    ## XXX
    def putx (self, db_id, item):
        #print db_id, item 
        data = self.extract(item)
        self.put (db_id, data)
        return
    
    def put (self, db_id, *keys):
        raise NotImplementedError
   
    def extract (self, item):
        return ['**N Y I**']
    
#
#       DBSet -- sets of records     
#----------------------------------------------------------------------
#

class DBSetI :
    """This class generalises sets and iterators of Records.

    It can be used as an Iterator with first() and next()
    and also __iter__() methods, as required.
    In addition it has a close() method to allow its use with cursors.

    """
    typ = '' # undefined

    def __init__ (self, db=None):
        assert db, "DBSetI needs a db= parameter"
        self._db = db
    
    def __iter__ (self):
        return self

    def __del__ (self):
        self.close()

    def close(self): pass

    def add_item(self, item):
        self._db.add(item)

    def first(self):
        return self.next()

    def next (self): pass

    def first_id(self):
        return self.next_id()

    def next_id (self): pass

    def add_set (self, set) :pass



class DBIndexSet (DBSetI):

    """DBSet for use with indexes. Holds a list of IDs."""

    def __init__(self, db=None, list=None):

        DBSetI.__init__(self, db=db)
        self._items = list  # caller to copy it, if nec.
        self._position = 0
        
    def __len__ (self): return len(self._items)

##     def add_set (self, set):
##         """Add an DBSet"""

        
    def next (self):
        if self._position < len (self._items):
            return self._dbase.get(db, self.next_id())
        else:
            return None
        
    def next_id(self):
        item_id = self._items[self._position]
        self._position += 1
        return item_id
        

class DBCursorSet (DBSetI):
    """DBSet for use with a cursor, represented by a cursor"""

    def __init__ (self, cursor):
        self.cursor = cursor

    def next (self):
        return self.cursor.next()
        
 
    def first(self):
        return self.cursor.next()
    


class DBListSet (DBSetI):
    """DBSet for use with temporary db and input sources.
    Keeps the records in a list -- allows adding them.

    """

    def __init__(self, db=None, list=[]):
        
        self._db = db
        self._items = list 
        self._position = 0
        
    

#----------------------------------------------------------------------

class temporary_database (DBaseI):
    
    """In core implementation of database. For compatibility (v1) only."""

    def __init__ (self, path=None, opener=None, name='', *args, **argh):
##         import traceback
##         traceback.print_stack()
##         print "ARGS: path=%s, opener=%s, name=%s, %s, %s" %(
##             path, opener, name, args, argh)
        self.name = name or path
        self.path = path
        self.type = 'In Core'
        self.data = {}

        print 'Temporary path=%s, ***' %(path)
        self._config = {}
        self.syscnt = CounterI (self._config, 'syscnt', len(self.data))

        
    def open (self, path):
        self.path = path
        #self.opener(self.path)

    def iterator (self):
        """Return a DBSet containing the list of items."""
        set = DBListSet (db=self, list = range(1, len (self.data)))
        #rs =   Recordset (list)
                        
        return set
        
    def close (self, path):
        raise NotImplementedError
    def newid (self):      
        raise NotImplementedError
    def store (self, db_id, item):
        self.data[db_id] = item

    def get (self, db_id) :
        return seld.data[db_id]

    def put (self, db_id, item):
        self.data[db_id] = item
    
    def read  (self, db_id) :     
        raise NotImplementedError
    def load  (self, db_id, into):
        raise NotImplementedError
    def remove (self, db_id):     
        raise NotImplementedError

    def connectx (self, index):
        """Return an object that can be used to store index data.
        This is necessary, because the index update code should
        not know about the implementation of the index (which depends
        on the concrete db, anyway).

        XXX What is exactly returned ?
        """
        raise NotImplementedError
        


#             Counter
#--------------------------------------------------

class ConfigT :
    """ a configuration object, associates a database and key"""
    def __init__ (self, db, key, initial=None):
        self.db = db
        self.key = key
        self._value = self._get(initial)

    def _set (self, value):
        self._value = value
        self.db[self.key] = value
        return value
    
    def _get (self, initial):
        if self.db.has_key(self.key):
            return self.db[self.key]
        else:
            return self._set(initial)
        
            
        
class CounterI (ConfigT):
    def __init__ (self, db, name, initial=0, ):
        self.name = name
        ConfigT.__init__(self, db, 'Z%s' % (name), initial)
        print self._value
        
    def next(self):
        #print self._value
        return self._set(self._value+1)

    def up(self, inc=1):
        return self._set(self._value+inc)

    def down(self, inc=1):
        return self._set(self._value-inc)

    def get (self):
        #print self._value, `self._value`
        return int(self._value)

    def unget (self, value):
        if self._value == value:
            self._set(value - 1)

def normalise_string(string):
    """Normalise a string to use it as a key.
    TODO: reduce three consecutive identical consonants. """
  
    ignore, whitespace, start, umlaut = 0, 0, 1, 0
    special = {'ä': ('ae','a'), 'Ä': ('ae','a'),
               'ö': ('oe','o'), 'Ö': ('oe','o'),
               'ü': ('ue','u'), 'Ü': ('ue','u'),}
    out1, out2 = [], []

    for c in str(string):
        if   c == '\x88': ignore = 1
        elif c == '\x89': ignore = 0
        elif ignore or c == '-' : pass
        elif c in ' \t.-;:!()?§$%&=/':
            if not start: whitespace = 1
        else:
            if whitespace: 
                out1.append(' ')
                out2.append(' ')
                whitespace = 0
            start = 0
            if c in 'ÄÖÜäöü':
                umlaut = 1
                out1.append(special[c][0])
                out2.append(special[c][1])
                continue
            elif c == 'ß':
                out1.append('ss')
                out2.append('ss')
                continue
            out1.append(c)
            out2.append(c)
    result1 = ''.join(out1).lower()
    if umlaut:
        result2 = ''.join(out2).lower()
        return [result1, result2]
    return [result1]

def unsinn():pass


##################################################
    
class DBIterator(Iterator.Iterator):
    _typ = 'db'

    sorting = 1
    
    def first_id (self):
        self.setup()
        
        self.cursor = self.rs.author_ix.iter()
        print self.cursor
        
        if self.sorting == 0:
            self.cursor = self.rs.base.cursor()
        elif self.sorting == 1:
            self.cursor = self.rs.author_ix.iter()
        else:
            self.cursor = self.rs.btxkey_ix.iter()
        #print self.cursor
        self.current = self.cursor.first()
        #print self.current
        self.list = self.current[1]
        self.position = 0
        self.size = len(self.cursor)
        return self.next_id()

    def next_id (self):
        if self.position != None:
            # try to survive an empty list
            while self.position >= len(self.list):
                self.current = self.cursor.next()
                print 'CURSOR NEXT:', self.current
                if not self.current: return
                self.list = self.current[1]
                self.position = 0
            if self.position < len(self.list):
                item_id = self.list[self.position]
            else: return
            self.position += 1
            return item_id
        else:
            return self.first_id()


class DBaseIterator (Iterator.Iterator):
    """Iterator that runs over a cursor."""
    pass

def print_stats (db):

    print 'Statistics for database: %s' %(db.name)
    print 60 * '-', '\n'

    if isinstance (db, DBaseI):
        print db._pdb.stat()
        print db._pdb.key_range (struct.pack('L', 1000000))
    elif isinstance (db, DBIndexI):
        print db.db.stat()
        if db.subid:
            print db.subid
            print db.db.key_range (chr(db.subid))
            print db.db.key_range (chr(db.subid + 1))
        else:
            print db.db.key_range ('Z')
    print db
    
