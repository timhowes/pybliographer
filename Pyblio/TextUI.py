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

# --------------------------------------------------
# Basical `high level' functions
# --------------------------------------------------

from types import *

import os, sys, traceback, tempfile, string

from Pyblio import Base, Help, Search, Types, Autoload, Fields
from Pyblio.Open import bibopen, bibwrite

# ----- Create elementary Test -----

Help.register ('searching', """
The general syntax of a search is :

 dbase.where ( constraints )

...where `constraints' is an arbitrary construction of :

  -  has (field, value) : matches if `field' matches `value' (as a REGEXP)
  -  has_key (key) : matches if the entry matches the key
  -  has_type (typename) : matches if the entry is of the given type
  -  any_has (value) : matches if any of the fields matches the value
  -  before (field, year [, month [, day]]) : matches if the entry is older than the date
  -  after (field, year [, month [, day]]) : matches if the entry is younger than the date
  -  &, | : boolean operators (& = and, | = or)

Negation of a constraint is noted `- constraint'.

Examples :

dbase.where (has ('author', 'me'))
dbase.where (has ('author', 'me') & - has ('title', 'failed'))

A search returns references on the entries that were found. It is then
possible to search these references to restrain the result.

For simple searches, you can use the function `search'

See also: search, references
""")

def has (field, value):
	return Search.Tester (field, value)

def has_key (value):
	return Search.KeyTester (value)

def any_has (value):
	return Search.AnyTester (value)

def has_type (value):
	the_type = Types.getentry (value, 0)
	if the_type is None:
		raise TypeError, "no such entry type"
	
	return Search.TypeTester (the_type)

def before (field, year, month = None, day = None):
	return Search.DateTester (field, Fields.Date ((year, month, day)))

def after (field, year, month = None, day = None):
	return - Search.DateTester (field, Fields.Date ((year, month, day)))


Help.register ('search',"""
Usage: search (database, request)

request is a string like:

	author = weig & title = time
""")


def _split_req (req):
	test = None
	
	list = map (string.strip, string.split (req, '|'))
	if len (list) > 1:
		for e in list:
			if test == None:
				test = _split_req (e)
			else:
				test = test | _split_req (e)
		return test
	
	list = map (string.strip, string.split (req, '&'))
	if len (list) > 1:
		for e in list:
			if test == None:
				test = _split_req (e)
			else:
				test = test & _split_req (e)
		return test

	list = map (string.strip, string.split (req, '!='))
	if len (list) > 2:
		raise SyntaxError, 'invalid test'

	if len (list) == 2:
		return - Search.Tester (string.lower (string.strip (list [0])),
				      string.strip (list [1]))


	list = map (string.strip, string.split (req, '='))
	if len (list) > 2:
		raise SyntaxError, 'invalid test'

	if len (list) == 2:
		return Search.Tester (string.lower (string.strip (list [0])),
				      string.strip (list [1]))

	for e in Types.SearchedFields:
		if test == None:
			test = Search.Tester (string.lower (e),
					      string.strip (list [0]))
		else:
			test = test | Search.Tester (string.lower (e),
						   string.strip (list [0]))

	return test


def search (base, req):
	t = _split_req (req)
	return base.where (t)



# ----- Generic reference holder -----

Help.register ('ref',"""
Syntax : reference = ref (base, [entries])

This function returns a reference object (like .where () method) on
the specified database (eventually restricted to a list of entry
names).
""")

def ref (base, list = None):
	ref = Base.Reference ()

	if list == None:
		ref.add (base)
	else:
		if type (list) is ListType:
			ref.add (base, list)
		else:
			ref.add (base, [ list ])
	return ref


# ----- Display -----

def pager_handle (inpager):
	if inpager:
		pagername = 'more'
	
		if os.environ.has_key ('PAGER'):
			pagername = os.environ ['PAGER']

		pager = os.popen (pagername, 'w')
	else:
		pager = sys.stdout

	return pager


Help.register ('more', """
Syntax: more (references, [pager])

Display references in BibTeX format. If nopager is 0, the entries are
sent to stdout instead of a pager.
""")

def more (refs, inpager = 1):
	"Output entries"

	try:
		bibwrite (refs, pager_handle (inpager))
		
	except IOError:
		print "warning: broken pipe"
		

Help.register ('ls', """
Syntax: ls (references, [pager])

Display only title/author and identifier for each entry.

See also : more, less
""")

def ls (refs, inpager = 1):
	"Output entries"

	def printer (entry, arg):
		title  = 'no title'
		author = 'no author'

		if entry.has_key ('title'):  title  = str (entry ['title'])
		if entry.has_key ('author'): author = str (entry ['author'])

		title  = title [0:34]
		author = author [0:24]
		name   = str (entry.key.key) [0:15]
		
		arg.write ('%-35s %-25s [%-16s]\n' % (title, author, name))


	try:
		refs.foreach (printer, pager_handle (inpager))
	except IOError:
		print "warning: broken pipe"


# ---------- Format ----------

Help.register ('format', """
Syntax : format (database, style, output_format, [filehandle], [id])

This function formats a database according to the given style and
output format. The formatted database is sent to stdout or
[filehandle] if specified.

See also: available ()
""")


available = Autoload.available

Help.register ('available', """
Syntax : list = available (category)

This function returns the list of available modules in a given
category.

Example:
	available ('style')
	available ('output')
	
""")

def format (database, style, output, file = sys.stdout, id = 'Bibliography'):
	
	style  = Autoload.get_by_name ("style",  style)
	output = Autoload.get_by_name ("output", output)

	formatter = output.data (file)
	style.data (id, formatter, database)

	return
