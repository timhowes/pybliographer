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

from Pyblio.Base import *
import string, re
from gnome.ui import *
from gtk import *
import GTK

import gettext
_ = gettext.gettext

from Pyblio import Fields, Config, Base, Types

from Pyblio.GnomeUI import FieldsInfo, Utils


regular_field = re.compile ('^\w+$')
regular_id    = re.compile ('^\w[\d\w:_-]+$')


class NativeEditor (GtkDialog):
    ''' Implements a dialog that display a simple edition box for
    native entry '''
    
    def __init__ (self, entry, text = None):
        
        self.entry    = entry
        self.modified = None
        self.native   = None

        # do we have our own mainloop ?
        self.running  = 0
        
        GtkDialog.__init__ (self)

        self.set_title (_("Native editing of field `%s'") % entry.field)
        self.set_modal (TRUE)
        self.set_usize (400, 200)
        
        self.connect('delete_event', self.close)

        apply_b = GnomeStockButton (STOCK_BUTTON_APPLY)
        apply_b.connect ('clicked', self.apply)

        close_b = GnomeStockButton (STOCK_BUTTON_CANCEL)
        close_b.connect ('clicked', self.close)

        # Use Escape to abort, Ctrl-Return to accept
        acc = GtkAccelGroup ()
        self.add_accel_group (acc)

        close_b.add_accelerator ('clicked', acc, GDK.Escape, 0, 0)
        apply_b.add_accelerator ('clicked', acc, GDK.Return,
                                 GDK.CONTROL_MASK, 0)

        self.action_area.add (apply_b)
        self.action_area.add (close_b)
        
        apply_b.show ()
        close_b.show ()
        
        self.editor = GtkText ()
        self.editor.set_editable (TRUE)

        self.editor.connect ('key_press_event', self.key_handler,
                             apply_b)
        
        scrolled = GtkScrolledWindow ()
        scrolled.set_policy (POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        scrolled.add (self.editor)
        
        self.vbox.pack_start (scrolled)

        if text:
            self.original = text
            self.editor.insert_defaults (self.original)
        else:
            if self.entry.entry.has_key (self.entry.field):
                self.original = self.entry.entry.get_native (self.entry.field)
                self.editor.insert_defaults (self.original)
            else:
                self.original = None
            
        scrolled.show_all ()
        return

    def close (self, * arg):
        self.destroy ()
        if self.running: mainquit ()
        return

    def apply (self, * arg):
        text = self.editor.get_chars (0, -1)
        
        try:
            self.native = text
            self.entry.entry.set_native (self.entry.field, text)
        except IOError, msg:
            Utils.error_dialog ('Edition error', msg)
            return

        # get the text corresponding to the entry
        self.modified = self.entry.entry [self.entry.field]
        
        # reset the old version (we are not supposed to set it now)
        if self.original is not None:
            self.entry.entry.set_native (self.entry.field, self.original)
        else:
            del self.entry.entry [self.entry.field]
        
        self.destroy ()
        
        if self.running: mainquit ()
        return

    def key_handler (self, widget, ev, button):
        if ev.keyval == GDK.Return and \
           ev.state  == GDK.CONTROL_MASK:
            widget.emit_stop_by_name ('key_press_event')
            button.emit ('clicked')
        return 1
    
    def run_and_close (self):
        self.show ()
        self.running = 1
        
        mainloop ()
        return self.modified


class BasicEditor (GtkHBox):
    def __init__ (self,
                  entry, field,
                  value = None, loss = 0, has_native = 1):

        ''' Edit a given field in a given Entry. It is possible to specify
        the current aspect of the edition box '''
        
        GtkHBox.__init__ (self, FALSE, 5)

        self.entry = entry
        self.field = string.lower (field)
        self.name  = field
        
        self.editable = 1

        # natively modified ?
        self.modified = 0
        # store the eventual native field
        self.native   = None

        # internal variable to avoid modification notice during self.fill ()
        self.__in_fill = 0

        # Note the previous value of the field
        if entry.has_key (self.field) and \
           entry.is_personal (self.field):
            
            self.value, loss = entry.text (self.field)
        else:
            self.value, loss = None, 0
            
        # add native editor if we have the native property
        if has_native:
            if loss:
                icon = GnomeStock (STOCK_BUTTON_CANCEL)
            else:
                icon = GnomeStock (STOCK_BUTTON_APPLY)
            
            self.button = GtkButton ()
            self.button.add (icon)
            self.button.connect ('clicked', self.edit_native)
        
            Utils.tooltips.set_tip (self.button,
                                    _("Edit the field in its Native format"))
        
            self.pack_end (self.button, FALSE, FALSE)
            
        self.show_all ()

        return

    def modified_cb (self, * arg):
        ''' called when the textual entry is modified. This discards the
        native editing '''
        
        if not self.__in_fill:
            self.modified = 0
            
        return
    
    def set_editable (self, val):
        ''' make the entry field editable or not '''
        
        self.editor.set_editable (val)
        self.button.set_sensitive (val)
        
        self.editable = val
        return
        
    def edit_native (self, * arg):
        n = NativeEditor (self, self.native)
        
        # was the entry modified ?
        text = n.run_and_close ()
        
        if text is not None:
            # display the modified text
            self.fill (text)

            self.modified = 1
            self.native   = n.native
        return
    
    
    def fill (self, text = None):
        ''' Fill the field with a given Field value '''
        
        self.__in_fill = 1

        if text is None:
            text = self.value
        
        if text is None:
            self.editor.set_text ('')
        else:
            self.editor.set_text (str (text))

        self.__in_fill = 0
        return

    
    def update (self):
        ''' Update the real entry according to the modifications '''

        # entry not editable -> nothing to update
        if not self.editable: return 0
        
        # entry has been natively modified
        if self.modified:
            self.entry.set_native (self.field, self.native)
            return 1

        new = self.get ()

        if (new is None and self.value is not None) or \
           (new is not None and self.value is None) or \
           new != self.value:
            
            if new:
                self.entry [self.field] = new
            else:
                # remove empty entries
                del self.entry [self.field]

            return 1
        
        return 0


    def key_handler (self, widget, ev, button):
        if ev.keyval == GDK.Return and \
           ev.state  == GDK.CONTROL_MASK:
            widget.emit_stop_by_name ('key_press_event')
            button [0].emit ('clicked')
            return 1
        if ev.keyval == GDK.Tab and \
           ev.state  == GDK.CONTROL_MASK:
            widget.emit_stop_by_name ('key_press_event')
            button [1].emit ('clicked')
        return 1


    def get (self):
        ''' Create a Field from the edition box '''
        
        text = string.strip (self.editor.get_text ())
        
        if text == '': return None
        
        return Fields.Text (text)

    
class TextEditor (BasicEditor):
    
    def __init__ (self, entry, field, apply_b,
                  value = None, loss = 0, has_native = 1):
        
        BasicEditor.__init__ (self, entry, field, value, loss, has_native)
        
        scrolled = GtkScrolledWindow ()
        scrolled.set_policy (POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        
        self.editor = GtkText ()
        self.editor.set_editable (TRUE)
        self.editor.set_usize (300,100)
        self.editor.set_word_wrap (1)
        self.editor.connect ('changed', self.modified_cb)
        
        self.editor.connect ('key_press_event', self.key_handler,
                             apply_b)

        scrolled.add (self.editor)
        self.pack_start (scrolled, TRUE, TRUE)
        
        self.fill (value)
        return

    
    def fill (self, text = None):
        if text is None:
            text = self.value
        
        self.editor.freeze ()
        self.editor.delete_text (0, -1)

        if text is not None:
            self.editor.insert_defaults (str (text))
            
        self.editor.thaw ()
        return

    def get (self):
        text = self.editor.get_chars (0,-1)
        if text == '': return None

        return Fields.Text (text)
    

class AuthorEditor (BasicEditor):
    
    def __init__ (self, entry, field, apply_b,
                  value = None, loss = 0, has_native = 1):
        
        BasicEditor.__init__ (self, entry, field, value, loss, has_native)

        scrolled = GtkScrolledWindow ()
        scrolled.set_policy (POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        
        self.editor = GtkText ()
        self.editor.connect ('changed', self.modified_cb)
        self.editor.set_editable (TRUE) 
        self.editor.set_word_wrap (1)
        self.editor.set_usize (300,100)
        
        self.editor.connect ('key_press_event', self.key_handler,
                             apply_b)

        scrolled.add (self.editor)
        self.pack_start (scrolled, TRUE, TRUE)
        self.fill (value)
        return

    def fill (self, text = None):
        def str_auth (auth):
            if auth.last is None: return ''
            
            if auth.first:
                ret = auth.last + ', ' + auth.first
            else:
                ret = auth.last

            if auth.lineage: ret = ret + ' ' + auth.lineage

            return ret

        if text is None:
            text = self.value
        
        self.editor.freeze ()
        self.editor.delete_text (0, -1)
        
        if text is not None:
            self.editor.insert_defaults (join (map (str_auth, text), '\n'))
            
        self.editor.thaw ()
        return

    def get (self):
        text = string.strip (self.editor.get_chars (0,-1))
        
        autg = Fields.AuthorGroup ()
        for line in string.split (text, '\n'):
            line = string.strip (line)
            if line == '': continue
            
            autg.append (Fields.Author (line, strict = 1))

        if len (autg) == 0: return None
        return autg

    
class FieldEditor (BasicEditor):
    
    def __init__ (self, entry, field, apply_b,
                  value = None, loss = 0, has_native = 1):
        
        BasicEditor.__init__ (self, entry, field, value, loss, has_native)
        
        self.editor = GtkEntry ()
        self.editor.connect ('key_press_event', self.key_handler,
                             apply_b)
        self.editor.connect ('changed', self.modified_cb)
        self.editor.set_editable (TRUE)
        self.pack_start (self.editor, TRUE, TRUE)
        self.fill (value)
        return



class DateEditor (BasicEditor):
    
    def __init__ (self, entry, field, apply_b,
                  value = None, loss = 0, has_native = 1):
        
        BasicEditor.__init__ (self, entry, field, value, loss, has_native)
        
        self.editor = GtkEntry ()
        self.editor.connect ('key_press_event', self.key_handler,
                             apply_b)
        self.editor.connect ('changed', self.modified_cb)
        self.editor.set_editable (TRUE)
        self.pack_start (self.editor, TRUE, TRUE)
        self.fill (value)
        return

    def get (self):
        text = string.strip (self.editor.get_text ())
        if text == '': return None

        return Fields.Date (text)
    
class FieldGroup:
    def __init__ (self, order = []):
        self.dict  = {}
        self.order = order
        return

    def __getitem__ (self, key):
        return self.dict [key]

    def __setitem__ (self, key, value):
        self.dict [key] = value
        return

    def keys (self):
        return self.dict.keys ()
    
    def __len__ (self):
        return len (self.dict.keys ())

    def has_key (self, key):
        return self.dict.has_key (key)

    def update (self):
        changed = 0
        
        for k in self.dict.keys ():
            changed = self [k].update () or changed
            
        return changed
    
    def as_table (self):
        table = GtkTable (len (self), 2)
        
        table.set_border_width (5)
        table.set_row_spacings (5)
        table.set_col_spacings (5)
            
        kt = self.dict.keys ()
        
        row = 0
        for k in self.order:
            
            lc = string.lower (k.name)
            if not self.has_key (lc): continue

            kt.remove (lc)
            entry = self [lc]

            tmp = GtkLabel (k.name)
            table.attach (tmp, 0, 1, row, row + 1)
            tmp.show ()

            table.attach (entry, 1, 2, row, row + 1)
            entry.show ()

            row = row + 1

        for k in kt:

            entry = self [k]

            tmp = GtkLabel (k)
            table.attach (tmp, 0, 1, row, row + 1, 0)
            tmp.show ()

            table.attach (entry, 1, 2, row, row + 1)
            entry.show ()

            row = row + 1

        table.show_all ()
        return table
    
    
class Entry (GtkVBox):
    ''' Entry displayer '''
    
    def __init__ (self, entry, apply_b, properties, database):
        GtkVBox.__init__ (self, FALSE)

        self.entry       = entry
        self.properties  = properties
        self.changed     = 0
        self.database    = database
        self.apply_b     = apply_b
        self.extra_keys  = []
        
        ent = entry.type

        table = GtkTable (2, 2)
        table.set_border_width (5)
        table.set_row_spacings (5)
        table.set_col_spacings (5)
        
        self.pack_start (table, FALSE, FALSE)
        
        table.attach (GtkLabel ('Type'), 0, 1, 0, 1)
        table.attach (GtkLabel ('Identifier'), 1, 2, 0, 1)

        self.name = GtkEntry ()
        self.name.show ()
        
        if self.has_property ('change_type'):
            self.type = GtkOptionMenu ()
            available = map (lambda x: x.name,
                             Config.get ('base/entries').data.values ())
            available.sort ()
            
            menu = GtkMenu ()
            self.type.set_menu (menu)
            
            for avail in available:
                Utils.popup_add (menu, avail, self.type_changed, avail)

            self.type.set_history (available.index (ent.name))
        else:
            self.type = GtkEntry ()
            self.type.set_text (ent.name)
            self.type.set_editable (FALSE)

        self.name.set_text (entry.key.key)

        if not self.has_property ('change_id'):
            self.name.set_editable (FALSE)

        table.attach (self.type, 0, 1, 1, 2)
        table.attach (self.name, 1, 2, 1, 2)
            
        table.show_all ()

        if self.has_property ('crossref'):
            # crossref handling
            box = GtkHBox (FALSE, 5)
            box.set_border_width (5)

            box.pack_start (GtkLabel ('Cross-Reference:'), fill = FALSE,
                            expand = FALSE)
            
            self.crossref = GtkEntry ()
            self.crossref.set_editable (FALSE)
            Utils.tooltips.set_tip (self.crossref,
                                    _("Drag an Entry to define a Cross-Reference"))
            
            box.pack_start (self.crossref)

            button = GtkButton ()
            button.add (GnomeStock (STOCK_BUTTON_CANCEL))
            button.connect ('clicked', self.remove_crossref)
            
            Utils.tooltips.set_tip (button,
                                    _("Remove the current Cross-Reference"))
            
            box.pack_start (button, fill = FALSE, expand = FALSE)
            
            self.pack_start (box, fill=FALSE, expand=FALSE)

            # initialize the field
            if self.entry.crossref:
                self.crossref.set_text (str (self.entry.crossref.key.key))

            targets = [ ('application/x-pybkey', 0, 1) ]
            
            self.crossref.connect ('drag_data_received',
                                   self.dnd_drag_data_received)
            self.crossref.drag_dest_set(DEST_DEFAULT_ALL, targets,
                                        GDK.ACTION_COPY)

            box.show_all ()
            
        if self.has_property ('has_extra'):
            # extra field addition
            hbox   = GtkHBox (FALSE, 5)
            hbox.set_border_width (5)
            select = GnomeEntry ('extra-entry')
            hbox.pack_start (select)
            add_button = GtkButton (_("Add Extra Field"))
            hbox.pack_start (add_button)
            self.pack_start (hbox, fill=FALSE, expand=FALSE)

            add_button.connect ('clicked', self.extra_field, select)
            hbox.show_all ()
            
        # fill in the data for the notebook
        self.current_data = {}
        
        for k in self.entry.keys ():
            perso       = self.entry.is_personal (k)
            value, loss = self.entry.text (k)
            
            self.current_data [k] = [value, loss, perso]
            
        # Create the notebook
        self.create_notebook (ent)
        return

    def next_entry (self, * arg):
        n = self.notebook
        box = n.get_nth_page (n.get_current_page ())
        
        box.focus (GTK.DIR_DOWN)
        return
    
    def dnd_drag_data_received (self, w, context, x, y, data, info, time):
        name = data.data

        # remove the is_personal flag everywhere
        try:
            crossref = self.database [Base.Key (self.entry.key.base, name)]
        except KeyError:
            d = GnomeErrorDialog \
                (_("Cross-Reference `%s' is unexistent in the database") % cr)
            d.run_and_close ()
            return
        
        self.crossref.set_text (data.data)

        for k in crossref.keys ():
            # unless the entry already provides something, overwrite
            # the field
            
            if self.mandatory.has_key (k):
                value = self.mandatory [k].get ()
            elif self.optional.has_key (k):
                value = self.optional [k].get ()
            elif self.extra.has_key (k):
                value = self.extra [k].get ()
            else:
                value = None

            if value is None:
                value, loss = crossref.text (k)
                edit        = 0
            else:
                loss = 0
                edit = 1
                
            self.current_data [k] = (value, loss, edit)


        # Refresh the whole stuff
        self.remove (self.notebook)
        self.create_notebook (self.entry.type)
        return


    def remove_crossref (self, * arg):
        name = self.crossref.get_text ()
        
        try:
            crossref = self.database [Base.Key (self.entry.key.base, name)]
        except KeyError:
            d = GnomeErrorDialog \
                (_("Cross-Reference `%s' is unexistent in the database") % cr)
            d.run_and_close ()
            return

        # set the is_personal flag everywhere
        for k in crossref.keys ():
            if self.current_data.has_key (k):
                value, loss, edit = self.current_data [k]

            if not edit:
                self.current_data [k] = ['', 0, 1]

        self.crossref.set_text ('')

        # Refresh the whole stuff
        self.remove (self.notebook)
        self.create_notebook (self.entry.type)
        return
    
    def has_property (self, prop):
        ''' indicates if the database has a given property '''
		
        if self.properties.has_key (prop):
            return self.properties [prop]
        
        return 0


    def create_notebook (self, ent):
        
        # Notebook holding Mandatory/Optional fields
        self.notebook = GtkNotebook ()
        
        self.mandatory = FieldGroup (ent.mandatory)
        self.optional  = FieldGroup (ent.optional)
        self.extra     = FieldGroup ()

        native = self.has_property ('native')
        
        def get_field (entry, field, native = native, self = self):
            type = FieldsInfo.fieldinfo (field).type

            lc = string.lower (field)
            
            if self.current_data.has_key (lc):
                value, loss, perso = self.current_data [lc]
            else:
                value, loss, perso = None, 0, 1

            if type == FieldsInfo.WidgetText: 
                tmp = TextEditor (entry, field, self.apply_b,
                                  value, loss, native)

            elif type == FieldsInfo.WidgetEntry:
                tmp = FieldEditor (entry, field, self.apply_b,
                                   value, loss, native)

            elif type == FieldsInfo.WidgetAuthor:
                tmp = AuthorEditor (entry, field, self.apply_b,
                                    value, loss, native)

            elif type == FieldsInfo.WidgetDate:
                tmp = DateEditor (entry, field, self.apply_b,
                                  value, loss, native)

            else:
                tmp = TextEditor (entry, field, self.apply_b,
                                  value, loss, native)

            tmp.show ()

            if (value is not None) and not perso:
                # for cross-referenced fields
                tmp.set_editable (FALSE)
                
            return tmp
        
        dico = self.entry.keys () + self.extra_keys

        for f in ent.mandatory:
            lc = string.lower (f.name)
            self.mandatory [lc] = get_field (self.entry, f.name)
            if self.entry.has_key (lc): dico.remove (lc)
            
        for f in ent.optional:
            lc = string.lower (f.name)
            self.optional [lc] = get_field (self.entry, f.name)
            if self.entry.has_key (lc): dico.remove (lc)

        for lc in dico:
            self.extra [lc] = get_field (self.entry, lc)

        table = self.mandatory.as_table ()
        self.notebook.append_page (table, GtkLabel (_("Mandatory")))

        table = self.optional.as_table ()
        self.notebook.append_page (table, GtkLabel (_("Optional")))

        table = self.extra.as_table ()
        self.notebook.append_page (table, GtkLabel (_("Extra")))

        self.notebook.show_all ()
        self.pack_start (self.notebook)
        return

    def store_tmp_data (self):
        # get the changed values
        for k in self.mandatory.keys ():
            value       = self.mandatory [k].get ()

            if self.current_data.has_key (k):
                self.current_data [k] [0] = value
            else:
                self.current_data [k] = [value, 0, 1]

        for k in self.optional.keys ():
            value       = self.optional [k].get ()

            if self.current_data.has_key (k):
                self.current_data [k] [0] = value
            else:
                self.current_data [k] = [value, 0, 1]

        for k in self.extra.keys ():
            value       = self.extra [k].get ()

            if self.current_data.has_key (k):
                self.current_data [k] [0] = value
            else:
                self.current_data [k] = [value, 0, 1]

        return
    
    def type_changed (self, menu, type):
        type = Types.getentry (type)
        self.entry.type = type

        self.store_tmp_data ()
        
        # Refresh the whole stuff
        self.remove (self.notebook)
        self.create_notebook (type)

        self.changed = 1
        return

    def extra_field (self, button, widget):
        text = string.lower (string.strip (widget.gtk_entry ().get_text ()))
        
        if not regular_field.search (text):
            d = GnomeErrorDialog (_("Invalid field name `%s'") % text)
            d.run_and_close ()
            return

        if self.entry.has_key (text):
            d = GnomeErrorDialog (_("Key `%s' already defined") % text)
            d.run_and_close ()
            return
            
        self.extra_keys.append (text)

        self.store_tmp_data ()

        # Refresh the whole stuff
        self.remove (self.notebook)
        self.create_notebook (self.entry.type)
        self.changed = 1
        self.notebook.set_page (2)

        box = self.notebook.get_nth_page (2)
        box.focus (GTK.DIR_DOWN)
        return
    
class EntryDialog (GtkDialog):
    
    def __init__ (self, entry, database, callback = None, user = None):

        GtkDialog.__init__ (self)
        
        self.set_policy (TRUE, TRUE, TRUE)

        self.set_title ('Edit')
        self.connect('delete_event', self.close)

        self.database = database
        self.callback = callback
        self.user     = user
        
        apply_b = GnomeStockButton (STOCK_BUTTON_APPLY)
        apply_b.connect ('clicked', self.apply)
        apply_b.show ()
        
        close_b = GnomeStockButton (STOCK_BUTTON_CANCEL)
        close_b.connect ('clicked', self.close)
        close_b.show ()

        next_b = GtkButton ()
        self.vbox.pack_start (next_b)
        next_b.connect ('clicked', self.next_item)
        
        self.entry = Entry (entry, (apply_b, next_b),
                            database.properties, database)

        # Use Escape to abort, Ctrl-Return to accept
        acc = GtkAccelGroup ()
        self.add_accel_group (acc)

        close_b.add_accelerator ('clicked', acc, GDK.Escape, 0, 0)
        apply_b.add_accelerator ('clicked', acc, GDK.Return, GDK.CONTROL_MASK,
                                 0)

        self.action_area.add (apply_b)
        self.action_area.add (close_b)

        self.vbox.pack_start (self.entry)
        self.entry.show ()
        if self.entry.has_property ('change_id'):
            self.entry.name.grab_focus ()
        return

    def next_entry (self, widget, key, page):
        n = self.entry.notebook
        box = n.get_nth_page (arg)
        
        box.focus (GTK.DIR_DOWN)
        return

    def next_item (self, *arg):
        self.entry.focus (GTK.DIR_DOWN)
        return

    def apply (self, widget):
        # ask every entry to apply its changes
        changed = self.entry.changed
        
        changed = self.entry.mandatory.update () or changed
        changed = self.entry.optional.update ()  or changed
        changed = self.entry.extra.update ()     or changed

        # check the id
        id = string.strip (self.entry.name.get_text ())
        
        if not regular_id.search (id):
            d = GnomeErrorDialog (_("Invalid identifier `%s'") % id)
            d.run_and_close ()
            return
            
        elif id != self.entry.entry.key.key:

            key = Base.Key (self.entry.entry.key.base, id)
            
            # check unicity
            if not self.database.has_key (key):
                # set the new key and remove the previous one...
                
                if self.database.has_key (self.entry.entry.key):
                    # if this entry is not brand new...
                    # remove it !
                    del self.database [self.entry.entry.key]
                    
                self.entry.entry.key = key
                self.database [key] = self.entry.entry
                changed = 1
            else:
                d = GnomeErrorDialog (_("Identifier `%s' already exists") % id)
                d.run_and_close ()
                return

        # check the crossref
        cr = self.entry.crossref.get_text ()
        if cr == '': cr = None
        
        oldcr = self.entry.entry.crossref
        if oldcr: oldcr = oldcr.key

        if oldcr != cr:
            changed = 1
            
            if cr is None:
                # remove the previous crossref
                self.entry.entry.crossref = None
            else:
                # add a new crossref
                try:
                    self.entry.entry.crossref = self.database \
                                                [Base.Key
                                                 (self.entry.entry.key.base,
                                                  cr)]
                except KeyError:
                    d = GnomeErrorDialog (
                        _("Cross-Reference `%s' is unexistent in the database") % cr)
                    d.run_and_close ()
                    return
                
        if changed and self.callback:
            self.callback (self.entry.entry, self.user)
        
        self.destroy ()
        return
    
    def close (self, *arg):
        self.destroy ()
        return

