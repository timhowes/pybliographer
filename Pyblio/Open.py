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


from types import *
import Pyblio.Base, Pyblio.Help
from Pyblio import Autoload

import urlparse, urllib, traceback, os, sys, tempfile, string


__urlhandles = []


Pyblio.Help.register ('bibopen', """
Syntax: database = bibopen (source)

bibopen  tries several  method  to open  `source'  as a  bibliographic
entry. `source'  can be  a simple file  or even  an URL. FTP  and HTTP
files are automatically fetched. One can even create a specific method
for client/server access for example.

One can apply the following commands on the output of bibopen :

 - database.keys () : lists the available entries
 - database ['key'] : returns a given entry
 - del database ['key'] : removes an entry from the file
 - database.where (...) : searches the base (see also `searching')
""")


def get_by_name (entity, method):
	''' returns a specific field of the given entity '''

	meth = Autoload.get_by_name ("format", entity)
	
	if meth and meth.data.has_key (method):
		return meth.data [method]

	return None

def get_by_regexp (entity, method):
	''' returns a specific field of the given entity '''

	meth = Autoload.get_by_regexp ("format", entity)
	
	if meth and meth.data.has_key (method):
		return meth.data [method]

	return None


def bibopen (entity, how = None):
	"Generic function to open a bibliographic database"

	def simple_try (url, how):
		base = None

		if how == None:
			listedmethods = Autoload.available ("format")
			
			for method in listedmethods:
				opener = get_by_name (method, 'open')
				if opener:
					base = opener (url, 1)
					if base is not None:
						return base
			return None
		
		opener = get_by_name (how, 'open')
		
		if opener:
			base = opener (url, 0)
		else:
			raise IOError, \
			      "method `%s' provides no opener" % how
		
		return base
	
	# Consider the reference as an URL
	url = list (urlparse.urlparse (entity))

	if url [0] == '':
		# Consider we handle a local file
		url [0] = 'file'
		url [2] = os.path.expanduser (url [2])

	# eventually load a new module
	if how is None:
		handler = Autoload.get_by_regexp ("format", urlparse.urlunparse (url))
		if handler:
			how = handler.name
	
	base = simple_try (url, how)
	
	# If one don't know how to retrieve a remote file, do it
	if base is None and (url [0] == 'http' or url [0] == 'ftp'):

		class myopener (urllib.FancyURLopener):
			def http_error_default(self, url, fp, errcode, errmsg, headers):
				raise IOError, "%d: %s" % (errcode, errmsg)

		urlhandle = myopener ()
		file, header = urlhandle.retrieve (entity, None, None)

		__urlhandles.append (urlhandle)
		
		url = ['file', '', file, '', '', '']

		base = simple_try (url, how)
		
	if base is None:
		raise IOError, "don't know how to open `" + entity + "'"
    
	return base


Pyblio.Help.register ('bibwrite', """
Syntax: bibwrite (entity, output, how)

This function sends an entry description to the specified output
(stdout by default), formatted as specified by the third argument. By
default, this formatting is the same as the one used by `more'
""")


def bibwrite (entity, out = None, how = None):
	''' '''

	# default output
	out = out or sys.stdout
	
	def simplewrite (entry, output = sys.stdout):
		''' Print an entry as simple text '''
		output.write (str (entry) + "\n")

	
	if how == None:
		entity.foreach (simplewrite, out)
		return

	writer = get_by_name (how, 'write')
	
	if writer is None:
		raise IOError, "type `%s' does not specify write method" % how

	writer (entity, out)
	return

Pyblio.Help.register ('bibnew', """
Syntax: bib = bibnew (name, type)

Creates a new bibliographic database of a given type
""")

def bibnew (name, type = None):

	opener = get_by_name (type, 'new')
	
	if opener is None:
		if os.path.exists (name):
			raise IOError, "file `%s' exists" % name
		
		file = open (name, 'w')
		file.close ()
		
		return bibopen (name, type)

	# Consider the reference as an URL
	url = list (urlparse.urlparse (name))

	if url [0] == '':
		# Consider we handle a local file
		url [0] = 'file'
		url [2] = os.path.expanduser (url [2])

	return opener (url)
