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

# Extension module for BibTeX files

import _bibtex
import os, sys, tempfile, pwd, time, traceback, re, string, copy

from types import *
from Pyblio.Fields import *
from Pyblio import Base, Config, Autoload, Types
from Pyblio import Open, Key, Utils, Iterator, Exceptions

import gettext
_ = gettext.gettext


# this database is shared between all the unpickled entries
_unpickle_db = _bibtex.open_string ("<unpickled>", '', 0);

_fieldtype = {
    Text        : 0,
    Date        : 3,
    AuthorGroup : 1,
    URL         : 0,
    Reference   : 0,
    }

class BibTextField (Text):
    ''' This class overrides the basic Text class and provides
    a specific method to write the entries as latex code '''

    def __init__ (self, text, native):
	Text.__init__ (self, text)
	self.native = native
	return

    def format (self, fmt):

	if string.lower (fmt) == 'latex':
	    return self.native

	return Text.format (self, fmt)


class Entry (Base.Entry):
    ''' This class holds a BibTeX entry and keeps a reference on
    its parser '''

    id = 'BibTeX'

    def __init__ (self, key, fieldtype, content, parser, line):
	Base.Entry.__init__ (self, key, fieldtype, content)

	self.__text = {}
	self.parser = parser
        self.line   = line
        
	# Check for date fields
	datefields = Config.get ('bibtex/datefield').data
	convert    = Config.get ('bibtex/months').data

	for field in datefields.keys ():
	    (yearfield, monthfield) = datefields [field]
	    
	    # check if this entry provides a date field
	    if not self.type.has_key (field): continue
	    if not self.has_key (yearfield): continue

	    month = None
	    year  = int (self [yearfield].text)
	    del self [yearfield]

	    if self.has_key (monthfield):
		mt = _bibtex.get_native (self.dict [monthfield])

		if convert.has_key (mt):
		    month = convert [mt]
		    del self [monthfield]

	    self [field] = Date ((year, month, None))
	return


    def __delitem__ (self, key):
	# First, eventually remove from cache
	if self.__text.has_key (key):
	    del self.__text [key]

	del self.dict [key]
	return

    def __setitem__ (self, key, value):
	# First, set the cache for free
	self.__text [key] = (value, 0)

        # then, convert as bibtex.
        if isinstance (value, Reference):
            value = string.join (map (lambda item: item.key, value.list),
                                 ', ')
        
	self.dict [key] = _bibtex.reverse (_fieldtype [self.type (key)],
                                           value)
	return


    def __deepcopy__ (self, memo):
        # create a copy of each native field
        content = {}
        for field in self.dict.keys ():
            value = _bibtex.copy_field (self.dict [field])
            content [field] = value
            
        return Entry (copy.deepcopy (self.key, memo),
                      copy.deepcopy (self.type, memo),
                      content,
                      self.parser, self.line)


    def __getstate__ (self):
        # transform the entry in a non-bibtex entry (as we don't keep
        # the specific information anyway, like @String,...)
        content = {}
        for field in self.keys ():
            content [field] = self [field]

        return Base.Entry (self.key, self.type, content)


    def __setstate__ (self, state):
        self.dict   = {}
        self.type   = state.type
        self.key    = state.key
        self.__text = state.dict
        self.parser = _unpickle_db

        for field in state.dict.keys ():
            self [field] = state [field]
        return

    
    def get_latex (self, key):
	''' Returns latex part '''

	return _bibtex.get_latex (self.parser,
                                  self.dict [key],
                                  _fieldtype [self.type (key)])


    def field_and_loss (self, key):

	# look in the cache first
	if self.__text.has_key (key):
	    return self.__text [key]

	obj = self.dict [key]

	# search its declared type

	fieldtype = self.type (key)
	ret  = _bibtex.expand (self.parser, obj,
                               _fieldtype [fieldtype])
        
	if fieldtype == AuthorGroup:
	    # Author
	    val = AuthorGroup ()
	    for aut in ret [3]:
		val.append (Author (aut))

	elif fieldtype == Date:
	    # Date
	    val = Date ((ret [3], None, None))

	elif fieldtype == Text:
	    # Any other text
	    val = BibTextField (ret [2], self.get_latex (key))

        elif fieldtype == Reference:
            # a reference on the same database
            val = Reference (ret [2], self.key.base)
            
        else:
            # specific fields, like URL
            val = fieldtype (ret [2])
            
	self.__text [key] = (val, ret [1])

	return (val, ret [1])



class BibtexIterator (Iterator.Iterator):

    def __init__ (self, db, parser):
	self.db     = db
	self.parser = parser
	return

    def first (self):
	_bibtex.first (self.parser)
	return self.next ()

    def next (self):
	retval = _bibtex.next (self.parser)

	if retval == None: return None

	name, fieldtype, offset, line, object = retval

	key   = Key.Key (self.db, name)
	fieldtype  = Types.get_entry (fieldtype)
	entry = Entry (key, fieldtype, object, self.parser, line)

	return entry
	
		
class DataBase (Base.DataBase):

    id = 'BibTeX'

    def __init__ (self, basename):
	''' Initialisation '''

	Base.DataBase.__init__ (self, basename)
	self.__parsefile__ ()
	return


    def __parsefile__ (self):
	self.dict   = {}

	# Ouvrir le fichier associe
	self.parser = _bibtex.open_file (Open.url_to_local (self.key),
					 Config.get ('bibtex/strict').data)

	# Incorporer les definitions de l'utilisateur
	if not Config.get ('bibtex/override').data:
	    user = Config.get ('bibtex/macros').data
	    valid = re.compile ('^\w+$')

	    for k in user.keys ():
		if not valid.match (k):
		    raise TypeError, _("key `%s' is malformed") % k

		_bibtex.set_string (self.parser, k,
				    _bibtex.reverse (_fieldtype [Text],
						     user [k] [0]))

	finished = 0
	errors = []

	# Creer la base de cles
	iter  = BibtexIterator (self, self.parser)

        while 1:
            # stay in the loop as long as we are on error
            try:
                entry = iter.first ()
            except IOError, err:
                errors.append (str (err))
                continue

            break

	while entry:
	    if self.dict.has_key (entry.key):
		errors.append (_("%s:%d: key `%s' already defined") % (
			str (self.key), entry.line, entry.key.key))
	    else:
		self.dict [entry.key] = entry

            while 1:
                try:
                    entry = iter.next ()
                except IOError, err:
                    errors.append (str (err))
                    continue
                
                break


	if len (errors) > 0:
	    raise Exceptions.ParserError (errors)

	# Incorporer les definitions de l'utilisateur
	if Config.get ('bibtex/override').data:
	    user  = Config.get ('bibtex/macros').data
	    valid = re.compile ('^\w+$')

	    for k in user.keys ():
		if not valid.match (k):
		    raise TypeError, _("key `%s' is malformed") % k

		_bibtex.set_string (self.parser, k,
				    _bibtex.reverse (_fieldtype [Text],
						     user [k] [0]))
	return



    def __str__ (self):
	''' '''
	return '<BibTeX database `%s\' (%d entries)>' % \
	       (self.key, len (self))


    def get_native (self, key):
	''' Return the object in its native format '''

	stream = Utils.StringStream ()
	entry_write (self.dict [key], stream)

	return stream.text


    def set_native (self, value):
	''' Parse text in native format '''

	parser = _bibtex.open_string ("<set_native string>", value,
				      Config.get ('bibtex/strict').data)

	iter  = BibtexIterator (self, parser)

	entry = iter.first ()
	while entry:
	    # set the entry parser to the current one, so
	    # that we keep the current string definitions
	    entry.parser = self.parser

	    # store this new entry.
	    self.dict [entry.key] = entry

	    entry = iter.next ()

	return



# ==================================================

def _nativify (field, fieldtype):
    ''' private method to convert from field to native format '''

    obj = _bibtex.reverse (fieldtype, field)
    return _bibtex.get_native (obj)


def entry_write (entry, output):
    ''' Print a single entry as BiBTeX code '''

    native = isinstance (entry, Entry)

    tp = entry.type

    # write the type and key
    output.write ('@%s{%s,\n' % (tp.name, entry.key.key))

    # create a hash containing all the keys, to keep track
    # of those who have been already written
    dico = {}
    if native:
	# for a native type, we have to handle the special case of the dates
	datefields = Config.get ('bibtex/datefield').data
	convert    = Config.get ('bibtex/months').data

	# create the list of months
	monthlist  = range (0, 12)
	for key in convert.keys ():
	    monthlist [convert [key] - 1] = key

	# loop over all the fields
	for field in entry.keys ():
	    if datefields.has_key (field):
		# we are processing a date...
		date = entry [field]

		dico [datefields [field] [0]] = str (date.year)
		if date.month:
		    dico [datefields [field] [1]] = \
			 monthlist [date.month - 1]

	    else:
		# we are processing a normal entry
		dico [field] = _bibtex.get_native (entry.dict [field])

    else:
	for field in entry.keys ():
	    # convert the field in a bibtex form
	    fieldtype = _fieldtype [tp (field)]
	    dico [field] = _nativify (entry [field], fieldtype)


    # write according to the type order
    for f in tp.mandatory + tp.optional:

	# dico contains all the available fields
	field = string.lower (f.name)
	if not dico.has_key (field): continue

	output.write ('  %-14s = ' % f.name)
	output.write (Utils.format (dico [field],
				    75, 19, 19) [19:] + ',\n')
	del dico [field]

    for f in dico.keys ():
	output.write ('  %-14s = ' % f)
	output.write (Utils.format (dico [f],
				   75, 19, 19) [19:] + ',\n')

    output.write ('}\n\n')
    return


def writer (it, output):
    ''' Outputs all the items refered by the iterator <it> to the
    <stdout> stream '''

    # write header
    output.write ('% This file has been generated by Pybliographer\n\n')

    # locate the entries that belong to a BibTeX database
    header = {}
    entry  = it.first ()
    while entry:
        if isinstance (entry, Entry):
	    header [entry.key.base] = entry
	entry = it.next ()

    # write the string definitions corresponding to these entries
    if len (header) > 0:
	user = Config.get ('bibtex/macros').data

	for entry in header.values ():
	    # write the list of strings
	    dict = _bibtex.get_dict (entry.parser)
	    if len (dict.keys ()) == 0: continue

	    for k in dict.keys ():
		if not (user.has_key (k) and user [k][1] == 0):
		    output.write ('@String{ ')
		    value = _bibtex.get_native (dict [k])
		    output.write ('%s \t= %s' % (k, value))
		    output.write ('}\n')

	    output.write ('\n')

    # write all the entries
    entry = it.first ()
    while entry:
	entry_write (entry, output)
	entry = it.next ()

    return


def opener (url, check):
    ''' This methods returns a new BibTeX database given a URL '''

    base = None

    if (not check) or url.url [2] [-4:] == '.bib':
	base = DataBase (url)

    return base


def iterator (url):
    ''' This methods returns an iterator that will parse the
    database on the fly (useful for merging or to parse broken
    databases '''

    # Ouvrir le fichier associe
    parser = _bibtex.open_file (Open.url_to_local (self.key),
				Config.get ('bibtex/strict').data)

    # create a database to generate correct keys
    db = Base.DataBase (url)

    return BibtexIterator (db, parser)


Autoload.register ('format', 'BibTeX', {'open'  : opener,
					'write' : writer,
					'iter'  : iterator})

