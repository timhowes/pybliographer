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

''' Defines a Dialog to open URL '''

from gi.repository import GObject
from gi.repository import Gtk

import string, os

from Pyblio import Connector, Autoload
from Pyblio.GnomeUI import Utils


class OpenDialog (Connector.Publisher, Utils.GladeWindow):

    """ Class implementing the Open Location dialog """

    gladeinfo = { 'file': 'openurl.ui',
                  'root': '_w_openurl',
                  'name': 'openurl'
                  }

    def __init__(self, parent=None, has_auto=True):

        Utils.GladeWindow.__init__(self, parent)

        liststore = Gtk.ListStore(GObject.TYPE_STRING)
        menu = self._w_combobox
        menu.set_model(liststore)
        cell = Gtk.CellRendererText()
        menu.pack_start(cell, True)
        menu.add_attribute(cell, 'text', 0)

        liste = Autoload.available('format')
        liste.sort ()

        self.formats = [ None ]

        if has_auto:
            iter = liststore.append()
            liststore.set (iter, 0, _(' - According to file suffix - '))
            self.ftype = None
        else:
            self.ftype = liste[0]

        for avail in liste:
            iter = liststore.append()
            liststore.set(iter, 0, avail)

        self.formats += liste

        menu.set_active (0)
        menu.connect ("changed", self.menu_select)
        return


    def menu_select(self, widget):
        self.ftype = self.formats [widget.get_active()]
        return


    def run(self):
        ret = self._w_openurl.run()

        if ret != Gtk.ResponseType.OK:
            self._w_openurl.destroy()
            return (None, None)

        url = self._w_url.get_text()

        self._w_openurl.destroy()

        return (url, self.ftype)
