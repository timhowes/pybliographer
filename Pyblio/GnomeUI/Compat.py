# This file is part of pybliographer
# 
# Copyright (C) 2005 Peter Schulte-Stracke
# Email : mail@schulte-stracke.de
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
from gi.repository import Gtk

# gnome-python (2.x)
#try:
#    from gnome.ui import gnome_error_dialog_parented
#except ImportError:
#    from gnome.ui import error_dialog_parented as gnome_error_dialog_parented
#
#error_dialog_parented = gnome_error_dialog_parented
# error_dialog_parented = str

class error_dialog_parented(Gtk.Dialog):
    def __init__(self, message, parent):
        Gtk.Dialog.__init__(self, _("Error"), parent, 0,
                            (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE))
        label = Gtk.Label(message)
        box = self.get_content_area()
        box.add(label)
        self.show_all()


# gnome-python (2.x)
#try:
#    import gnomevfs
#except ImportError:
#    import gnome.vfs as gnomevfs

#get_mime_type = gnomevfs.get_mime_type
get_mime_type = str


# Local Variables:
# coding: "latin-1"
# py-master-file: "ut_compat.py"
# End:
