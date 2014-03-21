# -*- coding: utf-8 -*-
# This file is part of pybliographer
#
# Copyright (C) 1998-2004 Frederic GOBRY <gobry@pybliographer.org>
# Copyright (C) 2013 Germán Poo-Caamaño <gpoo@gnome.org>
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
#


# TO FIX
#
#  - DnD with the world
#  - Copy/Paste with the world

######################### UNICODE ############################


''' Main index containing the columned view of the entries '''

from Pyblio import Config, Connector, Fields, Resource
from Pyblio import Types, Sort, userformat, version

from gi.repository import GObject, Gtk, Gdk, GdkPixbuf, Pango

import os.path

from Pyblio.GnomeUI import FieldsInfo, Mime, Utils

from string import *

import cPickle

pickle = cPickle
del cPickle

_safechar = ['_'] * 256
for c in ascii_letters + digits:
    _safechar [ord (c)] = c

_safechar = ''.join (_safechar)

class Index (Connector.Publisher):
    ''' Graphical index of an iterator '''

    def __init__ (self, fields = None, popup = None):
        ''' Creates a new list of entries '''

        self._w_popup = popup

        fields = fields or Config.get ('gnome/columns').data
        self.fields = map (lower, fields)

        self.model = apply (Gtk.ListStore,
                            (GObject.TYPE_STRING,) * len (fields) + (GObject.TYPE_OBJECT,))

        self.list = Gtk.TreeView ()
        self.list.set_model (self.model)
        self.selinfo = self.list.get_selection ()
        self.selinfo.set_mode (Gtk.SelectionMode.MULTIPLE)

        i = 0
        self.gvpixbuf = GdkPixbuf.Pixbuf.new_from_file(
            os.path.join (version.pixmapsdir, 'pybliographic-viewer.png'))
        if True:
            rend = Gtk.CellRendererPixbuf ()
            col = Gtk.TreeViewColumn ('P', rend, pixbuf = len(fields))
            col.set_fixed_width (22)
            self.list.append_column (col)
            i += 1

        i, self.prefix_columns =  0, i

        for f in fields:
            renderer = Gtk.CellRendererText ()
            renderer.set_property ('ellipsize', Pango.EllipsizeMode.END)
            col = Gtk.TreeViewColumn (f, renderer, text=i)
            col.set_resizable (True)
            col.set_clickable (True)

            f = self.fields [i]
            f = f.translate (_safechar)

            k = '/apps/pybliographic/columns/%s' % f

            w = Utils.config.get_int (k)

            if w:
                col.set_sizing (Gtk.TreeViewColumnSizing.FIXED)
                col.set_fixed_width (w)
            col.connect ('clicked', self.click_column, i)

            self.list.append_column (col)
            i = i + 1

        self.w = Gtk.ScrolledWindow ()

        self.w.set_policy (Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.w.add (self.list)

        self.access = []

        # some events we want to react to...
        self.selinfo.connect ('changed', self.select_row)

        self.list.connect ('row-activated', self.entry_edit)
        self.list.connect ('button-press-event', self.button_press)

        # DnD configuration

        targets = (
            (Mime.SYM_KEY,    0, Mime.KEY),
            (Mime.SYM_ENTRY,  0, Mime.ENTRY),
            (Mime.SYM_STRING, 0, Mime.STRING),
            (Mime.SYM_TEXT  , 0, Mime.STRING),
            )

        accept = (
            (Mime.SYM_ENTRY,  0, Mime.ENTRY),
            )

        accept_list = Gtk.TargetList.new([])
        for drag_type, target_flags, info in accept:
            accept_list.add(drag_type, target_flags, info)

        # Port to Gtk3 required some changes because of bug
        # https://bugzilla.gnome.org/show_bug.cgi?id=680638
        self.list.enable_model_drag_dest([], Gdk.DragAction.COPY | Gdk.DragAction.MOVE)
        self.list.drag_dest_set_target_list(accept_list)
        self.list.connect ("drag_data_received", self.drag_received)


        targets_list = Gtk.TargetList.new([])
        for drag_type, target_flags, info in targets:
            targets_list.add(drag_type, target_flags, info)

        self.list.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK |
                                           Gdk.ModifierType.BUTTON3_MASK,
                                           [],
                                           Gdk.DragAction.COPY | Gdk.DragAction.MOVE)
        self.list.drag_source_set_target_list(targets_list)
        self.list.connect ('drag_data_get', self.dnd_drag_data_get)

        # Copy/Paste configuration

        self.selection_buffer = None

        self.list.connect ('selection_received', self.selection_received)
        self.list.connect ('selection_get', self.selection_get)
        self.list.connect ('selection_clear_event', self.selection_clear)

        # We handle three selections: one specific to the application,
        # the clipboard, and the primary. Therefore, we should be able
        # to paste into every kind of editor/application.
        Gtk.selection_add_target (self.list, Gdk.SELECTION_PRIMARY,
                                  Mime.SYM_STRING,
                                  Mime.STRING)
        Gtk.selection_add_target (self.list, Gdk.SELECTION_SECONDARY,
                                  Mime.SYM_STRING,
                                  Mime.STRING)
        Gtk.selection_add_target (self.list, Mime.SYM_APP,
                                  Mime.SYM_ENTRY,
                                  Mime.ENTRY)
        return


    def selection_clear (self, * arg):
        self.selection_buffer = None
        return


    def selection_received (self, widget, selection, info):
        data = selection.get_data()

        if not data: return

        entries = pickle.loads (data)
        self.issue ('drag-received', entries)
        return


    def selection_get (self, widget, selection, info, time):
        if not self.selection_buffer:
            return

        if info == Mime.ENTRY:

            text = pickle.dumps (self.selection_buffer)
            selection.set (Mime.SYM_ENTRY, 8, text)

        elif info == Mime.STRING:

            if Config.get ('gnome/paste-key').data:
                # if we want the keys, return the keys !
                keys = []
                for e in self.selection_buffer:
                    keys.append (str (e.key.key))
                text = join (keys, ',')
            else:
                # else, return the full entries
                text = join (map (str, self.selection_buffer), '\n\n')

            selection.set ("STRING", 8, text)

        return


    def selection_copy (self, entries):
        # Advertise the fact that we hold the selection
        Gtk.selection_owner_set(self.list, Mime.SYM_APP, Gdk.CURRENT_TIME)
        Gtk.selection_owner_set(self.list, Gdk.SELECTION_PRIMARY, Gdk.CURRENT_TIME)
        Gtk.selection_owner_set(self.list, Gdk.SELECTION_SECONDARY, Gdk.CURRENT_TIME)

        self.selection_buffer = entries
        return


    def selection_paste (self):
        # Request the selection as a full entry
        Gtk.selection_convert(self.list, Mime.SYM_APP, Mime.SYM_ENTRY,
                              Gdk.CURRENT_TIME)
        return


    def drag_received (self, widget, drag_context, x, y, selection,
                       info, timestamp, *args):
        if info == Mime.ENTRY:
            entries = pickle.loads(selection.get_data())
            self.issue('drag-received', entries)

        return


    def dnd_drag_data_get (self, list, context, selection, info, time):
        ''' send the selected entries as dnd data '''

        entries = self.selection()
        if not entries:
            return

        if info == Mime.STRING:
            if Config.get ('gnome/paste-key').data:
                # if we want the keys, return the keys !
                keys = []
                for e in entries:
                    keys.append (str (e.key.key))
                text = join (keys, ',')
            else:
                # else, return the full entries
                text = join (map (str, entries), '\n\n')

            selection.set(selection.get_target(), 8, text)
            return

        if info == Mime.KEY:
            # must return a set of keys
            data = join (map (lambda e: str (e.key.base or '') + '\0' +
                              str (e.key.key), entries), '\n')
            selection.set(selection.get_target(), 8, data)

        elif info == Mime.ENTRY:
            data = pickle.dumps (entries)
            selection.set(selection.get_target(), 8, data)

        else:
            return

        if context.get_suggested_action() == Gdk.DragAction.MOVE:
            self.issue('drag-moved', entries)

        return

    # --------------------------------------------------

    def __len__ (self):
        ''' returns the number of lines in the current index '''

        return len (self.access)


    def get_item_position (self, item):
        try:
            return self.access.index (item)
        except ValueError:
            return -1


    def select_item (self, item):
        if type (item) is not type (1):
            item = self.get_item_position (item)

        if item == -1 or item >= len (self.access):
            return

        path = (item,)

        self.selinfo.select_path (path)
        self.list.scroll_to_cell (path)

        self.issue ('select-entry', self.access [item])
        return


    def set_scroll (self, item):
        if type (item) is not type (1):
            item = self.get_item_position (item)

        if item == -1:
            return

        self.list.scroll_to_cell ((item,),
                                  use_align = True,
                                  row_align = .5)
        return


    def display (self, iterator):

        # clear the access table
        self.access = []

        #Utils.set_cursor (self.w, 'clock')

        self.model.clear ()

        for entry in iterator:
            row = []
            i = 0

            for f in self.fields:
                text = ''

                if f == '-key-':
                    text = str(entry.key.key).decode('latin-1')

                elif f == '-type-':
                    text = str(entry.type.name)

                elif f == '-author/editor-':
                    text = userformat.author_editor_format(entry).decode ('latin-1')

                elif f == '-author/title-':
                    text = userformat.author_title_format(entry).decode ('latin-1')

                elif entry.has_key (f):
                    if Types.get_field (f).type == Fields.AuthorGroup:
                        text = join (map (lambda a: str (a.last), entry [f]), ', ')
                    elif Types.get_field (f).type == Fields.Date:
                        text = str (entry [f].year)
                    else:
                        text = str (entry [f])

                    text = text.decode ('latin-1')

                row.append((i, text))
                i = i + 1

            if True:
                if Resource.is_viewable (entry):
                    row.append((i, self.gvpixbuf))
                else:
                    row.append((i, None))

            iter = self.model.append  ()

            for k, v in row:
                if v is not None:
                    self.model.set_value(iter, k, v)

            self.access.append (entry)

            entry = iterator.next ()

        #Utils.set_cursor (self.w, 'normal')
        return


    def go_to_first (self, query, field):
        ''' Go to the first entry that matches a key '''
        if not isinstance (field, Sort.FieldSort): return 0

        f = field.field
        q = lower (query)
        l = len (q)
        i = 0

        for e in self.access:
            if not e.has_key (f): continue

            c = cmp (lower (str (e [f])) [0:l], q)

            if c == 0:
                # matching !
                self.set_scroll (i)
                return 1

            if c > 0:
                # we must be after the entry...
                self.set_scroll (i)
                return 0

            i = i + 1

        # well, show the user its entry must be after the bounds
        self.set_scroll (i)
        return  0


    def click_column (self, listcol, column):
        ''' handler for column title selection '''

        self.issue ('click-on-field', self.fields [column])
        return


    def select_row (self, sel, * data):
        ''' handler for row selection '''

        entries = self.selection ()
##      print 'ROW_SELECTED:', [x.key.key for x in entries]
        if len (entries) > 1:
            self.issue ('select-entries', entries)
            return

        if len (entries) == 1:
            self.issue ('select-entry', entries [0])
            return

        if len (entries) == 0:
            self.issue ('select-entry', None)
            return
        return


    def selection (self):
        ''' returns the current selection '''

        entries = []

        def retrieve (model, path, iter, entries):
            indices = path.get_indices()

            if len(self.access) > 0:
                entries.append(self.access[indices [0]])

        self.selinfo.selected_foreach (retrieve, entries)

        return entries


    def select_all (self):
        ''' select all the lines of the index '''

        self.clist.select_all ()
        return


    def button_press (self, clist, event, *arg):
        ''' handler for double-click and right mouse button '''

        if not (event.type == Gdk.EventType.BUTTON_PRESS and
                event.button == 3): return

        self._w_popup.popup (None, None, None, None, event.button, event.time)
        return

    def entry_new (self, * arg):
        self.issue ('new-entry')
        return

    def entry_edit (self, * arg):
        sel = self.selection ()
        if not sel: return

        self.issue ('edit-entry', sel)
        return

    def entry_delete (self, * arg):
        sel = self.selection ()
        if not sel: return

        self.issue ('delete-entry', sel)
        return


    def update_configuration (self):

        for i in range (len (self.fields)):
            w = self.list.get_column (i + self.prefix_columns).get_width ()
            f = self.fields [i]
            f = f.translate (_safechar)
            k = '/apps/pybliographic/columns/%s' % f
            Utils.config.set_int (k, w)


