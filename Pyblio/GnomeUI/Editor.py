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
from gnome import config
from gtk import *
import GTK

import gettext, copy, re
_ = gettext.gettext

from Pyblio import Fields, Config, Base, Types, Connector, Exceptions, Key

from Pyblio.GnomeUI import FieldsInfo, Utils, Mime

key_re = re.compile ("^[\w:_+-]+$")

_newcontent = {
    Fields.AuthorGroup : _("Last Name, First Name"),
    Fields.Text        : _("Text"),
    Fields.URL         : 'http://',
    Fields.Date        : '2000',
    Fields.Reference   : _("Reference"),
    }


class BaseField (Connector.Publisher):
    ''' common class to each specialized field editor '''
    
    def __init__ (self, entry, field, content, j):

        self.w = GtkVBox ()

        h = GtkHBox (spacing = 5)
        self.w.pack_start (GtkLabel (field), FALSE, FALSE)

        field = string.lower (field)
        self.field = field

        self.setup (entry)

        self.edit = None
        expand = self.create_widget (h)
        
        if self.edit:
            self.edit.connect ('key_press_event', self.key_handler)
        
        if self.loss: h.pack_start (GnomeStock (STOCK_BUTTON_NO),
                                    FALSE, FALSE)
        else:         h.pack_start (GnomeStock (STOCK_BUTTON_YES),
                                    FALSE, FALSE)

        self.w.pack_start (h, expand, expand)
        self.w.show_all ()

        flag = 0
        if expand: flag = EXPAND | FILL
        content.attach (self.w, 0, 1, j, j + 1, yoptions = flag)
        return


    def key_handler (self, widget, ev):
        if ev.keyval == GDK.Return and \
           ev.state  == GDK.CONTROL_MASK:
            widget.emit_stop_by_name ('key_press_event')
            self.issue ('apply')
        
        elif ev.keyval == GDK.Tab and \
           ev.state  == GDK.CONTROL_MASK:
            widget.emit_stop_by_name ('key_press_event')
            self.issue ('next')

        return 1


    def setup (self, entry):
        if entry.has_key (self.field):
            (self.value, self.loss)  = entry.field_and_loss (self.field)
            self.string = str (self.value)
        else:
            (self.value, self.loss) = (None, 0)
            self.string = ''
        return

    
    def update (self, entry):
        text = string.strip (self.edit.get_chars (0, -1))

        if text == self.string: return 0

        if text == '':
            del entry [self.field]
            return 1

        self.update_content (entry, text)
        return 1
        

class TextBase (BaseField):
    ''' Virtual class common to Text and Entry '''

    def setup (self, entry):
        BaseField.setup (self, entry)

        if self.string and self.string [0] == '@':
            self.string = ' ' + self.string
        return

    
    def update (self, entry):
        text = string.rstrip (self.edit.get_chars (0, -1))
        if text == self.string: return 0

        if text == '':
            del entry [self.field]
            return 1

        self.update_content (entry, text)
        return 1


    def update_content (self, entry, text):
        if text [0] == '@' and hasattr (entry, 'set_native'):
            entry.set_native (self.field, string.lstrip (text [1:]))
            return

        text = string.lstrip (text)
        entry [self.field] = Fields.Text (text)
        return

    
class Entry (TextBase):

    def create_widget (self, h):
        if len (self.string) < 50:
            self.edit = GtkEntry ()
            self.edit.set_text (self.string)
            self.edit.set_editable (TRUE)
            self.edit.show ()
            
            h.pack_start (self.edit)
            return 0

        w = GtkScrolledWindow ()
        w.set_policy (GTK.POLICY_NEVER, GTK.POLICY_AUTOMATIC)
        self.edit = GtkText ()
        self.edit.set_editable (TRUE)
        self.edit.insert_defaults (self.string)
        self.edit.set_word_wrap (TRUE)
        self.edit.show ()
        
        w.add (self.edit)
        w.show ()
        
        h.pack_start (w)
        return 1


class Text (TextBase):
    
    def create_widget (self, h):
        w = GtkScrolledWindow ()
        w.set_policy (GTK.POLICY_NEVER, GTK.POLICY_AUTOMATIC)
        self.edit = GtkText ()
        self.edit.set_editable (TRUE)
        self.edit.insert_defaults (self.string)
        self.edit.set_word_wrap (TRUE)
        self.edit.show ()
        w.add (self.edit)
        w.show ()

        h.pack_start (w)
        return 1


class AuthorGroup (BaseField):
    
    def create_widget (self, h):
        w = GtkScrolledWindow ()
        w.set_policy (GTK.POLICY_NEVER, GTK.POLICY_AUTOMATIC)
        self.edit = GtkText ()
        self.edit.set_editable (TRUE)
        self.edit.set_word_wrap (TRUE)
        self.edit.insert_defaults (self.string)
        self.edit.show ()
        w.add (self.edit)
        w.show ()

        h.pack_start (w)
        return 1


    def setup (self, entry):
        if entry.has_key (self.field):
            (self.value, self.loss)  = entry.field_and_loss (self.field)
            names = map (str, self.value)
            self.string = string.join (names, '\n')
        else:
            (self.value, self.loss) = (None, 0)
            self.string = ''
            
        return
        

    def update_content (self, entry, text):
        group = Fields.AuthorGroup ()
        for author in string.split (text, '\n'):
            author = string.strip (author)
            if author == '': continue

            group.append (Fields.Author (author))
        
        entry [self.field] = group
        return


class Date (BaseField):
    
    def create_widget (self, h):
        hbox = GtkHBox (FALSE, 5)

        self.day = GtkEntry ()
        (width, height) = self.day.size_request ()
        self.day.set_usize (width / 4, height)
        self.day.set_max_length (2)
        self.day.connect ('key_press_event', self.key_handler)
        if self.initial [0]:
            self.day.set_text (str (self.initial [0]))
        hbox.pack_start (self.day)
        hbox.pack_start (GtkLabel (_("Day")), FALSE, FALSE)
        
        self.month = GtkEntry ()
        self.month.set_usize (width / 4, height)
        self.month.set_max_length (2)
        self.month.connect ('key_press_event', self.key_handler)
        if self.initial [1]:
            self.month.set_text (str (self.initial [1]))
        hbox.pack_start (self.month)
        hbox.pack_start (GtkLabel (_("Month")), FALSE, FALSE)
        
        self.year = GtkEntry ()
        self.year.set_max_length (4)
        self.year.set_usize (width / 3, height)
        self.year.connect ('key_press_event', self.key_handler)
        if self.initial [2]:
            self.year.set_text (str (self.initial [2]))
        hbox.pack_start (self.year)
        hbox.pack_start (GtkLabel (_("Year")), FALSE, FALSE)

        hbox.show_all ()
        h.pack_start (hbox)
        return 0


    def setup (self, entry):
        if entry.has_key (self.field):
            date = entry [self.field]
            self.initial = (date.day, date.month, date.year)
        else:
            self.initial = (None, None, None)
            
        self.loss = 0
        return

    
    def update (self, entry):
        (day, month, year) = (None, None, None)
        
        text = string.strip (self.day.get_chars (0, -1))
        if text != '':
            try: day = int (text)
            except ValueError:
                GnomeErrorDialog (_("Invalid day field in date"),
                                  self.day.get_toplevel ()).show ()
                return -1
        
        text = string.strip (self.month.get_chars (0, -1))
        if text != '':
            try: month = int (text)
            except ValueError, err:
                GnomeErrorDialog (_("Invalid month field in date"),
                                  self.day.get_toplevel ()).show ()
                return -1
        
        text = string.strip (self.year.get_chars (0, -1))
        if text != '':
            try: year = int (text)
            except ValueError: 
                GnomeErrorDialog (_("Invalid year field in date"),
                                  self.day.get_toplevel ()).show ()
                return -1
        
        if self.initial == (day, month, year): return 0

        if (day, month, year) == (None, None, None):
            del entry [self.field]
            return 1

        try:
            entry [self.field] = Fields.Date ((year, month, day))
        except Exceptions.DateError, error:
            GnomeErrorDialog (str (error),
                              self.day.get_toplevel ()).show ()
            return -1
        return 1


class Reference (BaseField):
    
    def create_widget (self, h):
        accept = (
            (Mime.KEY_TYPE,   0, Mime.KEY),
            )

        self.edit = GtkEntry ()
        self.edit.set_editable (FALSE)
        self.edit.set_text (self.string)
        self.edit.show ()
        self.edit.drag_dest_set (DEST_DEFAULT_MOTION |
                                 DEST_DEFAULT_HIGHLIGHT |
                                 DEST_DEFAULT_DROP,
                                 accept,
                                 GDK.ACTION_COPY)
        self.edit.connect ('drag_data_received', self.drag_received)
        self.current = None
        
        h.pack_start (self.edit)
        return 0

    def setup (self, entry):
        if entry.has_key (self.field):
            (self.value, self.loss)  = entry.field_and_loss (self.field)
            self.string = string.join (map (lambda x: x.key, self.value.list), ', ')
        else:
            (self.value, self.loss) = (None, 0)
            self.string = ''
        return
    
    def drag_received (self, *arg):
        selection = arg [4]
        info      = arg [5]

        if not info == Mime.KEY: return

        keys = string.split (selection.data, '\n')
        reflist = []
        for k in keys:
            (base, key) = string.split (k, '\0')
            reflist.append (Key.Key (base, key))

        self.current = Fields.Reference (reflist)
        
        text = string.join (map (lambda x: x.key, self.current.list), ', ')
        self.edit.set_text (text)
        return
    

    def update_content (self, entry, text):
        entry [self.field] = self.current
        return


class URL (BaseField):
    
    def create_widget (self, h):
        self.edit = GtkEntry ()
        self.edit.set_editable (TRUE)
        self.edit.set_text (self.string)
        self.edit.show ()

        h.pack_start (self.edit)
        return 0


    def update_content (self, entry, text):
        entry [self.field] = Fields.URL (text)
        return


class RealEditor (Connector.Publisher):
    ''' Edits in standard form '''

    def __init__ (self, database, entry):
        self.entry    = entry
        self.database = database
        self.type     = entry.type
        self.fields   = entry.keys ()

        self.fields.sort ()
        
        self.w = GtkVBox ()
        table  = GtkTable (2, 2)
        table.set_border_width (5)
        table.set_col_spacings (5)
        
        table.attach (GtkLabel (_("Entry type")),
                      0, 1, 0, 1, yoptions = 0)
        table.attach (GtkLabel (_("Key")),
                      1, 2, 0, 1, yoptions = 0)

        self.key = GtkEntry ()
        self.key.set_editable (TRUE)
        if self.entry.key:
            self.key.set_text (self.entry.key.key)
        
        table.attach (self.key,
                      1, 2, 1, 2, yoptions = 0)

        self.menu = GtkOptionMenu ()
        menu = GtkMenu ()
        self.menu.set_menu (menu)

        table.attach (self.menu,
                      0, 1, 1, 2, yoptions = 0)

        entry_list = Config.get ("base/entries").data.values ()
        entry_list.sort (lambda x, y: cmp (x.name, y.name))

        i = 0
        history = 0
        for entry in entry_list:
            if entry == self.entry.type: history = i
            Utils.popup_add (menu, entry.name,
                             self.menu_select, entry)
            i = i + 1

        self.menu.set_history (history)
        
        table.show_all ()
        self.w.pack_start (table, FALSE, FALSE)

        self.newfield_area = GtkHBox (spacing = 5)
        self.newfield_area.set_border_width (5)
        self.newfield = GnomeEntry ('newfield')
        self.newfield_area.pack_start (self.newfield)

        b = GtkButton (_("Create Field"))
        b.connect ('clicked', self.create_field)
        self.newfield_area.pack_start (b)
        self.newfield_area.show_all ()
        
        self.w.pack_start (self.newfield_area, FALSE, FALSE)
        
        # Notebook
        self.notebook = GtkNotebook ()
        self.notebook.show ()

        self.w.pack_start (self.notebook)
        self.w.show ()
        
        self.notebook_init = FALSE
        self.update_notebook ()
        return


    def menu_select (self, menu, entry):
        # update the current entry
        new = self.update (self.database, copy.deepcopy (self.entry))
        if new is None:
            entry_list = Config.get ("base/entries").data.values ()
            entry_list.sort (lambda x, y: cmp (x.name, y.name))
            self.menu.set_history (entry_list.index (self.entry.type))
            return
        else:
            new.type = entry
            
        self.entry = new
        self.update_notebook ()
        return


    def apply_cb (self, * arg):
        self.issue ('apply')
        return
        
    def next_cb (self, * arg):
        self.issue ('next')
        return

    
    def update_notebook (self):
        if self.notebook_init:
            for i in range (0, 3):
                self.notebook.remove_page (0)
        
        self.notebook_init = TRUE

        names  = (_("Mandatory"), _("Optional"), _("Extra"))
        fields = map (string.lower, self.entry.keys ())
        
        self.content = []
        for i in range (0, 3):
            label   = GtkLabel (names [i])

            if   i == 0: table = map (lambda x: x.name, self.entry.type.mandatory)
            elif i == 1: table = map (lambda x: x.name, self.entry.type.optional)
            else:        table = copy.copy (fields)

            if len (table) == 0: continue
            
            content = GtkTable (1, len (table))

            j = 0
            for field in table:
                lcfield = string.lower (field)

                try: fields.remove (lcfield)
                except ValueError: pass

                widget = FieldsInfo.widget (lcfield) (self.entry, field, content, j)
                self.content.append (widget)

                widget.Subscribe ('apply', self.apply_cb)
                widget.Subscribe ('next', self.next_cb)
                
                j = j + 1

            label.show ()
            content.show ()
            
            self.notebook.insert_page (content, label, i)
            
        self.notebook.show ()
        return


    def create_field (self, * arg):
        widget = self.newfield.gtk_entry ()
        text = string.strip (string.lower (widget.get_text ()))
        if text == '': return

        newtype = Types.get_field (text).type
        self.entry [text] = newtype (_newcontent [newtype])
        self.update_notebook ()
        return
    

    def update (self, database, entry):
        modified = FALSE
        
        key = string.strip (self.key.get_text ())
        if key == '':
            self.entry.key = None
            modified = TRUE
        else:
            if not key_re.match (key):
                GnomeErrorDialog (_("Invalid key format"),
                                  self.w.get_toplevel ())
                return None

            key = Key.Key (database, key)

            if key != self.entry.key:
                if database.has_key (key):
                    GnomeErrorDialog (_("Key `%s' already exists") % str (key.key),
                                      self.w.get_toplevel ())
                    return None
                
                self.entry.key = key
                modified = TRUE
                
        modified = self.type != self.entry.type or modified
        
        for item in self.content:
            result = item.update (self.entry)
            if result == -1: return None
            
            modified = result or modified

        if not modified:
            fields = self.entry.keys ()
            fields.sort ()

            if fields != self.fields: modified = 1
        
        if modified: return self.entry
        
        return entry
    
            
class NativeEditor (Connector.Publisher):
    ''' Composit widget to edit an entry in its native format '''

    def __init__ (self, database, entry):

        self.entry    = entry
        self.database = database
        if database.has_key (entry.key):
            self.original = database.get_native (entry.key)
        else:
            self.original = ''
        
        self.w = GtkText ()
        self.w.set_editable (TRUE)
        self.w.connect ('key_press_event', self.key_handler)
        
        self.w.insert (Config.get ('gnomeui/monospaced').data,
                       None, None, self.original)
        return


    def key_handler (self, widget, ev):
        if ev.keyval == GDK.Return and \
           ev.state  == GDK.CONTROL_MASK:
            widget.emit_stop_by_name ('key_press_event')
            self.issue ('apply')
        
        elif ev.keyval == GDK.Tab and \
           ev.state  == GDK.CONTROL_MASK:
            widget.emit_stop_by_name ('key_press_event')
            self.issue ('next')

        return 1


    def update (self, database, entry):
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
        
        self.w.set_policy (TRUE, TRUE, FALSE)
        self.w.set_title (_("Edit entry"))
        self.w.connect ('delete_event', self.close_dialog)

        # set window size
        ui_width  = config.get_int ('Pybliographic/Editor/Width=-1')
        ui_height = config.get_int ('Pybliographic/Editor/Height=-1')

        if ui_width != -1 and ui_height != -1:
            self.w.set_default_size (ui_width, ui_height)

        if parent: self.w.set_transient_for (parent)

        self.apply_b = GnomeStockButton (STOCK_BUTTON_APPLY)
        self.apply_b.connect ('clicked', self.apply_changes)
        self.apply_b.show ()

        # check if the database supports native editing
        self.has_native = hasattr (database, 'get_native')

        if self.has_native:
            self.native_b = GtkButton (_("Native Editing"))
            self.native_b.connect ('clicked', self.toggle_native)
            self.native_b.show ()
        
        self.close_b = GnomeStockButton (STOCK_BUTTON_CANCEL)
        self.close_b.connect ('clicked', self.close_dialog)
        self.close_b.show ()

        # Use Escape to abort, Ctrl-Return to accept
        accelerator = GtkAccelGroup ()
        self.w.add_accel_group (accelerator)

        self.close_b.add_accelerator ('clicked', accelerator, GDK.Escape, 0, 0)
        self.apply_b.add_accelerator ('clicked', accelerator, GDK.Return, GDK.CONTROL_MASK,
                                 0)

        self.w.action_area.add (self.apply_b)
        if self.has_native: self.w.action_area.add (self.native_b)
        self.w.action_area.add (self.close_b)

        self.entry       = entry
        self.database    = database
        self.editor      = None

        # put the negated value, so that we can call toggle to switch and create
        self.native_mode = not (self.has_native and
                                Config.get ('gnome/native-as-default').data)

        self.toggle_native ()
        
        self.w.show ()
        return


    def toggle_native (self, * arg):
        if self.native_mode:
            # real edition
            self.native_mode = FALSE
            if self.has_native:
                self.native_b.children () [0].set_text (_("Native Editing"))

            if self.editor: self.editor.w.destroy ()
            self.editor = RealEditor (self.database,
                                      copy.deepcopy (self.entry))
            self.editor.Subscribe ('apply', self.apply_changes)
            self.editor.Subscribe ('next',  self.next_item)
        
            self.w.vbox.pack_start (self.editor.w)
            self.editor.w.show ()
        else:
            # native edition
            self.native_mode = TRUE
            if self.has_native:
                self.native_b.children () [0].set_text (_("Standard Editing"))
            
            if self.editor: self.editor.w.destroy ()
            self.editor = NativeEditor (self.database,
                                        copy.deepcopy (self.entry))
            self.editor.Subscribe ('apply', self.apply_changes)
            self.editor.Subscribe ('next',  self.next_item)
        
            self.w.vbox.pack_start (self.editor.w)
            self.editor.w.show ()

        return

    
    def next_item (self, * arg):
        if self.native_mode: return
        
        n = self.editor.notebook
        box = n.get_nth_page (n.get_current_page ())
        
        box.focus (GTK.DIR_DOWN)
        pass


    def close_dialog (self, *arg):
        alloc = self.w.get_allocation ()
        config.set_int ('Pybliographic/Editor/Width',  alloc [2])
        config.set_int ('Pybliographic/Editor/Height', alloc [3])
        config.sync ()
        
        self.w.destroy ()
        return


    def apply_changes (self, * arg):
        new = self.editor.update (self.database, self.entry)
        if new:
            self.close_dialog ()
            if new is not self.entry:
                self.issue ('commit-edition', self.entry, new)
        return
    
