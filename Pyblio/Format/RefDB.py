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

import string

from Pyblio import Base, Autoload, Open

""" This is a simple opener that reads a file containing references to
other databases (one per line) and returns a reference on this group
of databases """

def fileopen (entity, check):

    method, address, file, p, q, f = entity
    base = None
	
    if (not check) or (method == 'file' and file [-4:] == '.brf'):
        try:
            f = open (file, 'r')
        except IOError:
            f.close ()
            return None
        
        # read each line
        base = Base.Reference ()
        
        while 1:
            line = f.readline ()
            if line == '': break
            
            line = string.strip (line)
            
            if line == '': continue
            if line [0] == '#': continue
            
            base.add (Open.bibopen (line))
            
    return base


Autoload.register ('format', 'RefDB', {'open' : fileopen })

