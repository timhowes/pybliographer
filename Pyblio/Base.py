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
import re, copy
import Pyblio.Help
from types import *

from Pyblio import Config, Open, Utils, Key, Iterator

import gettext
_ = gettext.gettext


''' This Module contains the base classes one might want to inherit
from in order to provide a new database format '''


class Entry:
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
	
	id = 'VirtualEntry'

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


	def text (self, key):
		''' return text with indication of convertion loss '''
		
		if self.is_personal (key):
			return self.dict [key], 0
		raise KeyError, _("entry has no key `%s'") % key

	
	def __getitem__ (self, key):
		''' return text representation of a field '''
		
		return self.text (key) [0]
	
	
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
			
		text = '%s [%s]\n' % (tp, self.key.key)
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
	

class DataBase:
	
	''' This class represents a full bibliographic database.  It
	also looks like a dictionnary, each key being an instance of
	class Key.

	A database *has* to be stored somewhere, under a given
	format. '''


	# a default database provides no editing facilities
	# (as it cannot be saved)
	properties = {}

	id      = 'VirtualDB'
	__keyid = 0
	
	
	def __init__ (self, url):
		''' Open the database referenced by the URL '''
		self.key = url
		
		self.dict = {}
		return

	def close (self):
		''' Indicate that the database should not be cached
		anymore. This does not influence the references to it
		that are still in use. '''

		Open.bibclose (self)
		return

	
	def has_property (self, prop):
		''' indicates if the database has a given property '''
		
		if self.properties.has_key (prop):
			return self.properties [prop]
		
		return 0
	
	def add (self, entry):
		''' Adds an (eventually) anonymous entry '''

		entry.key = Utils.generate_key (entry, self)

		self [entry.key] = entry
		return entry


	def keys (self):
		''' Returns a list of all the keys available for the database '''
		
		return self.dict.keys ()


	def has_key (self, key):
		''' Tests for a given key '''
		
		return self.dict.has_key (key)


	def __getitem__ (self, key):
		''' Returns the Entry object associated with the key '''
		
		return copy.copy (self.dict [key])


	def __setitem__ (self, key, value):
		''' Sets a key Entry '''
		
		self.dict [key] = value
		return


	def get_native (self, key):
		''' returns the entry in its native form '''
		
		raise RuntimeError, "method is deferred"


	def set_native (self, value):
		''' sets entries written in native form '''
		
		raise RuntimeError, "method is deferred"

	
	def __delitem__ (self, key):
		''' Removes an Entry from the database, by its key '''
		
		del self.dict [key]
		return

	
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
		''' Returns an iterator for that database '''
		return Iterator.Iterator (self)


	def update (self):
		''' Updates the Entries stored in the database '''
		
		raise IOError, _("no update method defined")
		return
