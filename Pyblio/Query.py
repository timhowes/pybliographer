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

"""
Search a keyword in a medline database

This code has been contributed by: John Vu <jvu001@umaryland.edu>
"""

import urllib, sys, re, string

query_url = 'http://www.ncbi.nlm.nih.gov/entrez/utils/pmqty.fcgi'
fetch_url = 'http://www.ncbi.nlm.nih.gov/entrez/utils/pmfetch.fcgi'


def query_info (searchterm,displaynum):
    params = urllib.urlencode ({
        'db': 'pubmed',
        'term' : searchterm,  # searchterm is user inputted text
        'dopt' : 'd',
	'dispmax' : displaynum
        })
    f = urllib.urlopen ("%s?%s" % (query_url, params))
    uids = []
    in_body = 0
    uid_re = re.compile (r'^([\d]+)<br>')

    while 1:
        line = f.readline ()
        if line == '': break

        if in_body:
            line = string.strip (string.lower (line))

            if line == '</body>': break

            ret = uid_re.match (line)
            if not ret:
                print "unknown line: %s" % line
                continue

            uids.append (int (ret.group (1)))
        else:
            line = string.strip (string.lower (line))

            if line == '<body>':
                in_body = 1
                continue

    f.close ()
    return uids


def medline_query (keyword, maxcount):

    uids = query_info (keyword, maxcount)
    
    uids = string.replace (str(uids),'[','') # get rid of open bracket in string
    uids = string.replace (str(uids),']','') # get rid of close bracket in the string
    uids = string.replace (str(uids),' ','') # get rid of all the spaces in the string

    params = urllib.urlencode ({
        'db'     : 'pubmed',
        'report' : 'medline',
        'mode'   : 'text'
        })

    return "%s?%s&id=%s" % (fetch_url, params, str(uids))

