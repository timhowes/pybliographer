# -*- coding: utf-8 -*-
# This file is part of pybliographer
# 
# Copyright (C) 1998-2004 Frederic GOBRY <gobry@pybliographer.org>
# Copyright (C) 2013 Germán Poo-Caamaño <gpoo@gnome.org>
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
# 


""" Symbol Definitions for Drag and Drop, Copy / Paste """

from gi.repository import Gdk

# Manipulate data as strings
STRING = 0
# Manipulate pickled keys
KEY    = 1
# Manipulate pickled entries
ENTRY  = 2

# Related string definitions
SYM_STRING = Gdk.atom_intern('STRING', False)
SYM_KEY    = Gdk.atom_intern('application/x-pyblio-key', False)
SYM_ENTRY  = Gdk.atom_intern('application/x-pyblio-entry', False)
SYM_APP    = Gdk.atom_intern('application/x-pybliographic', False)
SYM_TEXT   = Gdk.atom_intern('text/plain', False)
