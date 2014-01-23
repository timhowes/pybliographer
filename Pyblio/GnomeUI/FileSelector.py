# This file is part of pybliographer
# 
# Copyright (C) 1998-2004 Frederic GOBRY
# Email : gobry@pybliographer.org
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
# along with this program; if not, see <http://www.gnu.org/licenses/>.
# 
# 

import string, os, urlparse
import gettext
_ = gettext.gettext

from gi.repository import Gtk, GObject, Gdk

from Pyblio import Open, Types, Base, Fields, Config, Autoload

from Pyblio.GnomeUI import Utils


class URLFileSelection (Gtk.FileChooserDialog):
    ''' Extended file selection dialog, with an URL field and a type
    selector. '''

    defaultdir = None
    
    def __init__(self, title = _("File"),
                 modal = True, has_auto = True, is_save = False,
                 directory = None, show_type=True):

        GObject.GObject.__init__ (self)

        accelerator = Gtk.AccelGroup ()
        self.add_accel_group (accelerator)

        b = self.add_button (Gtk.STOCK_OK, Gtk.ResponseType.OK)
        b.add_accelerator ('clicked', accelerator, Gdk.KEY_Return, 0, 0)

        b = self.add_button (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        b.add_accelerator ('clicked', accelerator, Gdk.KEY_Escape, 0, 0)

        if is_save:
            self.set_action(Gtk.FileChooserAction.SAVE)

        self.set_local_only (False)

        self.set_title (title)
        
        if directory:
            self.set_current_folder (directory)
            
        elif self.defaultdir:
            self.set_current_folder (self.defaultdir)
        
            
        self.ret = None
	self.ftype = None
	
	if show_type:
	    # type selector
	    hbox = Gtk.HBox ()
	    hbox.set_spacing (5)
	    hbox.set_border_width (5)
	    hbox.pack_start (Gtk.Label(label=_("Bibliography type:")),
			     expand=False, fill=False, padding=False)

	    self.menu = Gtk.ComboBoxText ()

	    hbox.pack_start (self.menu, False, False, False)

	    self.set_extra_widget (hbox)

	    # menu content

	    liste = Autoload.available ('format')
	    liste.sort ()

	    self.formats = []

	    if has_auto:
		self.menu.append_text (_(' - According to file suffix - '))
		self.ftype = None
                self.formats.append(None)
                
	    else:
		self.ftype = liste [0]

	    for avail in liste:
		self.menu.append_text (avail)

	    self.formats += liste

	    self.menu.set_active (0)
	    self.menu.connect ("changed", self.menu_select)

	    hbox.show_all ()
        return


    def menu_select (self, widget):
        self.ftype = self.formats [widget.get_active ()]
        return
        

    def run (self):
        ret = Gtk.FileChooserDialog.run (self)

        file = self.get_filename ()
        self.destroy ()

        if ret != Gtk.ResponseType.OK: return (None, None)
        
        URLFileSelection.defaultdir = os.path.dirname (file)
            
        return (file, self.ftype)

            

