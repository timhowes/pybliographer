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

''' This class defines certain graphical properties of output, in
order to insulate a bibliographic style definition from its
realization in a given language '''

import sys

from Pyblio import Autoload, Base

class Formatter:
    """ Base class for each file format writer """
    
    coding = 'Latin1'
    
    def __init__ (self, stdout = sys.stdout):
        self.out     = stdout
        self.counter = 1
        return

    def begin_document (self, name):
        """ Write a document header in the output flow """
        pass

    def end_document (self, name):
        """ Write a document footer in the output flow """
        pass
    
    def begin_biblio (self, id, table = None):
        """ Start a bibliography """
        pass

    def end_biblio (self):
        """ Finish a bibliography """
        pass

    def next_key (self):
        """ Ask for a numerical key """
        
        key = str (self.counter)
        self.counter = self.counter + 1

        return key

    def begin_entry (self, key, entry):
        """ Start a new bibliographic entry """
        pass
    
    def write (self, text, style = None):
        """ Sends a certain text with a given style to the output flow """
        self.out.write (text)
        return

    def separator (self):
        self.write (" ")
        return
    
    def end_entry (self):
        """ Finish a bibliographic entry """
        self.write ("\n")
        return
    


def format (fields,
            text,
            filter  = None,
            out     = sys.stdout,
            default = {},
            pre     = {},
            post    = {}):

    printable = {}
    # completer le texte
    for f in fields.keys ():
        t = fields [f]
        
        if filter:
            t = filter (t)
        
        if pre.has_key (f):
            t = pre [f] + t
            
        if post.has_key (f):
            t = t + post [f]

        printable [f] = t
        
    # completer les champs
    for f in default.keys ():
        if not fields.has_key (f):
            printable [f] = default [f]


    out.write (text % printable)

    return
