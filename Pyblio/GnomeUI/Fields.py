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

''' This module provides Dialogs to configure the structure of the bibliography '''

from gtk import *
from gnome.ui import *

import string, gettext, re, copy

_ = gettext.gettext

from Pyblio import Config, Fields, Types
from Pyblio.GnomeUI import Utils

_typename = {
    Fields.AuthorGroup : 'Authors',
    Fields.Text        : 'Text',
    Fields.URL         : 'URL',
    Fields.Reference   : 'Reference',
    Fields.Date        : 'Date'
    }

class FieldsDialog:

    def __init__ (self, parent = None):
        self.w = GnomeDialog (_("Fields configuration"),
                              STOCK_BUTTON_APPLY,
                              STOCK_BUTTON_CANCEL)
        if parent: self.w.set_parent (parent)

        self.w.button_connect (0, self.apply)
        self.w.set_close (1)
        self.w.set_policy (TRUE, TRUE, FALSE)

        # content of the dialog
        scroll = GtkScrolledWindow ()
        scroll.set_policy (POLICY_NEVER, POLICY_AUTOMATIC)
        
        self.list = GtkCList (2, (_("Name"), _("Type")))
        self.list.set_column_auto_resize (0, TRUE)
        self.list.connect ('select_row', self.select_row)
        (width, height) = self.list.size_request ()
        self.list.set_usize (width, 4 * height)
        scroll.add (self.list)
        self.w.vbox.pack_start (scroll)
        
        table = GtkTable (2, 2)
        table.set_col_spacings (5)
        table.set_row_spacings (5)
        table.attach (GtkLabel (_("Name:")),
                      0, 1, 0, 1, xoptions = 0, yoptions = 0)
        table.attach (GtkLabel (_("Type:")),
                      0, 1, 1, 2, xoptions = 0, yoptions = 0)

        self.name = GtkEntry ()
        table.attach (self.name, 1, 2, 0, 1)

        self.menu = GtkOptionMenu ()
        menu = GtkMenu ()
        self.menu.set_menu (menu)
        
        self.menu_items = _typename.keys ()
        for item in self.menu_items:
            Utils.popup_add (menu, _typename [item], self.select_menu, item)
            
        self.menu.set_history (0)
        self.current_menu = self.menu_items [0]
        
        table.attach (self.menu, 1, 2, 1, 2)
        self.w.vbox.pack_start (table, FALSE, FALSE)

        bbox = GtkHButtonBox ()
        button = GtkButton (_("Set"))
        button.connect ('clicked', self.add_cb)
        bbox.add (button)
        button = GtkButton (_("Remove"))
        button.connect ('clicked', self.remove_cb)
        bbox.add (button)
        self.w.vbox.pack_start (bbox, FALSE, FALSE)


        # fill in list
        self.data = copy.copy (Config.get ('base/fields').data)
        keys = self.data.keys ()
        keys.sort ()
        for key in keys:
            item = self.data [key]
            self.list.append ((item.name, _typename [item.type]))
            self.list.set_row_data (self.list.rows - 1, item)
        
        self.w.show_all ()
        return


    def select_menu (self, w, data):
        self.current_menu = data
        return

        
    def set (self, data):
        self.list.freeze ()
        self.list.clear ()
        self.data = data
        keys = self.data.keys ()
        keys.sort ()
        for key in keys:
            item = self.data [key]
            self.list.append ((item.name, _typename [item.type]))
            self.list.set_row_data (self.list.rows - 1, item)
        self.list.thaw ()
        pass


    def get (self):
        return self.data


    def select_row (self, widget, row, col, event):
        item = self.list.get_row_data (row)
        self.name.set_text (item.name)
        self.menu.set_history (self.menu_items.index (item.type))
        self.current_menu = item.type
        return


    def apply (self, * arg):
        result = self.get ()
        
        Config.set ('base/fields', result)
        Config.save_user ({'base/fields' : result})
        return


    def add_cb (self, * arg):
        name = string.strip (self.name.get_text ())
        if name == '': return

        table = self.get ()
        field = Types.FieldDescription (name, self.current_menu)
        table [string.lower (name)] = field
        self.set (table)
        return


    def remove_cb (self, * arg):
        selection = self.list.selection
        if not selection: return

        selection = selection [0]
        item = self.list.get_row_data (selection)
        table = self.get ()
        del table [string.lower (item.name)]
        self.set (table)
        return


_status = (
    '',
    _("Mandatory"),
    _("Optional")
    )

class EntriesDialog:

    def __init__ (self, parent = None):
        self.w = GnomeDialog (_("Entries configuration"),
                              STOCK_BUTTON_APPLY,
                              STOCK_BUTTON_CANCEL)
        if parent: self.w.set_parent (parent)

        self.w.button_connect (0, self.apply)
        self.w.set_close (1)
        self.w.set_policy (TRUE, TRUE, FALSE)

        scroll = GtkScrolledWindow ()
        self.main = GtkCList (1, (_("Entry"),))
        self.main.connect ('select_row', self.select_main)
        (width, height) = self.main.size_request ()
        self.main.set_usize (width, 4 * height)
        scroll.add (self.main)
        self.w.vbox.pack_start (scroll)

        self.w.vbox.pack_start (GtkHSeparator ())

        self.name = GtkEntry ()
        h = GtkHBox (spacing = 5)
        h.pack_start (GtkLabel (_("Entry Name:")), FALSE, FALSE)
        h.pack_start (self.name)
        self.w.vbox.pack_start (h, FALSE, FALSE)
        
        scroll = GtkScrolledWindow ()
        self.choice = GtkCList (2, (_("Status"), _("Field")))
        (width, height) = self.choice.size_request ()
        self.choice.set_usize (width, 4 * height)
        self.choice.set_reorderable (TRUE)
        self.choice.set_selection_mode (SELECTION_BROWSE)
        self.choice.set_column_auto_resize (0, TRUE)
        self.choice.connect ('select_row', self.select_choice)
        scroll.add (self.choice)
        self.w.vbox.pack_start (scroll)

        bbox = GtkHButtonBox ()
        button = GtkButton (_("Set"))
        button.connect ('clicked', self.add_cb)
        bbox.add (button)
        button = GtkButton (_("Remove"))
        button.connect ('clicked', self.remove_cb)
        bbox.add (button)
        self.w.vbox.pack_start (bbox, FALSE, FALSE)

        self.entries = copy.copy (Config.get ('base/entries').data)
        self.update_main ()

        # fill the second list
        fields = Config.get ('base/fields').data
        keys = fields.keys ()
        keys.sort ()
        for key in keys:
            item = fields [key]
            self.choice.append ((_status [0], item.name))
            self.choice.set_row_data (self.choice.rows - 1,
                                      [item, 0])
            
        self.w.show_all ()
        return

    def select_main (self, w, row, col, event):
        item = self.entries [self.main.get_row_data (row)]
        self.name.set_text (item.name)

        self.update_choice (item.mandatory, item.optional)
        return


    def update_main (self):
        self.main.freeze ()
        self.main.clear ()
        keys = self.entries.keys ()
        keys.sort ()
        for key in keys:
            item = self.entries [key]
            self.main.append ((item.name,))
            self.main.set_row_data (self.main.rows - 1,
                                      key)
        self.main.thaw ()
        return
    
    def update_choice (self, mdt, opt):
        self.choice.freeze ()
        self.choice.clear ()

        fields = copy.copy (Config.get ('base/fields').data)

        text = _status [1]
        for item in mdt:
            self.choice.append ((text, item.name))
            self.choice.set_row_data (self.choice.rows - 1,
                                      [item, 1])
            del fields [string.lower (item.name)]
            
        text = _status [2]
        for item in opt:
            self.choice.append ((text, item.name))
            self.choice.set_row_data (self.choice.rows - 1,
                                      [item, 2])
            del fields [string.lower (item.name)]

        keys = fields.keys ()
        keys.sort ()
        text = _status [0]
        for key in keys:
            item = fields [key]
            self.choice.append ((text, item.name))
            self.choice.set_row_data (self.choice.rows - 1,
                                      [item, 0])

        self.choice.thaw ()
        return
    
    def select_choice (self, w, row, col, event):
        if col != 0: return
        
        item = self.choice.get_row_data (row)
        if item is None: return
        
        item [1] = (item [1] + 1) % 3
        self.choice.set_text (row, 0, _status [item [1]])
        return
    
    def apply (self, * arg):
        Config.set ('base/entries', self.entries)

        default  = string.lower (Config.get ('base/defaulttype').data.name)
        def_type = Config.get ('base/entries').data [default]
        
        Config.set ('base/defaulttype', def_type)
        
        Config.save_user ({'base/entries' : self.entries,
                           'base/defaulttype' : def_type})
        return

    def add_cb (self, * arg):
        name = string.strip (self.name.get_text ())
        if not name: return

        newentry = Types.EntryDescription (name)
        cat = [[], []]
        for i in range (self.choice.rows):
            item = self.choice.get_row_data (i)
            if item [1]:
                cat [item [1] - 1].append (item [0])

        newentry.mandatory = cat [0]
        newentry.optional  = cat [1]

        self.entries [string.lower (name)] = newentry
        self.update_main ()
        return

    def remove_cb (self, * arg):
        selection = self.main.selection
        if not selection: return
        selection = selection [0]

        del self.entries [self.main.get_row_data (selection)]
        self.update_main ()
        return
    
