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


""" This module implements a simple custom style """

import string, re
from Pyblio import Autoload, Config, Types
from Pyblio.Style import Utils

def writer (id, fmt, database):

    fmt.start_group (id)

    user_fmt = Config.get ("style/custom").data

    match = re.compile ("%\((\w+)\)")
    
    pos   = 0
    res   = 1

    requested = []
    
    while res:
        res = match.search (user_fmt, pos)
        
        if res:
            pos = res.end (1)
            requested.append (string.lower (res.group (1)))

            
    def write_one (entry, fmt, user_fmt = user_fmt, requested = requested):

        # Write key
        # --------------------------------------------------
        fmt.start (key = entry.name, entry = entry)

        array = {}
        
        for k in requested:
            if entry.has_key (k):
                e = entry [k]
                t = Types.gettype (entry.type, k)
                
                if t == Types.TypeAuthor:
                    array [k] = Utils.author_desc (e, fmt.coding)
                elif t == Types.TypeDate:
                    array [k] = e.format (fmt.coding) [0]
                else:
                    array [k] = e.format (fmt.coding)
            else:
                array [k] = ''

        fmt.write (user_fmt % array)
        
        fmt.end ()
        return

    # write all the entries in the database
    database.foreach (write_one, fmt)

    fmt.end_group ()
    return


Autoload.register ('style', 'Custom', writer)
