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

import _recode, string, re

class std_recode:
    def __init__ (self, req):
        self.request = _recode.request ('latin1..' + req)
        return
    
    def __call__ (self, text):
        if text is None: return None
        
        return _recode.recode (self.request, text)


abi_re = re.compile ('[<>\x80-\xff]')

class abi_recode:

    def abi_replacer (self, match):
        c = match.group (0)
        if c == '<': return '&lt;'
        if c == '>': return '&gt;'
        
        return '&#x%x;' % ord (c)

    def __call__ (self, text):
        if text is None: return None

        return re.sub (abi_re, self.abi_replacer, text)


def recode (format):
    if string.lower (format) == 'abiword':
        return abi_recode ()

    return std_recode (format)
