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

import xml.sax

from xml.dom import minidom

from Pyblio import Exceptions
from Pyblio import Autoload
from Pyblio.Connector import Publisher

class Engine (Publisher):

    ''' A base query class that must be derived by each search
    connection family '''

    def __init__ (self, host, parameters):
        ''' Create a connection with a remote server  '''
        pass

    def search (self, args):
        pass

    def cancel (self):
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

        try:
            dom  = minidom.parse (open (description, 'r'))
        except xml.sax.SAXParseException:
            raise Exceptions.SyntaxError ('Cannot parse the XML file')
        
        root = dom.documentElement
        
        if string.lower (root.nodeName) != 'pyblioquery':
            raise Exceptions.SyntaxError ('invalid XML file')

        cnx = root.getElementsByTagName ('Connection') [0]
        
        try:
            self.type = cnx.attributes ['type'].value
        except KeyError:
            raise Exceptions.SyntaxError ('missing type in connection')

        self.name = getString (cnx.getElementsByTagName ('Name') [0])
        self.host = getString (cnx.getElementsByTagName ('Host') [0])

        self.args = {}

        for param in cnx.getElementsByTagName ('Parameter'):
            key = param.attributes ['name'].value
            val = getString (param)

            self.args [key] = val

        # get the query model of the server
        
        return

    def engine (self):
        
        query = Autoload.get_by_name ('query', self.type).data
        
        if query is None:
            raise Exceptions.SyntaxError ('unknown query module: %s' %
                                          cnx_type)

        return query (self.host, self.args)
            
        
