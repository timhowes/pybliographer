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

class Sort:
    ''' This class defines the methods used to sort a database '''
    
    def __init__ (self, fields = None):
        ''' Create a Sort class with a given set of SortFields '''
        
        self.fields = fields or []
        return

    def sort (self, iterator):
        ''' Returns a list of keys sorted according to the current
        sort settings '''
        
        data = {}
        keys = []
        ent  = {}
        
        # get the data for each field
        entry = iterator.first ()
        while entry:
            item = []
            for field in self.fields:
                item.append (field.get_field (entry))
                
            data [entry.key] = item
            keys.append (entry.key)
            ent  [entry.key] = entry
            
            entry = iterator.next ()

        # sort them
        def cmp_fcn (a, b, data = data):
            return cmp (data [a], data [b])

        keys.sort (cmp_fcn)
        
        return keys, ent

    
class TypeSort:

    def get_field (self, entry):
        return entry.type


class KeySort:

    def get_field (self, entry):
        return entry.key


class FieldSort:
    
    def __init__ (self, field):
        self.field = field
        return

    def get_field (self, entry):
        try:
            return entry [self.field]
        except KeyError:
            return None
            
