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

import string, types, re, string, recode

year_match = re.compile ('(\d\d\d\d)')

formatter_cache = {}

def get_formatter (format):
    ''' This function is used to get a recode formatter in an
    efficient way '''
    
    format = string.lower (format)
    
    if formatter_cache.has_key (format):
        ft = formatter_cache [format]
    else:
        ft = recode.recode ("latin1.." + format)
        formatter_cache [format] = ft

    return ft


class Access:
    ''' virtual class used to check if instance attributes have been
    modified '''
    
    def __init__ (self):
        self.clean ()
        return

    def __setattr__ (self, attr, value):
        if attr == '_modified_':
            raise AttributeError, "can't modify _modified_"
        
        self.__dict__ [attr] = value
        self.touch ()
        return

    def modified (self):
        return self._modified_

    def clean (self):
        self.__dict__ ['_modified_'] = 0
        return

    def touch (self):
        self.__dict__ ['_modified_'] = 1
        return


class Author (Access):
    ''' Fine description of an author '''
    
    def __init__ (self, copy = None, strict = 0):
        ''' Initialize an author from a string or an other Author '''

        if type (copy) is types.StringType:
            # manually split the author into subfields.
            self.honorific = None
            self.lineage   = None

            blocs = string.split (copy, ',')
            
            if len (blocs) == 1:
                if strict:
                    # strict parsing, the whole block is the last name
                    self.last  = blocs [0]
                    self.first = None
                else:
                    # lazy parsing, last name is after lowercase or is last word
                    words = map (string.strip, string.split (blocs [0]))
                    i = 0
                    while i < len (words) - 1:
                        if words [i] == string.lower (words [i]): break
                        i = i + 1
                    
                    self.first = string.join (words [:i], ' ')
                    self.last  = string.join (words [i:], ' ')
                    
            elif len (blocs) == 2:
                self.last  = string.strip (blocs [0])
                self.first = string.strip (blocs [1])
                
            elif len (blocs) == 3:
                self.last    = string.strip (blocs [0])
                self.lineage = string.strip (blocs [1])
                self.first   = string.strip (blocs [2])

            else:
                self.last  = copy
                self.first = None

            # cleanup
            if self.last == '':    self.last    = None
            if self.first == '':   self.first   = None
            if self.lineage == '': self.lineage = None
                        
        else:
            if copy:
                def clean_entry (f):
                    if f is not None:
                        f = string.strip (f)
                        if f == '': f = None

                    return f
                
                copy = map (clean_entry, copy)

                self.honorific = copy [0]
                self.first     = copy [1]
                self.last      = copy [2]
                self.lineage   = copy [3]
            else:
                self.honorific = None
                self.first     = None
                self.last      = None
                self.lineage   = None

        self.text = None

        Access.__init__ (self)
        return


    def format (self, fmt):
        ''' Returns the fields in a given format '''
        
        ft = get_formatter (fmt)
            
        return (ft (self.honorific), ft (self.first),
                ft (self.last), ft (self.lineage))

    
    def __str__ (self):
        ''' Returns textual representation '''

        changed = self.modified ()
        if changed or not self.text:
            text = ""
            if self.honorific: text = text + " " + self.honorific
            if self.first:     text = text + " " + self.first
            if self.last:      text = text + " " + self.last
            if self.lineage:   text = text + ", " + self.lineage
            self.text = text [1:]
            if not changed: self.clean ()
            
        return self.text


    def __repr__ (self):
        return "Author ((%s, %s, %s, %s))" % (`self.honorific`, `self.first`,
                                              `self.last`, `self.lineage`)


    def match (self, regex):
        ''' '''
        return regex.search (str (self))


    def initials (self, format = None):
        ''' Extract initials from a first name '''

        total = []

        if self.first is None: return None
        
        for atom in string.split (self.first, ' '):
            list = []
            
            for word in string.split (atom, '-'):
                list.append (word [0] + '.')
                
            total.append (string.join (list, '-'))
            
        text = string.join (total, ' ')
        if format:
            ft = get_formatter (format)
            text = ft (text)

        return text

    def __cmp__ (self, other):
        ''' field comparison '''
        
        r = cmp (self.last, other.last)
        if r != 0: return r

        r = cmp (self.first, other.first)
        if r != 0: return r

        r = cmp (self.lineage, other.lineage)
        if r != 0: return r
        
        r = cmp (self.honorific, other.honorific)
        if r != 0: return r

        return 0


class AuthorGroup (Access):
    ''' A group of Authors '''

    def __init__ (self):
        self.authors = []
        Access.__init__ (self)
        return

    def __getitem__ (self, pos):
        return self.authors [pos]

    def __setitem__ (self, pos, val):
        self.authors [pos] = val
        self.val.touch ()
        return

    def __len__ (self):
        return len (self.authors)

    def modified (self):
        for a in self.authors:
            if a.modified (): return 1
        return 0

    def clean (self):
        for a in self.authors:
            a.clean ()
        return
    
    def append (self, value):
        self.authors.append (value)
        
    def __str__ (self):
        return string.join (map (str, self.authors), ", ")

    def __repr__ (self):
        return `self.authors`

    def match (self, regex):
        return regex.search (string.join (map (str, self.authors), " "))

    def __cmp__ (self, other):
        i = 0
        try:
            s = len (self), len (other)
        except TypeError:
            return 1
        
        m = max (s)
        
        while i < m:
            if i >= s [0]: return -1
            if i >= s [1]: return +1

            r = cmp (self [i], other [i])
            if r != 0: return r

            i = i + 1

        return 0
            
RangeError = "RangeError"

class Date (Access):
    ''' Fine description of a date '''

    def __init__ (self, arg = (None, None, None)):

        if type (arg) is types.StringType:
            try:
                year  = int (arg)
            except ValueError:
                g = year_match.search (arg)
                if g:
                    year = int (g.group (1))
                else:
                    raise ValueError, "can't parse `%s' as a date" % arg
                
            month = None
            day   = None
        else:
            year, month, day = arg
        
        if year and year < 0:
            raise RangeError, "wrong year"
        self.year = year
        
        if month and (month < 1 or month > 12):
            raise RangeError, "wrong month"
        self.month = month
        
        if day and (day < 1 or day > 31):
            raise RangeError, "wrong day"
        self.day = day

        self.text = None
        Access.__init__ (self)
        return

    def __cmp__ (self, other):

        # No date is no date !
        if not self.year and not other.year: return 0

        diff = (self.year or other.year) - (other.year or self.year)
        if diff: return diff

        # Same year
        if not self.month and not other.month: return 0

        diff = (self.month or other.month) - (other.month or self.month)
        if diff: return diff
        
        # Same month
        if not self.day and not other.day: return 0

        return (self.day or other.day) - (other.day or self.day)

    def __str__ (self):
        ''' Returns textual representation '''
        changed = self.modified ()

        if changed or not self.text:
            if self.year and self.month and self.day:
                self.text = "%d/%d/%d" % (self.day, self.month, self.year)

            if self.year and self.month:
                self.text = "%d/%d" % (self.month, self.year)
            
            self.text = str (self.year)
            if not changed: self.clean ()
            
        return self.text

    def format (self, fmt):
        ''' Returns the fields in a given format '''
        ft = get_formatter (fmt)

        if self.year:
            year = ft (str (self.year))
        else: year = None

        if self.month:
            month = ft (str (self.month))
        else: month = None

        if self.day:
            day = ft (str (self.day))
        else: day = None

        return year, month, day

    
    def __repr__ (self):
        return str (self)


    def match (self, regex):
        ''' '''
        return regex.search (str (self))
        

class Text (Access):
    '''
    This class holds all the other fields (not an Author or a Date)
    '''
    
    def __init__ (self, text):
        self.text = text

        Access.__init__ (self)
        return


    def __str__ (self):
        return str (self.text)


    def __repr__ (self):
        return "Text (%s)" % `self.text`


    def match (self, regex):
        '''   '''
        return regex.search (self.text)


    def __cmp__ (self, other):
        return cmp (self.text, str (other))


    def format (self, fmt):
        ''' Returns the fields in a given format '''
        ft = get_formatter (fmt)

        return ft (self.text)
