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

import string
from Pyblio import Config

# Available field types
TypeText   = 0
TypeAuthor = 1
TypeTitle  = 2
TypeDate   = 3


def getentry (entry, has_default = 1):
	''' Returns an entry description given its name '''
	entries = Config.get ("base/entries").data

	l = string.lower (entry)
	
	if entries.has_key (l):
		return entries [l]

	if has_default:
		return EntryDescription (entry)

	return None

def gettype (entry, field):
	''' Return a field type given its name and the entry it
	belongs to '''
	
	fields = Config.get ("base/fields").data

	if entry and entry.has_key (field):
		return entry [field].type
	
	if fields.has_key (field):
		return fields [field].type
	
	return TypeText

	

class Description:
	''' Generic Holder for information related to Field/Entry
	descriptions '''
    
	def __init__ (self, name):
		self.name       = name
		self.__items__  = {}
		return
    
	def __getattr__ (self, attr):
		raise AttributeError, "no attribute `%s' in Description" % (attr)

	def __setattr__ (self, attr, value):
		self.__dict__ [attr] = value
		return
    
	def __getitem__ (self, item):
		return self.__items__ [item]
	
	def __setitem__ (self, item, value):
		self.__items__ [item] = value
		return
    
	def has_key (self, field):
		return self.__items__.has_key (field)
	
	def __hash__ (self):
		return hash (self.name)


class FieldDescription (Description):
	''' Available informations for a given field type '''
    
	def __init__ (self, name, type = TypeText):
        
		Description.__init__ (self, name)
		self.type = type
		return

    
class EntryDescription (Description):
	''' Informations on a given entry type '''
    
	def __init__ (self, name):
		Description.__init__ (self, name)
		
		self.__dict__ ['mandatory'] = []
		self.__dict__ ['optional']  = []
		self.__dict__ ['lcfields']  = {}
		return

	def __str__ (self):
		return "<EntryDescription `%s'>" % self.name
	
	def __getattr__ (self, attr):
		if attr == 'fields':
			return self.mandatory + self.optional
		
		return Description.__getattr__ (self, attr)

	def __setattr__ (self, attr, value):

		if attr == 'mandatory' or attr == 'optional':
			self.__dict__ [attr] = value
			self.__dict__ ['lcfields'] = {}
            
			for f in self.fields:
				self.__dict__ ['lcfields'] [string.lower (f.name)] = f

		else:
			Description.__setattr__ (self, attr, value)
			
		return
	
	def __getitem__ (self, item):
		return self.__dict__ ['lcfields'] [string.lower (item)]

	def __setitem__ (self, item, value):
		self.__dict__ ['lcfields'] [string.lower (item)] = value
		return
	
	def has_key (self, field):
		return self.__dict__ ['lcfields'].has_key (string.lower (field))

