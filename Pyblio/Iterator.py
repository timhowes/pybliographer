# This file is part of pybliographer
# 
# Copyright (C) 1998,1999,2000 Frederic GOBRY
# Email : gobry@idiap.ch
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

"""This module contains the basic interfaces to handle sets
of records, namely iterators, which implement the Python iterator
protocol, and resultsets, which are the associated containers.

Classes:

    Iterator    an iterator class for records
    Resultset   a container class for records

    
"""

import copy

from Pyblio import Coco

class Iterator:
    """
      ##################################################
      #                                                #
      #           E X P E R I M E N T A L              #
      #                                                #
      ##################################################

    This class generalises sets and iterators of Records.

    An Interface.

    It can be used as an Iterator with first() and next()
    and also __iter__() methods, as required.
    In addition it has a close() method for use with cursors.

    
    The progress bar related stuff should disappear . . 

   """
    filter = None
    sorting = None
    position = None

    
    def __init__(self, recordset, *args, **argh):
        
        self.rs = recordset
        self.maxprogress = -1
        
    def close (self):  pass

    def size (self):
        return len(self.rs)
    
    def __iter__ (self):
        return self

    def iterator (self):
        ''' loop method, so that we can for example call a method by
        passing indifferently a database or a database iterator...
        '''
        return self

    # iterator interface

    def next (self):
        return self.rs.get(self.next_id())

    def next_id(self): pass

    def first (self):        
        return self.rs.get(self.first_id())

    def first_id (self): pass

    # set filter and sorting:
    
    def set_filter (self, filter):
        self.filter = filter

    def set_sorting (self, sorting):
        self.sorting = sorting

    def setup(self):
        self.filter = self.filter or self.rs.default_filter
        self.sorting = self.sorting or self.rs.default_sorting
        self.base = self.rs.base

    # deprecated:
    
    def set_maximum (self, amount):
        if amount > 0:
            self.maxprogress = amount
        print 'filesize %d' % amount
        
        return

    def set_progress (self, amount):
        #if self.maxprogress > 0 and amount > 0:pass
        print 'progress %d %%' % (amount* 100 / self.maxprogress)
        #self.Issue('set-progress', amount, self.maxprogress)
        return


    
class DBIterator (Iterator):
    ''' This class defines an old style  database iterator;
    iterates over the BibTeX keys.  DEPRECATED (but copied to )
    '''
    _Typ = 'oldit'
    
    def __init__ (self, database):
        self.keys     = database.keys ()
        self.database = database
        return

    def first (self):
        self.count = 0
        return self.next ()

    def next (self):
        try:
            entry = self.database [self.keys [self.count]]
        except IndexError:
            entry = None
        
        self.count = self.count + 1
        return entry


 
      ##################################################
      #                                                #
      #           E X P E R I M E N T A L              #
      #                                                #
      ##################################################

class RecordSet:

    """This class represents a set of items (of various kinds)
    either selected from a database or currently being entered
    or imported. Thus it is the result of Open, of Query, of
    data entry, etc.

    It gives the ability to specify  display style (?),
    position or similar preferences.

    Acts also as an interface between database and consumers/
    suppliers. 

    The standard recordset just acts as a set (enumeration) of records.

    Iteration: the iterator method reutrns an iterator for this recordset.

    A recordset has a database or is itself a database. 

    """
    _Typ  = 'r'
    default_filter = None
    default_sorting = None
    default_style = None
    default_position = None
    _size = 0
    key = 'an iterator' ## deprecated

    def __init__(self, base=None, control=None, input=None,
                 name= '', temporary = 0,
                 *args, **argh):

        self.temporary = temporary
        self.name = name 
        self.control = control or Coco.RecordSet()
        self.base = base 
        self._items = {} ## ?
        self.input  = input #??
        return

    def __len__ (self):
        return len(self.items)

    
    #--------------------------------------------------
    #   Input interface

    def add (self, record):
        """Add a record to the base, if necessary.
        This must go through the base add method, because in
        typical situations, both, the data base and the current
        result set are meant to be updated.

        Only NEW items (not ids) are possible inputs.

        Note that in a database implemantation, much must be added;
        here it suffices to delegate.

        """

        assert record.DB == None, 'ERROR: only new records can be added'
        assert record.DB_ID == None, 'ERROR: record not new'
        
        record = self.check_in(record)
        if record:
            record = self.base.add(record)
        if record:
            self.add_items([record.DB_ID])
        print 'RECORD SET ADD : ', record.key, record.DB_ID

        return record

    def move (self, record, set):
        """Move a record *from* another recordset rs into this one.
        Note that the order of arguments is uncommon:
            target.move(item, from)
        """
        self.copy(record, set)
        set.remove (record)

    def copy (self, record, set=None):
        """copy a record from set into this recordset."""

        if record.DB != self.base:
            record = copy.copy(record)
            record.DB = None
            record.DB_ID = None
            return self.add(record)
        else:
            self.add_items([record.DB_ID])
            return record

    #### the following is in need of some distinctions
    def remove (self, record):
        """Remove a record from this recordset"""
        del self._items[record.DB_ID]
        self.size -= 1
        
    def delete (self, db_id):
        del self._items[db_id]
        self.size -= 1

    def add_items(self, list):
        for i in list:
            self._items[i.DB_ID] = i
            self.size += 1
        
    def check_in (self, item):
        return item
    
    def check_out (self, item):
        return item

    ### old stuff
    def add_item(self, item):
        """Adds an item to the result set, including substrate
        db action, if there is any."""

        ### the question of IDs is not clear yet
        checked_item = self.check_in (item)
        if self.base and checked_item:
            self.add_c (checked_item, db=self.base)
            self.add_x (checked_item, db=self.base)
        return #some_id?

    def add_c (self, item, db=None):
        """Adds the item to the substrate collection/database.
        Subclass dependent."""
        raise NotImplementedError

    def add_x (self, item, db=None):
        
        """Updates the indices. --
        This is a generic routine. Which indices are to be
        updated is the responsibility of the item, and provided
        via a call to item.index_set()

        ad interim, we use the following:
        author, title, isbn, issn, bibtex key.
        """
        raise NotImplementedError

        
        
    ## DEPRECATED 

    def add_set(self, set):
        """Add a DB_Set to the base -- perhaps that should be
        an error sometimes ? XXXX
        """
        
        if self._root and set:
            self._root = self._root.add_set(set)
        elif set:
            self._root = set
        else:
            self._root = DBListSet(db=self._base)
        return self._root

 
    #--------------------------------------------------
    #   Iterator interface

    def __iter__ (self):
        return self.iterator()
    # DOES THIS WORK ?
    
    def iterator (self):
        return RSIterator(recordset=self)
    

    #--------------------------------------------------
    #   Defaults
    
    
    def set_filter(self, filter):
        """Set the filter of the Recordset."""
        self.default_filter = filter
        self.control['filter'] = filter
        return
    
    def set_sorting (self, sorting):
        """set the sorting order for the Recordset."""
        self.default_sorting = sorting
        self.control['sorting'] = sorting
        return

    def set_style (self, style):
        self.default_style = style
        self.control['style'] = style
        return

    def set_order (self, kind):
        """Selects the kind of ordering required. Typical values are:
        0  implicit,  
        1  author only,
        2  title only
        3  author/title style.
        """

        if self.ordering:
            self.ordering = kind
            self.redisplay()
        else:
            self.ordering = kind
        return

    def set_position(self, position):
        """Sets the starting position for the iterator.
        0 means the very  first record, acording to current ordering,
        -1 means the very last one."""
        
        self.default_position = position
        
    def set_limit (self, start, stop=None):
        if stop != None:
            self.low_limit = start
            self.high_limit = stop
        else:
            self.low_limit = None
            self.high_limit = stop
        return

    #--------------------------------------------------
    #   Utilities
    
    def create_bibtex_key(self, item, dict, url):
        from Pyblio import Autoload, Config, Key
        if item.key is None:
            # call a key generator
            keytype   = Config.get ('base/keyformat').data
            return  Autoload.get_by_name (
                'key', keytype).data (item, dict)
        else:
            prefix = item.key.key
            key = Key.Key (self, prefix)
            suffix = ord ('a')
            while dict.has_key (key):
                key = Key.Key (self, prefix + '-' + chr (suffix))
                suffix = suffix + 1
            return key
    

class ResultSet(RecordSet):
    pass 
