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

import string, os, urlparse, gettext

_ = gettext.gettext

from gnome.ui import *
from gnome import config

from gtk import *
import GtkExtra, GDK, GTK

from Pyblio import Open, Types, Base, Fields, Config, Autoload

from Pyblio.GnomeUI import Utils

class URLFileSelection (GtkFileSelection):
    ''' Extended file selection dialog, with an URL field and a type
    selector. '''
    
    def __init__(self, title = _("File"),
                 url=TRUE, modal=TRUE, has_auto=TRUE, path=None,
                 bibpath=None,  directory = None):
        
        GtkFileSelection.__init__(self)
        self.set_title (title)
        self.hide_fileop_buttons ()
        
        self.connect('destroy', self.quit)
        self.connect('delete_event', self.quit)
        self.cancel_button.connect('clicked', self.quit)
        self.ok_button.connect('clicked', self.ok_cb)

        
        if directory: self.set_filename (directory)
        elif path: self.set_filename(path[0])
        
        if modal:     grab_add (self)

        self.ret = None
        self.url = None
        self.path = path
        self.bibpath = bibpath

        vbox = self.main_vbox
        
        # path handler
        if path or bibpath:
            hbox = GtkHBox ()
            hbox.set_spacing (5)
            hbox.pack_start (GtkLabel ('Path:'), expand = FALSE, fill = FALSE)
            self.path_m = GtkOptionMenu()
            hbox.pack_start (self.path_m)
            vbox.pack_start (hbox, expand = FALSE, fill = FALSE)
            menu =  GtkMenu ()
            self.path_m.set_menu (menu)
            start_at = None
            if bibpath:
                for i in bibpath:
                    sel = os.path.isdir(os.path.expanduser(i))
                    Utils.popup_add(menu, i, self.path_select, i,
                                    sensitive=sel)
                    start_at = start_at or (sel and i)
            if path:
                for i in path:
                    sel = os.path.isdir(os.path.expanduser(i))
                    Utils.popup_add(menu, i, self.path_select, i,
                                    sensitive=sel)
                    start_at = start_at or (sel and i)

            self.set_filename(start_at+'/')
            menu.show()
            self.path_m.set_history (0)

        # url handler
        if url:
            hbox = GtkHBox ()
            hbox.set_spacing (5)
            hbox.pack_start (GtkLabel ('URL:'), expand = FALSE, fill = FALSE)
            self.url = GtkEntry ()
            hbox.pack_start (self.url)
            vbox.pack_start (hbox, expand = FALSE, fill = FALSE)

        # type selector
        hbox = GtkHBox ()
        hbox.set_spacing (5)
        hbox.pack_start (GtkLabel (_("Bibliography type:")),
                         expand = FALSE, fill = FALSE)
        self.menu = GtkOptionMenu ()
        hbox.pack_start (self.menu)
        vbox.pack_start (hbox, expand = FALSE, fill = FALSE)

        # menu content
        menu = GtkMenu ()
        self.menu.set_menu (menu)
        
        liste = Autoload.available ('format')
        liste.sort ()
        
        if has_auto:
            Utils.popup_add (menu, ' - Auto - ', self.menu_select, None)
            self.type = None
        else:
            self.type = liste [0]
            
        for avail in liste:
            Utils.popup_add (menu, avail, self.menu_select, avail)

        self.menu.set_history (0)
        return

    def menu_select (self, widget, selection):
        self.type = selection
        return
        
    def path_select (self, widget, selection):
        self.set_filename(selection+'/')
        return
        
    def quit (self, *args):
        self.hide()
        self.destroy()
        mainquit()
        return
    
    def ok_cb (self, b):
        self.ret = self.get_filename()
        
        if self.ret [-1] == '/':
            if self.url:
                ret = self.url.get_text ()
                
                if ret == '':
                    self.ret = None
                    return
                
                # construct a nice URL
                if string.lower (ret [0:5]) != 'http:' and \
                   string.lower (ret [0:4]) != 'ftp:':
                    
                    if ret [0:2] != '//':
                        ret = '//' + ret
                        
                    ret = 'http:' + ret

                self.ret = ret
            else:
                self.ret = None
        
        self.quit()
        return
    
    def run (self):
        self.show_all ()
        mainloop ()

        return (self.ret, self.type)

