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

import string, re
from gnome.ui import *
from gtk import *

import gettext, copy
_ = gettext.gettext

from Pyblio import Fields, Config, Base, Types, Connector, Exceptions

from Pyblio.GnomeUI import FieldsInfo, Utils



class BaseField (Connector.Publisher):
    ''' common class to each specialized field editor '''
    
    def __init__ (self, entry, field):
        self.field = field
        
        if entry.has_key (field):
            self.value = entry [field]
        else:
            self.value = None
        return


class EntryField (BaseField):

    def __init__ (self, entry, field):
        EditionFieldBase.__init__ (self, field, value)

        self.w = GtkEntry ()
        self.w.set_editable (TRUE)

        self.original = ''
        
        if value:
            self.original = str (value)
            self.w.set_text (self.original)
            
        self.w.show ()
        return


    def update (self, entry):
        ''' updates the entry according to the current field value '''
        
        text = self.w.get_text ()
        if text == self.original: return
        
        if text:
            entry [self.field] = Fields.Text (text)
        else:
            del entry [self.field]
            
        return 1


class NativeEditor:
    def __init__ (self, database, entry):
        ''' Composit widget to edit an entry in its native format '''

        self.entry    = entry
        self.database = database
        self.original = database.get_native (entry.key)

        self.w = GtkText ()
        self.w.set_editable (TRUE)

        self.w.insert_defaults (self.original)
        return


    def update (self):
        ''' updates and returns the new entry '''
        new  = None

        try:
            new = self.database.create_native (self.w.get_chars (0, -1))
        except Exceptions.ParserError, error:
            Utils.error_dialog (_("Error in native string parsing"),
                                str (error))
        
        return new

    
class Editor (Connector.Publisher):
    
    def __init__ (self, database, entry, parent = None):

        self.w = GtkDialog ()
        
        self.w.set_policy (TRUE, TRUE, TRUE)
        self.w.set_title ('Edit')
        self.w.connect ('delete_event', self.close_dialog)

        if parent: self.w.set_transient_for (parent)

        apply_b = GnomeStockButton (STOCK_BUTTON_APPLY)
        apply_b.connect ('clicked', self.apply_changes)
        apply_b.show ()
        
        close_b = GnomeStockButton (STOCK_BUTTON_CANCEL)
        close_b.connect ('clicked', self.close_dialog)
        close_b.show ()

        # Use Escape to abort, Ctrl-Return to accept
        accelerator = GtkAccelGroup ()
        self.w.add_accel_group (accelerator)

        close_b.add_accelerator ('clicked', accelerator, GDK.Escape, 0, 0)
        apply_b.add_accelerator ('clicked', accelerator, GDK.Return, GDK.CONTROL_MASK,
                                 0)

        self.w.action_area.add (apply_b)
        self.w.action_area.add (close_b)

        # virtual button to jump to the next field
        next_b = GtkButton ()
        self.w.vbox.pack_start (next_b)
        next_b.connect ('clicked', self.next_item)

        self.entry  = entry
        self.editor = NativeEditor (database, copy.deepcopy (entry))

        self.w.vbox.pack_start (self.editor.w)
        self.editor.w.show ()
        self.w.show ()
        return


    def next_item (self, * arg):
        pass


    def close_dialog (self, *arg):
        self.w.destroy ()
        return


    def apply_changes (self, * arg):
        new = self.editor.update ()
        if new:
            self.issue ('commit-edition', self.entry, new)
            self.close_dialog ()
        return
    
