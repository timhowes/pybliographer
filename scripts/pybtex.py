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

import string, sys, os

from Pyblio.Output import latexutils

from Pyblio import Base, Autoload

def usage ():
    print """usage: pybtex <latexfile> [bibtexfiles...]"""
    return

# test input arguments
if len (sys.argv) < 2:
    # user gave wrong arguments...
    usage ()
    sys.exit (1)
    
latex  = sys.argv [1]
bibtex = sys.argv [2:]

# --------------------------------------------------
# Search the entries found in the LaTeX document
# --------------------------------------------------

entries, style, missing = latexutils.find_entries (latex, bibtex)

if missing:
    # warn the user that some entries were not found
    print "pybtex: warning: the following keys were not resolved"
    print "	" + string.join (missing, "\n	") + "\n"

if style is None:
    # If the LaTeX document declares no style...
    
    print "pybtex: error: no defined style"
    sys.exit (1)
    

# --------------------------------------------------
# generate the latex bibliography
# --------------------------------------------------

# open the .bbl file
bblfile = os.path.splitext (latex) [0] + '.bbl'
bbl = open (bblfile, 'w')

# Create a formatter that writes in the .bbl file
formatter = Autoload.get_by_name ('output', 'LaTeX').data (bbl)

# Ask the requested style to format the entries we read
Autoload.get_by_name ('style', style).data ('Test', formatter, entries)

bbl.close ()
