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

Class DBaseI     interface to a concrete implementation
Class DBObjectT  the code common to all item types

Class Database casts a database as an Folder/Iterator

      ##################################################
      #                                                #
      #           E X P E R I M E N T A L              #
      #                                                #
      ##################################################

"""
import array, cStringIO, os.path, re, string, struct, sys, types


from Pyblio import Attributes, Base, Dedup, Fields, Key, Iterator, Types, Utils


VERSION = 1


class DBaseI:

    """Interface to concrete database classes, like SQLbase or,
    perhaps, XMLbase.
    
    newid (): rid_t       return the rid (number) of new entry
    store (rid, item)     store the item's data
    load (rid, into)      load the data for record rid ...
    remove (rid)          remove record (perhaps flag only)

    connectx (index)     returns an index storage object 
    
    
    """
    
    def __init__ (self, name, dbtype):
        self.name = name
        self.type = dbtype

    def open (self, path):      ## abstract ##
        raise NotImplementedError
    def close (self, path):     ## abstract ##
        raise NotImplementedError
    def newid (self):           ## abstract ##
        raise NotImplementedError
    def store (self, rid, item): ## abstract ##
        raise NotImplementedError
    def read  (self, rid) :      ## abstract ##
        raise NotImplementedError
    def load  (self, rid, into): ## abstract ##
        raise NotImplementedError
    def remove (self, rid):      ## abstract ##
        raise NotImplementedError

    def connectx (self, index):
        """Return an object that can be used to store index data.
        This is necessary, because the index update code should
        not know about the implementation of the index (which depends
        on the concrete db, anyway).

        XXX What is exactly returned ?
        """
        raise NotImplementedError
        

class DBObjectT:

    """A storable object.
    """
    
    def __init__(self, rid=None, db=None, creator=None):
        db = db or current_database()
        if rid:
            self.load(creator, db, rid) 
        else:
            self.create(creator)


class DBIndexI:

    """An index."""

    def __init__ (self, base, name, title='', *args, **argh):
        self.base = base
        self.name = name
        self.title = title or name
        self.connect (base, name , *args, **argh)
        return

    def connect (self, base, name , *args, **argh):
        r = base.connectx (name,  *args, **argh)
        print '*connecting:*', `base`, name, r
        return

    def __str__(self):
        return self.title

#--------------------------------------------------
#   user interface

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
    
    def putx (self, rid, item):
        #print rid, item 
        data = self.extract(item)
        self.put (rid, data)
        return
    
    def put (self, rid, *keys): pass


    def get (self, rid):
        return []

   
    def extract (self, item):
        return ['**N Y I**']
    
class Database(Base.DatabaseI, Iterator.ResultSet) :

    """The real database version of a result set.

    Also implements the Base.DatabaseI interface!
    """
    
    id = 'RealDB'
    
    def __init__ (self, base, path=None, control=None, entry=None):

        self.base = base
        if path:
            self.base.open(path)
        
        self.sysID = self.base.sysid
        self.control = control
        self.new_entry = entry or self.new_entry
        self.key = 'Pybliographer Database %s' %(self.base.path)

        self.author_ix = self.base.mk_index('author')
        self.title_ix = self.base.mk_index('title')
        self.issn_ix = self.base.mk_index('issn')
        self.isbn_ix = self.base.mk_index('isbn')
        self.citedref_ix = self.base.mk_index('citedref')
        self.btxkey_ix = self.base.mk_index('btxkey')


    def open (self, path):
        return self.base.open(path)

    def close (self):
        if self.base:
            self.base.close()
        return
    
##     def has_property (self, prop):
## 	''' indicates if the database has a given property '''

##         if self.control:
##             return self.control.properties.get(prop,1)
##         else: return 1

    def new_entry (self):
        import Base
        return Base.Entry2()

    def mk_item (self):
        return self.new_entry()

#--------------------------------------------------
#   Iterator interface

    def first(self):
        self.set_order (self.ordering or 0)
        self.set_position (self.position or 0)
        self.xc = self.base._pdb.cursor()
        pair = self.xc.first()
        if not pair:
            self.xc.close()
        return self.read_data(pair)


    def next(self):
        pair =   self.xc.next()
        if not pair:
            self.xc.close()
        return self.read_data(pair)

    def read_data (self, pair):

        if pair:
            rid = struct.unpack('L', pair[0])[0]
            #print 'Record #', rid
            item = self.mk_item()
            item._id = rid
            item = self.base.load (item, rid, pair[1])
            return item
        else:
            return None

    def iterator (self):
	''' Returns an iterator for that database '''
	return self

#--------------------------------------------------
#   DatabaseI interface

    def add (self, item, temp=0):
        """Add an item to the external database"""

        #print '*Add:*', item,
        assert item._id == None, 'Item already in database'
        assert item.key != None, 'Item has no key'
        if temp:
            rid = self.base.tmpid.next()
            self.base.tmpcnt.up()
        else:
            rid = self.base.sysid.next()
            self.base.syscnt.up()
	item._id = rid
        # duplication checks ?
        checked_item = self.check_in (item)

        if self.base and checked_item:
            self.base.store (rid, checked_item)
            self.add_x (rid, checked_item)
            self.add_c (rid, checked_item)
	return item

    def get (self, rid):
        print '*GET*', rid
        data = self.base.get(rid)
        item = self.base.load(rid, data,   )
        return item

    def delete (self, rid, purge=0):
        if isinstance(rid, DBObject):
            rid = rid._id
        item = self.base.load (rid)
        if not item : ## flagged for deletion?
            print 'attempt to delete non-item'
            return
        for i in item.index_set():
            o, r = i[0], i[1:]
            o.delete(rid, *r)
            
        if purge:
            self.base.delete(rid)
        else:
            pass
        pass

    def update_item(self, item, old=None):
        rid = item._id
        if old == None:
            old = self.load(rid)
        old_x = old.index_set()
        new_x = item.index_set()
        for i in old_x:

            if i in new_x:
                new_x.remove(i)
            else:
                o, r = i[0], i[1:]
                o.put(rid, *r)
        del old
        return

    def update (self, sorting = None):
	''' Not applicable'''
        return

    def check_in (self, item):  ## hook ##
        return item

    def add_c (self, rid, item): ## hook ##
        
        return

    def __len__ (self):
	''' Number of entries in the database '''
	return self.base.syscnt.get()
    
#--------------------------------------------------
#   Utilities

    def add_x (self, rid, item, db=None):
        
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
        
        if item.dict.has_key('issn'):
            self.issn_ix.put(rid, str(item['issn']))

        if item.dict.has_key('isbn'):
            self.isbn_ix.put(rid, str(item['issn']))

        if item.dict.has_key('title'):
            key =  normalise_string(str(item['title']))
            self.title_ix.put(rid, *key)

        if item.dict.has_key('author'):
            print '*Authors:', item['author']
            for aut in item['author']:
                autn = normalise_string('%s,%s\x01' %(aut.last, aut.first))
                self.author_ix.put(rid, *autn)
                
        if item.dict.has_key('editor'):
            try:
                for aut in item['editor']:
                    autn = normalise_string('%s,%s\x01' %(aut.last, aut.first))
                    self.author_ix.put(rid, sub=010, *autn)
            except: pass

        if item.key:
            self.btxkey_ix.put(rid, item.key.key)

        if item.has_key('citedref'):
            t = str(item['citedref'])
            x = re.split("', '", t[2:-2])
            self.citedref_ix.put(rid, *x)

        return



    def make_key(self, item):
        key = struct.pack('L',item.id())
        print 'MY KEY:', key
        return key


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

