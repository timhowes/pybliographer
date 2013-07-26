# -*- coding: utf-8 -*-
# This file is part of pybliographer
# 
# Copyright (C) 2005 Peter Schulte-Stracke <mail@schulte-stracke.de>
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

"""
Compatability module 

 


"""
from gettext import gettext as _
from gi.repository import Gtk, Gio


class error_dialog_parented(Gtk.Dialog):
    def __init__(self, message, parent):
        Gtk.Dialog.__init__(self, _("Error"), parent, 0,
                            (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE))
        label = Gtk.Label(message)
        box = self.get_content_area()
        box.add(label)
        self.show_all()


get_mime_type = Gio.content_type_get_mime_type


# Local Variables:
# coding: "utf-8"
# py-master-file: "ut_compat.py"
# End:
