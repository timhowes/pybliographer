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


class Z3950 (Engine):

    def __init__ (self, url, param):
        self.url = urlparse.urlparse (url)
        return

    def search (self, query, common):
        print query
        return 0
    
    def cancel (self):
        self.running = 0
        return

    
register ('query', 'Z3950', Z3950)
