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

from string import *
import copy, os, re, struct
import Pyblio.Help
from types import *

from Pyblio import Autoload, Coco, Config, Fields,\
     Iterator, Key, Numerus,  Open, Selection, Storage, Types, Utils

import gettext
_ = gettext.gettext


''' This Module contains the base classes one might want to inherit
from in order to provide a new database format '''


class Entry(Storage.DBObjectT):
    '''
    A database entry. It behaves like a dictionnary, which
    returns an instance of Description for each key. For example,
    entry [\'author\'] is expected to return a Types.AuthorGroup
    instance.

    Each entry class must define an unique ID, which is used
    during conversions.

    The entry.key is an instance of Key, and has to be unique over
    the whole application.

    The entry.type is an instance of Types.EntryDescription. It
    links the field names with their type.
    '''

    id_x = 'VirtualEntry'

    def __init__ (self, key = None, type = None, dict = None):

	self.type = type
	self.dict = dict or {}
	self.key  = key
	return

    def keys (self):
	''' returns all the keys for this entry '''
	return self.dict.keys ()

    def has_key (self, key):
	if self.dict.has_key (key): return 1
	return 0


    def set_bibtex (self, key, typ):
        """Sets the bibtex attributes key and type.
        Used by database routines."""
        
        if type(type) == StringType:
            self.type = Types.get_entry(lower(typ))
        else:
            self.type = typ
            self.type = Types.get_entry(lower(typ))
        
        if type(key) ==  StringType:
            self.key = Key.Key('DB', key)
        else:
            self.key = key, 

    def field_and_loss (self, key):
	''' return field with indication of convertion loss '''
	return self.dict [key], 0

    def __getitem__ (self, key):
	''' return text representation of a field '''

	return self.field_and_loss (key) [0]

    def __setitem__ (self, name, value):
	self.dict [name] = value
	return
	
    def __delitem__ (self, name):
	del self.dict [name]
	return

    def __add__ (self, other):
	''' Merges two entries, key by key '''

	ret = Entry (self.key, self.type, {})

	# Prendre ses propres entrees
	for f in self.keys ():
	    ret [f] = self [f]

	# et ajouter celles qu'on n'a pas
	for f in other.keys ():
	    if not self.has_key (f):
		ret [f] = other [f]

	return ret

    def __repr__ (self):
	''' Internal representation '''

	return 'Entry (%s, %s, %s)' % (`self.key`, `self.type`, `self.dict`)


    def __str__ (self):
	''' Nice standard entry  '''

	tp = self.type.name
	fields = self.type.fields

        try:
            text = '%s [%s]\n' % (tp, self.key.key)
        except AttributeError:
            text = '%s [...]\n' % (tp)
	text = text + ('-' * 70) + '\n'

	dico = self.keys ()

	for f in fields:
	    name = f.name
	    lcname = lower (name)

	    if not self.has_key (lcname): continue

	    text = text + '  %-14s ' % name
	    text = text + Utils.format (str (self [lcname]),
					75, 17, 17) [17:]
	    text = text + '\n'

	    try:
		dico.remove (lcname)
	    except ValueError:
		raise ValueError, \
		      'multiple definitions of field `%s\' in `%s\'' \
		      % (name, tp)

	for f in dico:
	    text = text + '  %-14s ' % f
	    text = text + Utils.format (str (self [f]),
				  75, 17, 17) [17:]
	    text = text + '\n'

	return text


class Entry2 (Entry):

    """ad interim -- Entry with additions."""

    id_x = 'VirtualEntry2'

    def __init__ (self, key=None, type = None, dict = None,
                  *args, **argh):

        self.flags = [32, 0, 0, 0, 0]
        Entry.__init__(self, key=key, type=type, dict=dict,
                       *args, **argh)

    def get (self, name, default=''):
        return self.dict.get(name, default)

    def add_person (self, name=None, role=None, econtrol=None):
        self.add_simple('author', name)
        return
    
    def add_title (self, string, econtrol=None):
        self.add_simple_nr('title', string)
        return

    def add_simple (self, name, value, join=' '):
        if self.dict.has_key(name):
            self.dict[name] = Fields.Text(
                str(self.dict[name]) + join + value)
        else:
            self.dict[name] = Fields.Text(value)
        return
    
    def add_simple_nr (self, name, value):
        if self.dict.has_key(name):
            print 'WARNING: attempt to add %s to field %s = %s' % (
                value, name, self.dict[name])
        else:
            self.dict[name] = Fields.Text(value)
        return
    # deprecated:
    def add_journal (self, *args, **argh): pass


class DataBase (Iterator.RecordSet):

    """
    Changes:   Now interfaces to (temporary) database.  New code will
    use the interface that Storage provides directly.




    This class represents a full bibliographic database.  It
    also looks like a dictionnary, each key being an instance of
    class Key.

    Ad iterim we use this to interface to the in-core version of
    Storage.Database.

    We don't use the path on initialisation, opening a file is done
    outside  of this code.

    """
    id = 'VirtualDB'
    

    def __init__ (self, url):
        """ UNTRUE: Open the database referenced by the URL """

        print 'creating a DATABASE: url=%s' %(url)
        self.base = Storage.temporary_db()
        self.data = Storage.DBListSet(db=self.base)
        self.control = Coco.InputFile(
            title='Pyblio (Input): %s' %(url), file=url)
        Iterator.RecordSet.__init__(
            self, base=self.base, control=self.control,
            path=url, input=self.data, temporary=1)

        self.url = url
        self.key = self.url ## ad interim
        self.dict = {} ## ad interim
        self._ITEMS = []
        
        
	return

    # Old style interface
    #--------------------------------------------------
    
    def add (self, item):
	''' Adds an (eventually) anonymous entry
        '''

        # create BibTeX key:
        item.key = self.create_bibtex_key(item, self.dict,
                                          self.url)

        item.DB_ID = len(self._ITEMS)
        self._ITEMS.append(item)
        self.dict[item.key] = item.DB_ID

	return item

    def update_item (self, new, old=None):
        """ad interim, nothing specila to this class in fact"""
        db_id = item.DB_ID
        if old == None:
            old = self._ITEMS[db_id]
        # we have only one index
        del self.dict[old.key.key]
        new.key = self.create_bibtex_key(item, self.dict, self.url)
        self.dict[new.key.key] = new.DB_ID
        self._ITEMS[new.DB_ID] = new
        del old
        return item

    def delete (self, item, purge=0):
        if isinstance(item, DBObjectT):
            db_id = item.DB_ID
        else:
            db_id = item
            item = self._ITEMS[db_id]

        self.__delitem__(item.key.key)

    def new_entry (self, type):
        ''' Creates a new entry of the native type of the database '''
        return Entry (None, type)
    

    def keys (self):
	''' Returns a list of all the keys available for the database '''

	return self.dict.keys ()


    def has_key (self, key):
	''' Tests for a given key '''

	return self.dict.has_key (key)


    def would_have_key (self, key):
        ''' Test for a key that would be set on the database '''

        return self.has_key (Key.Key (self, key.key))

    
    def __getitem__ (self, key):
	''' Returns the Entry object associated with the key '''

	return self.dict [key]


    def __setitem__ (self, key, value):
	''' Sets a key Entry Old style interface'''
        print 'DATABASE SET ITEM:', key, value
        key.base  = self.key
        value.key = key
        if not value.DB_ID:
            self.add(value)
        else:
            self.dict [key] = value
	return


    def __delitem__ (self, key):
	''' Removes an Entry from the database, by its key '''
        del self._ITEMS[self.dict[key]]
	del self.dict [key]

    def __len__ (self):
	''' Number of entries in the database '''
	return len (self.keys ())

    def __str__ (self):
	''' Database representation '''

	return '<generic bibliographic database (' + `len (self)` + \
	       ' entries)>'


    def __repr__ (self):
	''' Database representation '''
	
	return 'DataBase (%s)' % `self.key`


    def iterator (self):
	""" Returns an iterator for that database """
        return EnumIterator(self)


    def update (self, sorting = None):
	''' Updates the Entries stored in the database '''
	#print 'UPDATE DATABASE', `self`
	if self.key.url [0] != 'file':
	    raise IOError, "can't update the remote database `%s'" % self.key

	name = self.key.url [2]

        # create a temporary file for the new version
        tmp = os.path.join (os.path.dirname (name),
                            '.#' + os.path.basename (name))
        
        tmpfile = open (tmp, 'w')

        iterator = Selection.Selection (sort = sorting).iterator (self.iterator ())
	Open.bibwrite (iterator, out = tmpfile, how = self.id)
        
	tmpfile.close ()
        
	# if we succeeded, backup file
	os.rename (name, name + '.bak')
	# ...and bring new version online
        os.rename (tmp, name)
        return

    # Utilities
    #--------------------------------------------------

class EnumIterator(Iterator.Iterator):

    _typ = 'enum'
        
    def first_id(self):

        self.filter = self.filter or self.rs.default_filter
        self.sorting = self.sorting or self.rs.default_sorting

        if self.filter:
            self._items = [item.DB_ID for item in self.rs._ITEMS
                           if self.filter.test(item)]
        else:
            self._items = range(len(self.rs._ITEMS))


        if self.sorting:
            pass
        else:
            pass
        self.items = self._items
        self.position = 0
        print 'ITEMS:', self.items
        return self.next_id()

    def first (self):
        item_id = self.first_id()
        
        print 'ITERATOR FIRST', self, item_id, self.rs
        if item_id != None:
            return self.rs._ITEMS [item_id]

    def next_id (self):
        position = self.position
        self.position += 1
        if position < len(self.items):
            print 'ITEM:', self.items[position]
            return self.items[position]

    def next (self):
        item_id = self.next_id()
        if item_id != None:
            return self.rs._ITEMS[item_id]


# for unit testing, the master file is tBase.py:

# Local Variables:
# py-master-file: "tBase.py"
# End:
