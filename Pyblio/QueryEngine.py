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

    return string.strip (s)


class Connection:

    ''' Definition of the connection to a specific server '''

    def __init__ (self, file, form):

        self.name = None
        
        try:
            dom  = minidom.parse (open (file, 'r'))
        except xml.sax.SAXParseException, msg:
            raise Exceptions.SyntaxError ('Cannot parse the XML file\n%s' %
                                          msg)
        
        root = dom.documentElement
        
        if string.lower (root.nodeName) != 'connection':
            raise Exceptions.SyntaxError ('Not a Connection XML file')

        for node in root.childNodes:
            tag = string.lower (node.nodeName)

            if tag == 'name':
                self.name = getString (node)
                continue

            if tag == 'server':
                self.__parse_server (node)
                continue

            if tag == 'query':
                self.__parse_query (node, form)
                continue
        
        return


    def __parse_server (self, root):

        self.args = {}
        self.type = None
        self.host = None
        
        try:
            self.type = root.attributes ['type'].value
        except KeyError:
            raise Exceptions.SyntaxError ('Unspecified Connection type')
        
        for node in root.childNodes:
            tag = string.lower (node.nodeName)

            if tag == 'host':
                self.host = getString (node)
                continue

            if tag == 'parameter':
                key = node.attributes ['name'].value
                val = getString (node)
            
                self.args [key] = val
                continue

        return


    def __parse_query (self, root, form):
        self.default  = None
        self.extended = None

        for node in root.childNodes:
            tag = string.lower (node.nodeName)

            if tag == 'default':
                if self.default is None:
                    self.default = form ()

                self.default.parse (node)
                continue
            
            if tag == 'extended':
                if self.extended is None:
                    self.extended = form ()

                self.extended.parse (node)
                continue
            
        return


    def engine (self):
        
        query = Autoload.get_by_name ('query', self.type).data
        
        if query is None:
            raise Exceptions.SyntaxError ('unknown query module: %s' %
                                          cnx_type)

        return query (self.host, self.args)
            
        
    

class QOperator:
    ''' Allowed operators for a field search '''

    def parse (self, root):
        try:
            self.name = root.attributes ['name'].value
        except KeyError:
            raise Exceptions.SyntaxError ('missing name in operator')

        self.title = getString (root)
        return

    
class QField:

    CL = {
        'QOperator' : QOperator
        }
    
    ''' A specific field that can be searched '''

    def __init__ (self, operators = []):

        self.operators = [] + operators
        return
    

    def parse (self, root):
        self.title = None

        try:
            self.name = root.attributes ['name'].value
        except KeyError:
            raise Exceptions.SyntaxError ('missing name in field')

        try:
            self.type = root.attributes ['type'].value
        except KeyError:
            raise Exceptions.SyntaxError ('missing type in field')


        for node in root.childNodes:
            tag = string.lower (node.nodeName)

            if tag == 'title':
                self.title = getString (node)
                continue

            if tag == 'operator':
                p = self.CL ['QOperator'] ()
                p.parse (node)

                self.operators.append (p)
                continue

        if self.title is None:
            raise Exceptions.SyntaxError ('missing title in field')
        
        return


class QFields:

    CL = {
        'QOperator'  : QOperator,
        'QField'     : QField,
        }
    
    ''' Sets of fields the user can search on '''

    def parse (self, root):
        self.max   = None
        self.title = None
        self.content = []

        operators = []
        
        try:
            self.max = int (root.attributes ['max'].value)
        except ValueError:
            raise Exceptions.SyntaxError ('invalid fields maximal value')
        except KeyError:
            pass

        try:
            self.name = root.attributes ['name'].value
        except KeyError:
            raise Exceptions.SyntaxError ('missing name in fields')

        for node in root.childNodes:
            tag = string.lower (node.nodeName)

            if tag == 'title':
                self.title = getString (node)
                continue

            if tag == 'operator':
                p = self.CL ['QOperator'] ()
                p.parse (node)

                operators.append (p)
                continue
            
            if tag == 'field':
                p = self.CL ['QField'] (operators)
                p.parse (node)
                
                self.content.append (p)
                continue

        return


class QSelection:
    ''' A selection between several choices '''
    def parse (self, root):
        self.content = []
        self.title   = None
        
        try:
            self.name = root.attributes ['name'].value
        except KeyError:
            raise Exceptions.SyntaxError ('missing name in selection')

        for node in root.childNodes:
            tag = string.lower (node.nodeName)

            if tag == 'title':
                self.title = getString (node)
                continue

            if tag == 'item':
                text = getString (node)
                try:
                    name = node.attributes ['name'].value
                except ValueError:
                    raise Exceptions.SyntaxError ('missing name in item')

                self.content.append ((name, text))
                continue

        if self.title is None:
            raise Exceptions.SyntaxError ('missing title in selection')
        return

class QToggle:
    ''' A selection between two choices '''

    def parse (self, root):
        try:
            self.name = root.attributes ['name'].value
        except KeyError:
            raise Exceptions.SyntaxError ('missing name in toggle')

        if not root.hasAttribute ('default'):
            self.enabled = 0
        else:
            val = string.lower (root.attributes ['default'].value)
            self.enabled = val == 'true'
            
        self.title = getString (root)
        return


class QGroup:
    CL = {
        'QFields' : QFields,
        'QSelection' : QSelection,
        'QToggle' : QToggle,
        }

    ''' Grouping of several query forms '''

    def __init__ (self):
        self.content = []
        return

    def parse (self, root):
        self.title = None
        
        for node in root.childNodes:
            tag = string.lower (node.nodeName)

            if tag == 'title':
                self.title = getString (node)
                continue

            if tag in ('fields', 'selection', 'toggle'):
                cls = 'Q' + string.capitalize (tag)
                
                fields = self.CL [cls] ()
                fields.parse (node)
                
                self.content.append (fields)
                continue

        return

class QForm:
    ''' Complete description of a query form '''

    CL = {
        'QFields'    : QFields,
        'QGroup'     : QGroup,
        'QSelection' : QSelection,
        'QOperator'  : QOperator,
        'QToggle'    : QToggle,
        }

    def __init__ (self):

        self.content = []
        return

    
    def parse (self, root):
        
        for node in root.childNodes:
            tag = string.lower (node.nodeName)

            if tag in ('fields', 'group', 'selection', 'toggle'):
                cls = 'Q' + string.capitalize (tag)
                
                fields = self.CL [cls] ()
                fields.parse (node)
                
                self.content.append (fields)
                continue

        return

