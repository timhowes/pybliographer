# This file is part of pybliographer
# 
# Copyright (C) 1998 Frederic GOBRY
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
import re
import Pyblio.Help
from types import *

from Pyblio import Config

''' This Module contains the base classes one might want to inherit
from in order to provide a new database format '''


		
def format (string, width, first, next):
	''' Format a string on a given width '''

	out = []
	current = first

	# if the entry does not fit the current width
	while len (string) > width - current:
		
		pos = width - current - 1

		# search a previous space
		while pos > 0 and string [pos] <> ' ':
			pos = pos - 1

		# if there is no space before...
		if pos == 0:
			pos = width - current
			taille = len (string)
			while pos < taille and string [pos] <> ' ':
				pos = pos + 1

		out.append (' ' * current + string [0:pos])
		string = string [pos+1:]
		current = next

	out.append (' ' * current + string)

	return rstrip (join (out, '\n'))


class Key:

	''' A special key that embeds both database and database
	key Such a key is expected to be completely unique among the
	whole program and should be the reliable information checked
	to see if two entries are the same.

	The .base field is the database name from which the actual
	entry can be recovered, whereas the .key field is the name in
	the database itself.  '''
	
	def __init__ (self, base, key):
		if type (key) is InstanceType:
			self.base = key.base
			self.key  = key.key
		else:
			self.key  = key
			if type (base) is StringType:
				self.base = base
			else:
				self.base = base.key
		return

	def __repr__ (self):
		return "Key (%s, %s)" % (`self.base`, `self.key`)
	
	def __str__ (self):
		if self.base:
			return str (self.base) + ' - ' + str (self.key)
		else:
			return str (self.key)
		
	def __cmp__ (self, other):
		try:
			r = cmp (self.base, other.base)
		except AttributeError:
			return 1
		
		if r: return r
		
		return cmp (self.key, other.key)

	def __hash__ (self):
		return hash (self.key + '\0' + self.base)


class Entry:
	'''
	A database entry. It behaves like a dictionnary, which
	returns an instance of Description for each key. For example,
	entry ['author'] is expected to return a Types.AuthorGroup
	instance.

	Each entry class must define an unique ID, which is used
	during conversions.

	The entry.name is the name of the entry inside its database,
	whereas the entry.key is an instance of Key, and has to be
	unique over the whole application.

	The entry.type is an instance of Types.EntryDescription. It
	links the field names with their type.
	'''
	
	id = 'VirtualEntry'

	def __init__ (self, key, type = None, dict = None):
		self.type = type
		self.__dict = dict or {}
		self.key    = key
		
		self.crossref = None
		return


	def keys (self):
		''' returns all the keys for this entry (counting
		those who belong to crossreferences) '''
		perso = self.__dict.keys ()
		if self.crossref:
			for k in self.crossref.keys ():
				if not self.is_personal (k):
					perso.append (k)

		return perso

			
	def personal_keys (self):
		''' Returns the keys that are actually defined by the entry,
		and not by its crossreferences '''
		return self.__dict.keys ()

	
	def is_personal (self, key):
		''' indicates if a given field is defined by the entry or
		one of its crossreferences '''
		if self.__dict.has_key (key):
			return 1
		return 0

	
	def has_key (self, key):
		if self.__dict.has_key (key): return 1
		
		if self.crossref:
			if self.crossref.has_key (key): return 1
			
		return 0


	def text (self, key):
		''' return text with indication of convertion loss '''
		
		if self.is_personal (key):
			return self.__dict [key], 0

		if self.crossref:
			if self.crossref.has_key (key):
				return self.crossref.text (key)
			
		raise KeyError, "entry has no key `%s'" % key

	
	def get_native (self, key):
		''' returns the field in its native form '''
		
		return self [key]


	def set_native (self, key, value):
		''' sets the field in its native form '''
		
		self [key] = value
		return
	
	def __getitem__ (self, key):
		''' return text representation of a field '''
		
		return self.text (key) [0]
	
	def foreach (self, function, argument = None):
		''' To provide compatibility with ref '''
		
		function (self, argument)
		return

	
	def __setitem__ (self, name, value):
		self.__dict [name] = value
		return

	
	def __delitem__ (self, name):
		del self.__dict [name]
		return

	
	def __add__ (self, other):
		''' Merges two entries, key by key '''

		ret = Entry (self.key, self.type, {})

		# Prendre ses propres entrees
		for f in self.personal_keys ():
			ret [f] = self [f]

		# et ajouter celles qu'on n'a pas
		for f in other.keys ():
			if not self.has_key (f):
				ret [f] = other [f]

		ret.crossref = self.crossref
		return ret


	def __repr__ (self):
		return "<entry `" + self.key.key + "'>"


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
			text = text + format (str (self [lcname]),
					      75, 17, 17) [17:]
			text = text + '\n'
			
			try:
				dico.remove (lcname)
			except ValueError:
				raise ValueError,\
				      "error: field `%s' appears more than once in " +\
				      "the definition of `%s'" % (name, tp)
			
		for f in dico:
			text = text + '  %-14s ' % f
			text = text + format (str (self [f]),
					      75, 17, 17) [17:]
			text = text + '\n'
		
		return text
	

SortByKey  = 0
SortByType = 1

class DataBase:
	'''
	This class represents a full bibliographic database.
	It also looks like a dictionnary, each key being an instance
	of class Key.

	The foreach() method should provide an efficient way of
	looping over all the elements, if one exists. 
	'''

	# a default database provides no editing facilities
	# (as it cannot be saved)
	properties = {}

	id    = 'VirtualDB'
	__count = 0
	__keyid = 0
	
	
	def __init__ (self, basename):
		self.name = basename

		self.key  = 'base-' + str (DataBase.__count)
		DataBase.__count = DataBase.__count + 1

		self.__dict = {}
		return
	
	def has_property (self, prop):
		''' indicates if the database has a given property '''
		
		if self.properties.has_key (prop):
			return self.properties [prop]
		
		return 0
	
	def new_entry (self):
		''' returns a newly created entry '''

		name = None
		key  = None
		
		# generate a new key
		while (not name) or self.has_key (key):
			name = "entry-%d" % self.__keyid
			key = Key (self, name)
			
			self.__keyid = self.__keyid + 1

		# get the first type
		type = Config.get ("base/defaulttype").data

		# return the new entry
		return Entry (key, type)


	def keys (self):
		''' Returns a list of all the keys available for the database '''
		return self.__dict.keys ()

	def has_key (self, key):
		''' Tests for a given key '''
		return self.__dict.has_key (key)

	def __getitem__ (self, key):
		''' Returns the Entry object associated with the key '''
		return self.__dict [key]

	def __setitem__ (self, key, value):
		''' Sets a key Entry '''
		
		self.__dict [key] = value
		return

	def __delitem__ (self, key):
		''' Removes an Entry from the database, by its key '''
		del self.__dict [key]
		return
	
	def __len__ (self):
		''' Number of entries in the database '''
		return len (self.keys ())

	def __repr__ (self):
		return "<generic bibliographic database (" + `len (self)` + \
		       " entries)>"
		

	def where (self, test):
		''' Returns a subset of the entries according to a
		criterion '''
		keys = []
		for e in self.keys ():
			if test.match (self [e]):
				keys.append (e)

		refs = Reference ()
		
		if len (keys):
			refs.add (self, keys)

		refs.properties = self.properties
		return refs
	
	def foreach (self, function, args = None):
		''' Run function on every entry. '''
		
		for e in self.keys ():
			function (self [e], args)
		return

	def update (self):
		''' Updates the Entries stored in the database '''
		
		raise IOError, "no update method defined"
		return


	def sort (self, sortkey = SortByKey):

		''' sort entries according to a given key.  If the
		sortkey is None, sort according to the entry key '''
		
		# collect key values
		dict = {}
		none = []
		
		def collect (entry, arg):
			sortkey, dict, none = arg

			if sortkey is SortByKey :
				# sort by key
				dict [entry.key] = entry.key
				return

			if sortkey is SortByType :
				# sort by type name
				dict [entry.key] = entry.type.name
				return
			
			if entry.has_key (sortkey):
				dict [entry.key] = entry [sortkey]
			else:
				none.append (entry.key)
			return

		self.foreach (collect, (sortkey, dict, none))
		
		keys = dict.keys ()
		def sort_method (a,b, dict = dict):
			return cmp (dict [a], dict [b])
		
		keys.sort (sort_method)
		
		r = Reference ()
		r.add (self, none + keys)

		# simple search, copy the properties
		r.properties = self.properties
		return r



# ----- A class that holds references from several databases -----

Pyblio.Help.register ('references', '''

References are generic holders of subsets or complete databases. One
can apply several method on a reference :

 - ref.add (base, items) : adds `items' from a given `base' in the
   reference
 
 - ref.foreach (method, argument) : calls `method' on every entry
 - ref.where ( condition ) : returns the reference of entries matching
   the condition

 - ref.bases () : a list of all the bases that compose the reference
 - ref.refs (base) : entries from a given database
 - ref.base_foreach (base) : like `foreach' but only on a given database

In addition, references can be merged with `+'.
''')


class Reference (DataBase):

	''' This class is a specialization of DataBase, whose purpose
	is to store entries from different sources, and to keep the
	order of these entries. Therefore it is often used to store
	the results of a sort or search operation. '''
	
	__count = 0
	id = 'Reference'


	def __init__ (self):
		self.__refs  = []
		self.__bases = {}
		
		self.key  = 'ref-' + str (Reference.__count)
		Reference.__count = Reference.__count + 1

		return
	
	
	def add (self, base, liste = None):
		''' Add a list of Keys corresponding to a given database '''

		if base.id == 'Reference':
			for b in base.bases ():
				self.__bases [b.key] = b
		else:
			self.__bases [base.key] = base
		
		if liste is None:
			liste = base.keys ()

		if type (liste) is ListType:
			self.__refs = self.__refs + liste
		else:
			self.__refs.append (liste)
		return

	def remove (self, key):
		''' Removes a Key from the Reference (no impact on the
		underlying database '''

		self.__refs.remove (key)
		return

	
	def bases (self):
		''' Returns the databases available in the Reference
		object '''
		
		return self.__bases.values ()
	

	def base (self, entry):
		''' Returns the database an entry actually comes from '''
		return self.__bases [entry.key.base]

	
	def refs (self, base):
		''' Returns the references available in a given
		database '''
		
		if self.__bases.has_key (base.key):
			return filter (lambda x, base = base:
				       x.base == base.key,
				       self.__refs)
		
		return None


	def base_foreach (self, base, function, arg = None):
		''' Foreach entry in a given base '''
		
		for k in self.refs (base):
			entry = base [k]
			function (entry, arg)
		return

	
	def __add__ (self, other):
		''' Merges two References to create a third one '''
		
		r = Reference ()

		for b in self.bases ():
			r.add (b, self.refs (b))

		for b in other.bases ():
			r.add (b, other.refs (b))

		return r


	def foreach (self, function, arg = None):
		''' Foreach entry in all the databases '''
		
		for k in self.keys ():
			function (self [k], arg)
		return
		

	def __len__ (self):
		''' Number of entries in the Reference '''
		
		return len (self.keys ())


	def keys (self):
		''' Returns the list of the keys in the Reference '''
		
		# Only returns the really existing keys
		ret = []
		bad = []
		# separate the already existing keys from those who
		# vanished
		for k in self.__refs:
			if self.__bases [k.base].has_key (k):
				ret.append (k)
			else:
				bad.append (k)

		# remove the bad keys
		for k in bad:
			self.__refs.remove (k)
			
		return ret

	
	def has_key (self, key):
		''' Tests if a Key is in the Reference '''
		
		# Do we know this key ?
		if not self.__refs.count (key):
			return 0
		# If yes, does it still exist ?
		if self.__bases [key.base] [key]:
			return 1
		# So, remove it for the next time !
		self.__refs.remove (key)
		return 0

	
	def __getitem__ (self, key):
		''' Returns an Entry given its Key '''
		return self.__bases [key.base] [key]


	def __delitem__ (self, key):
		''' Removes an Entry (both in the Reference and in the
		real database) '''
		
		# delete from the target database
		del self.__bases [key.base] [key]
		# delete from our list
		self.__refs.remove (key)
		return

	
	def __setitem__ (self, key, value):
		self.__bases [key.base] [key] = value

		# eventually add it to the current list
		if not self.has_key (key):
			# check the database
			if not self.__bases.has_key (key.base):
				raise KeyError, "database `%s' is unknown in this Reference" \
				      % key.base
			
			self.__refs.append (key)
		return

	
	def new_entry (self):
		if self.has_property ('add'):
			return self.bases () [0].new_entry ()

		return DataBase.new_entry (self)

		
	def update (self):
		# if we have any edition property
		if self.has_property ('edit') or self.has_property ('add') or\
		   self.has_property ('remove'):
			
			for b in self.bases ():
				b.update ()
			return
		
		# else, raise an error
		raise IOError, "can't update a database of type Reference ()"
	

	def where (self, test):
		r = Reference ()

		for k in self.keys ():
			entry = self [k]
			
			if test.match (self [k]):
				r.add (self.base (entry), k)

		r.properties = self.properties
		return r


	def __repr__ (self):
		''' Representation of the database '''
		
		return "Reference (<...%d entries...>)" % len (self.keys ())
