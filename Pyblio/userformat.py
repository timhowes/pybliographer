# This file is part of pybliographer
# 
# Copyright (C) 2002 Peter Schulte-Stracke
# Email : Peter.Schulte-Stracke@t-online.de
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

"""This module contains the simple formatting routines.
""" 

import string

def getitem(item, field):
    if item.has_key(field): return item[field]
    else: return None

def make_paragraph(list, n=50):
    """Breaks a list of lines into a list of lines fitting
    into a line of at most n characters"""
    return list



def simple_combined_format_1 (item):
    """Returns a string containing combined person and title fields."""

    t = []
    x = getitem(item, 'author') or getitem(item, 'editor')
    if x: t = [str(x), ': ']
    x = getitem(item, 'title') or getitem(item, 'booktitle')
    t.append(str(x))
    return string.join(t,'')


simple_combined_format = simple_combined_format_1

def simple_untagged_format_1 (item, width=65):
    """Returns multiple lines containing an untagged formatted entry"""

    l= []

    

    return make_paragraph(l)

simple_untagged_format = simple_untagged_format_1

recoding = {'ä': 'ae',
            'ö': 'oe',
            'ü': 'ue',
            'ß': 'ss',}

def simple_filing_string (item):
    s = simple_combined_format_1(item)
    s = string.lower(s)
    t = []
    for i in s:
        if recoding.has_key(i):
            t.append(recoding[i]) 
        else:
            t.append(i)
    return string.join(t,'')


#simple_combined_format = simple_filing_string
