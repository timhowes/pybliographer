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

# TO FIX
#
#  - spacing in the window

import string, os, urlparse, gettext

_ = gettext.gettext

from gnome.ui import *

from gtk import *

from Pyblio import Open, Types, Base, Fields, Config, Autoload

from Pyblio.GnomeUI import Utils


class URLFileSelection (FileSelection):
    ''' Extended file selection dialog, with an URL field and a type
    selector. '''
    
    def __init__(self, title = _("File"),
                 url=TRUE, modal=TRUE, has_auto=TRUE,
                 directory = None):
        
        FileSelection.__init__(self)
        self.set_title (title)
        self.hide_fileop_buttons ()
        
        self.connect('destroy', self.quit)
        self.connect('delete_event', self.quit)
        self.cancel_button.connect('clicked', self.quit)
        self.ok_button.connect('clicked', self.ok_cb)

        if directory: self.set_filename (directory)

        self.ret = None
        self.url = None
        
        vbox = self.main_vbox
        
        # url handler
        if url:
            hbox = HBox ()
            hbox.set_spacing (5)
            hbox.pack_start (Label ('URL:'), expand = FALSE, fill = FALSE)
            self.url = Entry ()
            hbox.pack_start (self.url)
            vbox.pack_start (hbox, expand = FALSE, fill = FALSE)

        # type selector
        hbox = HBox ()
        hbox.set_spacing (5)
        hbox.pack_start (Label (_("Bibliography type:")),
                         expand = FALSE, fill = FALSE)
        self.menu = OptionMenu ()
        hbox.pack_start (self.menu)
        vbox.pack_start (hbox, expand = FALSE, fill = FALSE)

        # menu content
        menu = Menu ()
        self.menu.set_menu (menu)
        
        liste = Autoload.available ('format')
        liste.sort ()
        
        if has_auto:
            Utils.popup_add (menu, ' - Auto - ', self.menu_select, None)
            self.ftype = None
        else:
            self.ftype = liste [0]
            
        for avail in liste:
            Utils.popup_add (menu, avail, self.menu_select, avail)

        self.menu.set_history (0)
        return

    def menu_select (self, widget, selection):
        self.ftype = selection
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

        return (self.ret, self.ftype)

