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

WidgetText   = 0
WidgetEntry  = 1
WidgetAuthor = 2

class UIDescription:
    def __init__ (self, name, width, type):
        self.name  = name
        self.width = width
        self.type  = type
        return

    
FieldInfo = {
    'Author'  : (150, WidgetAuthor),
    'Editor'  : (150, WidgetAuthor),
    'Title'   : (200, WidgetText),
    'BookTitle' : (200, WidgetText),
    'Year'    : (50,  WidgetEntry),
    'Comment' : (50,  WidgetText),
    }


DefaultFieldWidth  = 150
DefaultFieldWidget = WidgetEntry
DefaultFieldList   = ('Author', 'Year', 'Title')


def fieldwidth (field):
    if FieldInfo.has_key (field):
        return FieldInfo [field] [0]
    else:
        return DefaultFieldWidth

def fieldwidget (field):
    if FieldInfo.has_key (field):
        
        return FieldInfo [field] [1]
    else:
        return DefaultFieldWidget

        
