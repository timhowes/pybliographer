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

from types import *


class Key:

	''' A special key that embeds both database id and database
	key Such a key is expected to be completely unique among the
	whole program and should be the reliable information checked
	to see if two entries are the same.

	The .base field is the database id from which the actual entry
	can be recovered, whereas the .key field is the name in the
	database itself.  '''
	
	def __init__ (self, base, key):
		if type (key) is InstanceType:
			self.base = key.base
			self.key  = key.key
		else:
			self.key  = key
			self.base = base.key
		return

	def __repr__ (self):
		return 'Key (%s, %s)' % (`self.base`, `self.key`)
	
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
		return hash (`self.key` + `self.base`)

