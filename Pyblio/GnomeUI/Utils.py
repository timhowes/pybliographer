# This file is part of pybliographer
# 
# Copyright (C) 1998 Frederic GOBRY
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

from Pyblio import Config

import gettext
_ = gettext.gettext


tooltips = GtkTooltips ()

if Config.get ('gnomeui/tooltips').data:
    tooltips.enable ()
else:
    tooltips.disable ()

cursor = {}
cursor ['clock']  = cursor_new (150)
cursor ['normal'] = cursor_new (68)

def set_cursor (self, name):
    if not Config.get ('gnomeui/threads').data: return

    self.get_window ().set_cursor (cursor [name])
        
    # not necessary with Gtk+-1.2.5
    # threads_leave ()
    
    while events_pending ():
        mainiteration (FALSE)
    
    # not necessary with Gtk+-1.2.5
    # threads_enter ()
    return

def popup_add (menu, item, action = None, argument = None):
    ''' Helper to add a new menu entry '''
    
    tmp = GtkMenuItem (item)
    if action:
        tmp.connect ('activate', action, argument)
    
    tmp.show ()
    menu.append (tmp)
    
    return tmp

def error_dialog (title, err):
    dialog = GnomeDialog (title, STOCK_BUTTON_CLOSE)
    dialog.button_connect (1, GnomeDialog.close)
    dialog.set_usize (500, 300)
            
    text = GtkText ()
    text.insert_defaults (_("The following errors occured:\n\n"))
    text.insert (None, color ['red'], None, str (err))
    
    holder = GtkScrolledWindow ()
    holder.set_policy (POLICY_AUTOMATIC, POLICY_AUTOMATIC)
    holder.add (text)
    
    dialog.vbox.pack_start (holder)
    
    dialog.show_all ()
    dialog.run_and_close ()
    return

color = {}

def init_colors (colormap):
    color [' colormap '] = colormap
    
    color ['red']  = colormap.alloc ('red')
    color ['blue'] = colormap.alloc ('blue')
    return


