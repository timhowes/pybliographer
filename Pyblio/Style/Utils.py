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

""" This module contains several functions that can ease the work of
describing a new bibliographic style """

import string

from Pyblio import recode

def author_desc (group, coding, initials = 0, reverse = 0):
    """ Create a nice string describing a group of authors.

    	coding   : name of the output coding (as requested for recode)
        initials : if = 1, uses initials instead of complete first names
        reverse  : use Last, First for all the authors, not only the first
    """
    
    l = len (group)
            
    fulltext = ""
    
    for i in range (0, l):
        (honorific, first, last, lineage) = group [i].format (coding)

        if initials:
            first = group [i].initials (coding)

        text = ""

        if i == 0 or reverse:
            if last:    text = text + last
            if lineage: text = text + ", " + lineage
            if first:   text = text + ", " + first
        else:
            if first:   text = first + " "
            if last:    text = text + last
            if lineage: text = text + ", " + lineage

        if text:
            if i < l - 2:
                text = text + ", "
            elif i == l - 2:
                text = text + " and "

        fulltext = fulltext + text
        
    return fulltext


def generate_key (database, fmt):
    """ Generates an alphabetical key for each entry. fmt is the
    output coding """

    rc = recode.recode ("latin1.." + fmt.coding)
    
    def generate_one_key (entry, fmt, table, rc = rc):
        
        if   entry.has_key ('author'): aut = entry ['author']
        elif entry.has_key ('editor'): aut = entry ['editor']
        else:                          aut = ()

        if len (aut) > 0:
            if len (aut) > 1:
                key = ''
                for a in aut:
                    honorific, first, last, lineage = a.format (fmt.coding)
                    key = key + string.join (map (lambda x:
                                                  x [0], string.split (last, ' ')), '')
                    if len (key) >= 3:
                        if len (aut) > 3:
                            key = key + '+'
                        break
            else:
                honorific, first, last, lineage = aut [0].format (fmt.coding)
                parts = string.split (last, ' ')
	            
                if len (parts) == 1:
                    key = parts [0][0:3]
                else:
                    key = string.join (map (lambda x: x [0], parts), '')
	
        else:
            key = rc (entry.key.key [0:3])
	
        if entry.has_key ('year'):
            year = entry ['year'].format (fmt.coding) [0]
            
            if year:
                key = key + year [2:]
	
        if table.has_key (key) or table.has_key (key + 'a'):
	
            if table.has_key (key):
                # rename the old entry
                new = key + 'a'
	        
                table [new] = table [key]
                del table [key]
	
            base = key
            suff = ord ('b')
            key  = base + chr (suff)
	        
            while table.has_key (key):
                suff = suff + 1
                key  = base + chr (suff)
	            
        return key


    # generate output keys
    key_table = {}

    def test_key (entry, fmt, key_table = key_table,
                  generate_one_key = generate_one_key):
        key = generate_one_key (entry, fmt, key_table)
        key_table [key] = entry.key
        return

    database.foreach (test_key, fmt)

    reverse_table = {}
    
    for k in key_table.keys ():
        reverse_table [key_table [k]] = k
        
    return reverse_table, key_table



class SimpleWriter:
    """ Class providing easy methods for writing bibliographies. To
    see it in action, please read the code of the Alpha style for
    example. """
    
    def __init__ (self, fmt, database, initials = 0):
        self.fmt = fmt
        self.database = database
        self.initials = initials
        
        self.has_written = 0
        self.can_sep = 0
        return


    def new_group (self):
        """ Starts a new group of information. Fields are separated by
        a dot """
        
        if self.can_sep:
            self.write ('.')
            self.fmt.separator ()
            
        self.has_written = 0
        self.can_sep = 0
        return


    def write (self, text, style = None, count = 1):
        """ Writes a text in a given style
        When count = 0, only perform writing if a real writing has
        been performed before. It is then possible to write
        
        self.write (', ', count = 0)
        self.write (text)
        
        ...and the comma won't be written if there was no text before
        """
        
        if text:
            if count or self.has_written:
                self.fmt.write (text, style)
                self.can_sep = 1
                
                if not count:
                    self.has_written = 0
                    
            if count:
                self.has_written = 1
        return

    def ewrite (self, entry, field,
                style = None,
                pre = None, post = None,
                force = 0):

        """ Writes a field from an entry :

        	entry : the full entry
                field : the field name
                style : the text style for the entry field
                pre   : a string that should be prepended to the text
                post  : a string that should be appended to the text
                force : 1 if the pre string has to be written anyway

        pre and post are not written if the entry field is unexistant
        or empty. If the field exists, pre is written if there has
        been a previous writing, unless force = 1.
        """
            
        if not entry.has_key (field): return

        text = string.strip (self.text (entry [field]))
        if not text: return
        
        if pre:  self.write (pre, count = force)
        self.write (text, style)
        if post: self.write (post)
        return


    def dwrite (self, entry,
                style = None, pre = None, post = None,
                force = 0):
        
        """ Like ewrite, but for a date. This methods automatically
        uses the year and month fields """
        
        text = string.strip (self.date (entry))
        if not text: return
        
        if pre:  self.write (pre, count = force)
        self.write (text, style)
        if post: self.write (post)
        return
        
    def awrite (self, entry, field,
                style = None, pre = None, post = None,
                force = 0):
        
        """ Like ewrite, but for an author group. """
        
        if not entry.has_key (field): return
        
        text = string.strip (self.author (entry [field]))
        if not text: return
        
        if pre:  self.write (pre, count = force)
        self.write (text, style)
        if post: self.write (post)
        return

        
    def author (self, group):
        """ Writes a nice string corresponding to an AuthorGroup field
        """
        
        return author_desc (group, self.fmt.coding, self.initials)


    def text (self, field):
        """ Formats a field in the given encoding """
        
        return field.format (self.fmt.coding)


    def date (self, entry):
        """ Formats a date in the given encoding """
        
        text = ""
        
        if entry.has_key ('year'):
            text, month, day = entry ['year'].format (self.fmt.coding)

        text = text or ""
        
        if entry.has_key ('month'):
            text = self.text (entry ['month']) + " " + text

        return text

            
    def get_list (self, table):
        """ Creates a list of keys in the order they should be used
        """
        
        k = table.keys ()
        k.sort ()
        
        return map (lambda x, table = table: table [x], k)

    def get_keys (self):
        """ Generate the keys as they should appear in the
        bibliography. Returns two hash tables :

        	- the first maps from biblio key to entry key
                - the second does the reverse mapping
        """
        
        return generate_key (self.database, self.fmt)


    def write_one (self, entry, key):
        """ Takes an entry and its key, and write the resulting
        bibliography """
        
        raise TypeError, "override me !"

    
    def run (self, id):
        """ Main function actually called to create the bibliography """
        
        # generate output keys
        key_table, reverse_table = self.get_keys ()

        # sort keys...
        key_list = self.get_list (reverse_table)

        self.fmt.start_group (id, key_table.values ())

        # write all the entries in the database
        for key in key_list:
            entry    = self.database [key]
            text_key = key_table [key]
            
            self.write_one (entry, text_key)

        self.fmt.end_group ()
        return
