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

import string

from xml.dom import minidom

from Pyblio import Exceptions
from Pyblio import Autoload

class Query:

    ''' A base query class that must be derived by each search
    connection family '''

    pass


def getString (element):
    s = ''
    
    for node in element.childNodes:
        if node.nodeType == node.TEXT_NODE:
            s += node.data

    return s


class Connection:

    ''' Definition of the connection to a specific server '''

    def __init__ (self, description):

        dom  = minidom.parse (open (description, 'r'))
        root = dom.documentElement
        
        if string.lower (root.nodeName) != 'pyblioquery':
            raise Exceptions.ParserError ('invalid XML file')

        cnx = root.getElementsByTagName ('Connection') [0]
        
        try:
            cnx_type = cnx.attributes ['type'].value
        except KeyError:
            raise Exceptions.ParserError ('missing type in connection')

        self.name = getString (cnx.getElementsByTagName ('Name') [0])
        
        host = getString (cnx.getElementsByTagName ('Host') [0])

        args = {}

        for param in cnx.getElementsByTagName ('Parameter'):
            key = param.attributes ['name'].value
            val = getString (param)

            args [key] = val

            
        query = Autoload.get_by_name ('query', cnx_type).data
        if query is None:
            raise Exceptions.ParserError ('unknown query module: %s' %
                                          cnx_type)

        self.engine = query (host, args)
        return
            
        
