# This file is part of pybliographer
# 
# Copyright (C) 1998-2002 Frederic GOBRY
# Email : gobry@users.sf.net
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

''' Manage the generic query interface. '''

from libglade import GladeXML
from Pyblio import version

import os

path = os.path.join ('Pyblio', 'GnomeUI', 'query.glade')

if not os.path.exists (path):
    path = os.path.join (version.prefix, path)


class QueryUI:

    def __init__ (self, parent = None):

        xml = GladeXML (path, 'query')
        xml.signal_autoconnect ({ 'search' : self.search,
                                  'cancel' : self.cancel })
        
        self.w = xml.get_widget ('query')

        if parent: self.w.set_parent (parent)

        self.w.show_all ()
        return

    def search (self, * arg):
        print arg

    def cancel (self, * arg):
        print arg
                
