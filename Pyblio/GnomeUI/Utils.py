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

''' Useful functions for Gnome Interface '''

from gtk import *
from gnome.ui import *

from Pyblio import Config

import gettext
_ = gettext.gettext


cursor = {}
cursor ['clock']  = cursor_new (150)
cursor ['normal'] = cursor_new (68)

def set_cursor (self, name):

    window = self.get_window ()
    if not window: return
    
    window.set_cursor (cursor [name])
        
    while events_pending ():
        mainiteration (FALSE)
    return


def popup_add (menu, item, action = None, argument = None):
    ''' Helper to add a new menu entry '''
    
    tmp = GtkMenuItem (item)
    if action:
        tmp.connect ('activate', action, argument)
    
    tmp.show ()
    menu.append (tmp)
    
    return tmp


class TmpGnomeDialog (GtkDialog):

    def __init__ (self, title='', b1=None, b2=None, b3=None, b4=None,
                  b5=None, b6=None, b7=None, b8=None, b9=None, b10=None):

        self._o = GtkDialog ()._o
        
        self.set_title (title)
        self.vbox.set_spacing (5)
        self.vbox.set_border_width (5)

        self.connect ('delete_event', self._delete)
        
        self._b = []
        self._close = 1
        self._hides = 0
        
        self.append_buttons (b1,b2,b3,b4,b5,b6,b7,b8,b9,b10)
        return

    def _delete (self, * arg):
        self.close ()
        return 1

    def _clicked (self, * arg):
        if self._close: self.close ()
        return
    
    def set_parent(self, parent):
        self.set_transient_for (parent)
        return
        
    def button_connect(self, button, callback):
        b = self._b [button]
        b.connect ('clicked', callback)
        return
        
    def set_default(self, button):
        return

    def set_sensitive(self, button, setting):
        self._b [button].set_sensitive (setting)
        return
    
    def close (self):
        if self._hides:
            self.hide ()
        else:
            self.destroy ()
        return

    def close_hides (self, just_hide):
        self._hides = just_hide
        return
    
    def set_close (self, click_closes):
        self._close = click_closes
        return

    def editable_enters (self, editable):
        return

    def append_buttons (self, b1=None, b2=None, b3=None, b4=None, b5=None,
                        b6=None, b7=None, b8=None, b9=None, b10=None):
        buttons = filter(lambda x: x, (b1,b2,b3,b4,b5,b6,b7,b8,b9,b10))
        for b in buttons:
            self.append_button (b)
        return
    
    def append_button (self, name):
        button = GnomeStockButton (name)
        button.connect_after ('clicked', self._clicked)
        
        self._b.append (button)
        self.action_area.pack_start (button)
        return


def error_dialog (title, err, parent = None):
    dialog = TmpGnomeDialog (title, STOCK_BUTTON_CLOSE)
    dialog.set_close (TRUE)
    dialog.set_usize (500, 300)
    
    if parent:
        dialog.set_parent (parent)
        
    text = GtkText ()
    text.insert_defaults (_("The following errors occured:\n\n"))
    text.insert (None, color ['red'], None, str (err))
    
    holder = GtkScrolledWindow ()
    holder.set_policy (POLICY_AUTOMATIC, POLICY_AUTOMATIC)
    holder.add (text)
    
    dialog.vbox.pack_start (holder)
    
    dialog.show_all ()
    return

color = {}

def init_colors (colormap):
    if color: return
    
    color [' colormap '] = colormap
    
    color ['red']  = colormap.alloc ('red')
    color ['blue'] = colormap.alloc ('blue')
    return


class Callback:
    def __init__ (self, question, parent = None):
        self.ans = 0

        dialog = GnomeQuestionDialog (question, self.callback, parent = parent)
        dialog.connect ('delete_event', mainquit)
        return

    def answer (self):
        mainloop ()
        return self.ans

    def callback (self, button):
        self.ans = button == 0
        mainquit ()
        return


