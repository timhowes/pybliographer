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

''' This module overrides the standard error so that all problems get
redirected to a GnomeDialog '''

import sys
from gnome.ui import *
from gtk import *

import gettext
_ = gettext.gettext

class ErrorHandler:
    def __init__ (self):
        self.stderr = sys.stderr
        
        self.w = GnomeDialog (_("Internal Error"), STOCK_BUTTON_CLOSE)

        self.w.button_connect (0, self.close_window)
        self.w.set_close (TRUE)
        self.w.close_hides (TRUE)
        self.w.set_usize (500, 300)
        
        self.text = GtkText ()
    
        holder = GtkScrolledWindow ()
        holder.set_policy (POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        holder.add (self.text)
    
        self.w.vbox.pack_start (holder)

        self.shown = FALSE
        return

    def close_window (self, * arg):
        self.text.delete_text (0, -1)
        self.shown = FALSE
        return

    def write (self, text):
        self.stderr.write (text)
        self.text.insert_defaults (text)

        if not self.shown: 
            self.shown = TRUE
            self.w.show_all ()
        return
    
    def flush (self):
        self.stderr.flush ()
        return

    def close (self):
        return

sys.stderr = ErrorHandler ()
