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

from gtk import *
from gnome.ui import *

import string, gettext, re

_ = gettext.gettext

from Pyblio.GnomeUI import Utils
from Pyblio import Config

_map = string.maketrans ('\t\n', '  ')
_cpt = re.compile ('\s+')

class ConfigDialog:

    def __init__ (self, parent = None):

        tooltips = GtkTooltips ()
        tooltips.enable ()
        
        self.w = GnomePropertyBox ()
        self.w.set_parent (parent)
        self.w.set_title (_("Choose you preferences"))
        
        domains = Config.domains ()
        domains = map (lambda x: string.capitalize (x), domains)
        domains.sort ()
        
        for dom in domains:

            keys  = Config.keys_in_domain (string.lower (dom))
            table = GtkTable (len (keys), 2, FALSE)

            i = 0
            for item in keys:
                data  = Config.get (item)
                nice  = string.capitalize (string.split (item, '/') [1])
                label = GtkLabel (nice)
                desc  = data.description
                desc  = string.translate (desc, _map)
                desc  = _cpt.sub (' ', desc)

                table.attach (label, 0, 1, i, i + 1, xoptions = 0)
                if data.type is None or not hasattr (data, 'w'):
                    table.attach (GtkLabel (_("Not yet editable")),
                                  1, 2, i, i + 1)
                    i = i + 1
                    continue

                # Create the edition widget...
                
                i = i + 1
                
            self.w.append_page (table, GtkLabel (dom))
        
        self.w.show_all ()
        return
    
