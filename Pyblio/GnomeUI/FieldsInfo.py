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

from Pyblio import Config
import string

WidgetText   = 0
WidgetEntry  = 1
WidgetAuthor = 2
WidgetDate   = 3

class UIDescription:
    def __init__ (self, width, type):
        self.width = width
        self.type  = type
        return

def fieldinfo (field):
    ht = Config.get ('gnomeui/fields').data

    field = string.lower (field)
    
    if ht.has_key (field):
        return ht [field]
    else:
        return Config.get ('gnomeui/default').data

        
