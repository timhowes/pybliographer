#! /usr/local/bin/pybliographer -q
# -*- python -*-
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

import string, sys, os, getopt

from Pyblio.Output import latexutils

from Pyblio import Base, Autoload

def usage ():
    sys.stderr.write ("usage: pybformat <style>:<output> [bibtexfiles...]\n")
    return

def error (text, exit = 1):
    sys.stderr.write ("pybformat: error: " + text + "\n")
    if exit:
        sys.exit (1)
    return

def warning (text, exit = 0):
    sys.stderr.write ("pybformat: warning: " + text + "\n")
    if exit:
        sys.exit (1)
    return

optlist, args = getopt.getopt (sys.argv [1:],
			       'H:F:o:l:vh',
			       ['header=',
				'footer=',
                                'output=',
                                'list=',
				'version',
				'help'])


header  = None
footer  = None
outfile = sys.stdout

for opt, value in optlist:
    if opt == '-H' or opt == '--header':
        header = value
        continue
    
    if opt == '-F' or opt == '--footer':
        footer = value
        continue

    if opt == '-o' or opt == '--output':
        try:
            outfile = open (value, 'w')
        except IOError, err:
            error ("can't open `%s': %s" % (value, err))
        continue

    if opt == '-l' or opt == '--list':
        try:
            list = Autoload.available (value)
        except KeyError:
            error ("unknown list `%s'" % value)
            
        if list:
            print "pybformat: available values for `%s':" % value
            print "  " + string.join (list, ", ")
            sys.exit (0)
        else:
            warning ("empty value list `%s'" % value)
            sys.exit (0)
            
    if opt == '-h' or opt == '--help':
        usage ()
        sys.exit (0)
        continue
    
    if opt == '-v' or opt == '--version':
        usage ()
        sys.exit (0)
        continue


# test input arguments
if len (args) < 2:
    # user gave wrong arguments...
    usage ()
    error ("too few arguments")


format = string.split (args [0], ":")
files  = args [1:]

if len (format) != 2:
    usage ()
    error ("illegal format specification")

# get the specified style and the output
style  = Autoload.get_by_name ("style",  format [0])
output = Autoload.get_by_name ("output", format [1])

if style is None:
    error ("unknown style `%s'\n" % format [0])

if output is None:
    error ("unknown output format `%s'" % format [1])

sys.stderr.write ("pybformat: using style `%s', format `%s'\n" \
                  % (style.name, output.name))

formatter = output.data (outfile)

# first, write the header
if header:
    try:
        h = open (header, 'r')
        line = '\n'
        while line:
            line = h.readline ()
            if line:
                outfile.write (line)
        h.close ()
    except IOError, err:
        error ("can't open header `%s': %s" % (header, err))


# write the data
for file in files:

    try:
        db = bibopen (file)
    except IOError, err:
        error ("can't open database: %s" % file)

    style.data ("Bibliography", formatter, db)
    
# last, write the footer
if footer:
    try:
        h = open (footer, 'r')
        line = '\n'
        while line:
            line = h.readline ()
            if line:
                outfile.write (line)
        h.close ()
    except IOError, err:
        error ("can't open footer `%s': %s" % (header, err))

        
outfile.close ()
