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

from Pyblio.QueryEngine import Engine
from Pyblio.Autoload import register

from Pyblio import Exceptions

import string, urllib, urlparse


class Spires (Engine):

    def __init__ (self, url, param):
        self.url = urlparse.urlparse (url)
        return

    def search (self, query, common):
        print query

        params = { 'FORMAT' : 'WWWBRIEFBIBTEX' }
        
        for k in ('topcit', 'j', 'SEQUENCE'):
            if not query [k]: continue
            
            params [k] = query [k]

        if query ['published']: params ['ps'] = 'yes'

        if query ['rpp']: params ['url'] = 'pdg-rpp'
        
        for q in query ['query']:
            params [q [0]] = q [2]

        if query ['eprint']:
            params ['eprint'] = '+' + query ['eprint']
            
        elif query ['eprint-num']:
            params ['eprint'] = query ['eprint-num']
            
        print params

        url = list (self.url)
        url [4] = urllib.urlencode (params)
        
        return urlparse.urlunparse (url).encode ('ascii'), 'bibtex'

    
    def cancel (self):
        self.running = 0
        return

    
register ('query', 'spires', Spires)
