# This file is part of pybliographer
# 
# Copyright (C) 1998-2003 Frederic GOBRY
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

'''This module provides a dialog to configure the structure of the
bibliography '''

# TO DO:
# 

import gobject, gtk

import copy, gettext, os, re, string

_ = gettext.gettext

from Pyblio import Config, Fields, Types, version
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

        gp = os.path.join (version.prefix, 'glade', 'config1.glade')
        
        self.xml = gtk.glade.XML (gp, 'fields1')
        self.xml.signal_autoconnect (self)

        self.dialog = self.xml.get_widget ('fields1')
        self.w = self.xml.get_widget ('dialog-vbox')

        tooltips = gtk.Tooltips ()
        tooltips.enable ()
        
        #self.dialog.set_parent (parent) ####
        self.dialog.set_title (_("Entry types and field names configuration"))
        self.warning = 0
        self.parent = parent

        # content of the dialog  Page 1

        self.fields1 = self.xml.get_widget('f_list_1')
        rend = gtk.CellRendererText()
        col = gtk.TreeViewColumn(_('Name'), rend, text = 0)
        self.fields1.append_column(col)
        rend = gtk.CellRendererText()
        col = gtk.TreeViewColumn(_('Type'), rend, text = 1)
        self.fields1.append_column(col)
        
        self.fm = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING,
                                gobject.TYPE_PYOBJECT)
        self.fields1.set_model(self.fm)
        self.s1 = self.fields1.get_selection()
        self.s1.connect ('changed', self.list_1_select)
        data = copy.copy (Config.get ('base/fields').data)
        keys = data.keys ()
        keys.sort ()
        for item in [data[key] for key in keys]:
            self.fm.append((item.name, _(_typename [item.type]), item.type))

##         self.list.connect ('select_row', self.select_row)
##         (width, height) = self.list.size_request ()
##         self.list.set_usize (width, 4 * height)
        
        self.name1 = self.xml.get_widget('name1')
        self.menu = self.xml.get_widget('type1')
        menu = gtk.Menu ()
        self.menu.set_menu (menu)
        self.menu_items = _typename.keys ()
        for item in self.menu_items:
            Utils.popup_add (menu, _typename [item], self.select_menu, item)
        self.menu.set_history (0)
        self.current_menu = self.menu_items [0]

        self.show()

        self.changed = 0
        return

    def show(self):
        self.dialog.show_all ()

    def on_close (self, w):
        self.dialog.hide_all()

    def on_add(self, *args):
        t = self.menu_items[0]
        iter = self.fm.append(('new field', _(_typename[t]), t))
        if iter:
            path = self.fm.get_path (iter)
            self.fields1.scroll_to_cell(path)
            sel = self.fields1.get_selection()
            sel.select_iter(iter)
        
    def on_remove (self, *args):
        sel = self.fields1.get_selection()
        m, iter = sel.get_selected()
        if iter:
            m.remove(iter)

    def on_help (self, *args):
        print 'ON HELP:', args

    def list_1_select (self, sel):
        m, iter = sel.get_selected()
        print 'SELECT:', m, iter
        if iter:
            data = m[iter]
            self.name1.set_text(data[0])
            self.menu.set_history (self.menu_items.index(data[2]))

    def on_name1_changed (self, *args):
        sel = self.fields1.get_selection()
        m, iter = sel.get_selected()
        m[iter] [0] = self.name1.get_text()

    def on_type1_changed (self, *args):
        print 'TYP!', args
        x = self.menu_items[self.menu.get_history()]
        sel = self.fields1.get_selection()
        m, iter = sel.get_selected()
        if iter:
            m[iter] [1] = _(_typename[x])
            m[iter] [2] = x

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
        if not self.changed: return
        
        result = self.get ()
        
        Config.set ('base/fields', result)
        Config.save_user ({'base/fields' : result})

        if self.parent:
            self.parent.warning (_("Some changes require to restart Pybliographic\n"
                                   "to be correctly taken into account"))
        return


    def add_cb (self, * arg):
        name = string.strip (self.name.get_text ())
        if name == '': return

        table = self.get ()
        field = Types.FieldDescription (name, self.current_menu)
        table [string.lower (name)] = field
        self.set (table)

        self.changed = 1
        return


    def remove_cb (self, * arg):
        selection = self.list.selection
        if not selection: return

        selection = selection [0]
        item = self.list.get_row_data (selection)
        table = self.get ()
        del table [string.lower (item.name)]
        self.set (table)

        self.changed = 1
        return


_status = (
    '',
    _("Mandatory"),
    _("Optional")
    )

class EntriesDialog:

    def __init__ (self, parent = None):
        self.w = GnomeDialog (_("Entries configuration"),
                              gtk.STOCK_BUTTON_APPLY,
                              gtk.STOCK_BUTTON_CANCEL)
        if parent: self.w.set_parent (parent)
        self.parent = parent
        
        self.w.button_connect (0, self.apply)
        self.w.set_close (1)
        self.w.set_policy (True, True, False)

        scroll = gtk.ScrolledWindow ()
        self.main = gtk.CList (1, (_("Entry"),))
        self.main.connect ('select_row', self.select_main)
        (width, height) = self.main.size_request ()
        self.main.set_usize (width, 4 * height)
        scroll.add (self.main)
        self.w.vbox.pack_start (scroll)

        self.w.vbox.pack_start (gtk.HSeparator ())

        self.name = gtk.Entry ()
        h = gtk.HBox (spacing = 5)
        h.pack_start (gtk.Label (_("Entry Name:")), False, False)
        h.pack_start (self.name)
        self.w.vbox.pack_start (h, False, False)
        
        scroll = gtk.ScrolledWindow ()
        self.choice = gtk.CList (2, (_("Status"), _("Field")))
        (width, height) = self.choice.size_request ()
        self.choice.set_usize (width, 4 * height)
        self.choice.set_reorderable (True)
        self.choice.set_selection_mode (gtk.SELECTION_BROWSE)
        self.choice.set_column_auto_resize (0, True)
        self.choice.connect ('select_row', self.select_choice)
        scroll.add (self.choice)
        self.w.vbox.pack_start (scroll)

        bbox = gtk.HButtonBox ()
        button = gtk.Button (_("Set"))
        button.connect ('clicked', self.add_cb)
        bbox.add (button)
        button = gtk.Button (_("Remove"))
        button.connect ('clicked', self.remove_cb)
        bbox.add (button)
        self.w.vbox.pack_start (bbox, False, False)

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

        self.changed = 0
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
        if not self.changed: return
        
        Config.set ('base/entries', self.entries)

        default  = string.lower (Config.get ('base/defaulttype').data.name)
        def_type = Config.get ('base/entries').data [default]
        
        Config.set ('base/defaulttype', def_type)
        
        Config.save_user ({'base/entries' : self.entries,
                           'base/defaulttype' : def_type})

        if self.parent:
            self.parent.warning (_("Some changes require to restart Pybliographic\n"
                                   "to be correctly taken into account"))
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

        self.changed = 1
        return

    def remove_cb (self, * arg):
        selection = self.main.selection
        if not selection: return
        selection = selection [0]

        del self.entries [self.main.get_row_data (selection)]
        self.update_main ()

        self.changed = 1
        return
    
__fields_object = None
__entries_object = None

def run (w):
    global __fields_object
    if __fields_object:
        __fields_object.show()
    else:
        __fields_object = FieldsDialog(w)

def run_entries (w):
    global __entries_object
    if __entries_object:
        __entries_object.show()
    else:
        __entries_object = EntriesDialog(w)
