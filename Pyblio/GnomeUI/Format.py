# This file is part of pybliographer
# 
# Copyright (C) 1998-2003 Frederic GOBRY
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

''' Defines a Dialog to format a subset of entries as a bibliography '''

import gtk
from gnome import ui

import string, os

from Pyblio import Connector, version, Autoload
from Pyblio.GnomeUI import Utils


class FormatDialog (Connector.Publisher, Utils.GladeWindow):

    gladeinfo = { 'file': 'format.glade',
                  'root': '_w_format',
                  'name': 'format'
                  }
    
    def __init__ (self, parent = None):

        Utils.GladeWindow.__init__ (self, parent)

        return
    
        self.w = GnomeDialog (_("Format entries"),
                              STOCK_BUTTON_OK,
                              STOCK_BUTTON_CANCEL)
        
        if parent: self.w.set_parent (parent)
        
        self.w.set_close (0)
        self.w.close_hides (1)
        self.w.set_policy (TRUE, TRUE, FALSE)

        self.w.button_connect (0, self.apply)
        self.w.button_connect (1, self.close)

        h = GtkHBox (FALSE, 5)
        h.pack_start (GtkLabel (_("Bibliography style:")), FALSE, FALSE)
        self.file = GnomeFileEntry ('format', _("Select style"))
        self.file.set_default_path (os.path.join (version.prefix, 'Styles'))
        h.pack_start (self.file)
        self.w.vbox.pack_start (h, TRUE, FALSE)

        h = GtkHBox (FALSE, 5)
        h.pack_start (GtkLabel (_("Output format:")), FALSE, FALSE)
        self.menu = GtkOptionMenu ()
        h.pack_start (self.menu)
        self.w.vbox.pack_start (h, TRUE, FALSE)

        # menu content
        menu = GtkMenu ()
        self.menu.set_menu (menu)
        
        liste = Autoload.available ('output')
        liste.sort ()
        for avail in liste:
            Utils.popup_add (menu, avail, self.menu_select, avail)
        self.menu.set_history (0)
        self.menu_item = liste [0]
        
        h = GtkHBox (FALSE, 5)
        h.pack_start (GtkLabel (_("Output File:")), FALSE, FALSE)
        self.output = GnomeFileEntry ('output', _("Select output file"))
        h.pack_start (self.output)
        self.w.vbox.pack_start (h, TRUE, FALSE)
        
        self.w.show_all ()
        return


    def menu_select (self, menu, item):
        self.menu_item = item
        return
    

    def show (self):
        self._w_format.show ()
        return
    

    def apply (self, * arg):
        style  = self.file.get_full_path (FALSE)
        output = self.output.get_full_path (FALSE)
        format = Autoload.get_by_name ('output', self.menu_item).data

        if style is None or output is None: return
        self.issue ('format-query', style, format, output)
        
        self.w.close ()
        return
    

    def close (self, * arg):
        self.size_save ()
        self._w_format.close ()
        return
