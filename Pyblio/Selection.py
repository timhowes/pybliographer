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

class SearchSelection:

    def __init__ (self, search, iterator):
        self.search   = search
        self.iterator = iterator
        return

    def first (self):
        entry = self.iterator.first ()
        if not entry: return None
            
        while not self.search.match (entry):
            entry = self.iterator.next ()
            if not entry: return None
            
        return entry

    def next (self):
        entry = self.iterator.next ()
        if not entry: return None
        
        while not self.search.match (entry):
            entry = self.iterator.next ()
            if not entry: return None

        return entry


class SortSelection:

    def __init__ (self, sort, iterator):
        # compute asap
        (self.keys, self.data)  = sort.sort (iterator)
        self.count = 0
        return

    def first (self):
        self.count = 0
        return self.next ()

    def next (self):
        try:
            ret = self.data [self.keys [self.count]]
        except IndexError:
            return None
        
        self.count = self.count + 1
        return ret
    
        
class Selection:
        
    def __init__ (self, search = None, sort = None):
        self.search = search
        self.sort   = sort
        return
    
    def iterator (self, iterator):
        ''' returns an iterator that will provide the entries of the
        database according to the properties of the current Selection
        '''

        # no filtering ? then pass through
        if not self.search and not self.sort:
            return iterator

        if not self.sort:
            return SearchSelection (self.search, iterator)

        if not self.search:
            return SortSelection (self.sort, iterator)

        return SortSelection (self.sort,
                              SearchSelection (self.search, iterator))
    
        
        
