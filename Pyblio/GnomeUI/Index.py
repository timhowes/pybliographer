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
#  - DnD with the world
#  - Copy/Paste with the world
#  - contextual popup menu
#  - column width storage


''' Main index containing the columned view of the entries '''

from Pyblio import Fields, Config, Connector, Types, Sort

from gnome import ui
import gtk, gobject

from Pyblio.GnomeUI import FieldsInfo, Utils, Mime

from string import *

import gettext, cPickle

pickle = cPickle
del cPickle

_ = gettext.gettext


class Index (Connector.Publisher):
    ''' Graphical index of an iterator '''
    
    def __init__ (self, fields = None):
        ''' Creates a new list of entries '''
        
        fields = fields or Config.get ('gnome/columns').data
        self.fields = map (lower, fields)

        self.model = apply (gtk.ListStore,
                            (gobject.TYPE_STRING,) * len (fields))

        self.list = gtk.TreeView ()
        self.list.set_model (self.model)
        
        self.selinfo = self.list.get_selection ()
        
        i = 0
        for f in fields:
            col = gtk.TreeViewColumn (f, gtk.CellRendererText (),
                                      text = i)
            col.set_resizable (True)
            col.set_clickable (True)

            col.connect ('clicked', self.click_column, i)
            
            self.list.append_column (col)
            i = i + 1
        
        self.w = gtk.ScrolledWindow ()

        self.w.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.w.add (self.list)

        self.access = []
            
        # some events we want to react to...
        self.selinfo.connect ('changed', self.select_row)
        self.list.connect ('row-activated', self.entry_edit)

        # ---------- DnD configuration
 
        targets = (
            (Mime.KEY_TYPE,   0, Mime.KEY),
            (Mime.ENTRY_TYPE, 0, Mime.ENTRY),
            )
 
        accept = (
            (Mime.ENTRY_TYPE, 0, Mime.ENTRY),
            )
 
        self.list.drag_dest_set (gtk.DEST_DEFAULT_MOTION |
                                 gtk.DEST_DEFAULT_HIGHLIGHT |
                                 gtk.DEST_DEFAULT_DROP,
                                 accept,
                                 gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
        self.list.connect ("drag_data_received", self.drag_received)
 
 
        self.list.drag_source_set (gtk.gdk.BUTTON1_MASK | gtk.gdk.BUTTON3_MASK,
                                   targets, gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
        self.list.connect ('drag_data_get', self.dnd_drag_data_get)
 
        # ---------- Copy/Paste configuration
 
        self.selection_buffer = None
         
        self.list.connect ('selection_received', self.selection_received)
        self.list.connect ('selection_get', self.selection_get)
        self.list.connect ('selection_clear_event', self.selection_clear)
 
        self.list.selection_add_target (Mime.atom ['self'],
                                        Mime.atom ['STRING'],
                                        Mime.STRING)
        
        self.list.selection_add_target (Mime.atom ['self'],
                                        Mime.atom [Mime.ENTRY_TYPE],
                                        Mime.ENTRY)
        return


    def selection_clear (self, * arg):
        self.selection_buffer = None
        return

    
    def selection_received (self, widget, selection, info):
        
        data = selection.data
        
        if not data: return
 
        entries = pickle.loads (data)
        self.issue ('drag-received', entries)
        return


    def selection_get (self, widget, selection, info, time):

        if not self.selection_buffer: return
        
        if info == Mime.ENTRY:
            text = pickle.dumps (self.selection_buffer)
        else:
            if Config.get ('gnome/paste-key').data:
                # if we want the keys, return the keys !
                keys = []
                for e in self.selection_buffer:
                    keys.append (str (e.key.key))
                text = join (keys, ',')
            else:
                # else, return the full entries
                text = join (map (str, self.selection_buffer), '\n\n')
        
        selection.set (Mime.atom ['self'], 8, text)
        return


    def selection_copy (self, entries):
        self.list.selection_owner_set (Mime.atom ['self'])
        self.selection_buffer = entries
        return


    def selection_paste (self):
        self.list.selection_convert (Mime.atom ['self'],
                                     Mime.atom [Mime.ENTRY_TYPE])
        return

        
    def set_menu_active (self, item, value):
        ''' This method sets the sensitivity of each popup menu item '''

        self.menu.children () [self.menu_position [item]].set_sensitive (value)
        return
    

    def drag_received (self, * arg):
        selection = arg [4]
        info      = arg [5]

        if info == Mime.ENTRY:
            entries = pickle.loads (selection.data)
            self.issue ('drag-received', entries)

        return

    
    def dnd_drag_data_get (self, list, context, selection, info, time):
        ''' send the selected entries as dnd data '''

        entries = self.selection ()
        if not entries: return

        print info
        
        if info == Mime.KEY:
            # must return a set of keys
            data = join (map (lambda e: str (e.key.base or '') + '\0' +
                              str (e.key.key), entries), '\n')
            selection.set (selection.target, 8, data)
            
        elif info == Mime.ENTRY:
            data = pickle.dumps (entries)
            selection.set (selection.target, 8, data)

        if context.action == gtk.gdk.ACTION_MOVE:
            self.issue ('drag-moved', entries)
        
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

        if item == -1 or item >= len (self.access): return

        path = (item,)
        
        self.selinfo.select_path (path)
        self.list.scroll_to_cell (path)

        self.issue ('select-entry', self.access [item])
        return
    
        
    def set_scroll (self, item):
        if type (item) is not type (1):
            item = self.get_item_position (item)

        if item == -1: return
        
        self.list.scroll_to_cell ((item,),
                                  use_align = True,
                                  row_align = .5)
        return

    
    def display (self, iterator):

        # clear the access table
        self.access = []

        Utils.set_cursor (self.w, 'clock')
        
        self.model.clear ()

        entry = iterator.first ()
        while entry:
            row = []

            i = 0
            for f in self.fields:
                row.append (i)
                i = i + 1
                
                if f == '-key-':
                    row.append (str (entry.key.key))
                    
                elif f == '-type-':
                    row.append (str (entry.type.name))
                    
                elif entry.has_key (f):
                    
                    if Types.get_field (f).type == Fields.AuthorGroup:
                        text = join (map (lambda a: str (a.last), entry [f]), ', ')
                    else:
                        text = str (entry [f])
                        
                    row.append (text)
                else:
                    row.append ('')

            iter = self.model.append  ()
            apply (self.model.set, [iter] + row)
            
            self.access.append (entry)

            entry = iterator.next ()
            
        Utils.set_cursor (self.w, 'normal')
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


    def resize_column (self, clist, column, width):
        self.field_width [column] = width
        return

    
    def select_row (self, sel, * data):
        ''' handler for row selection '''

        entries = self.selection ()
        
        if len (entries) > 1:
            self.issue ('select-entries', entries)
            return

        if len (entries) == 1:
            self.issue ('select-entry', entries [0])
            return
        return


    def selection (self):
        ''' returns the current selection '''
        
        entries = []

        def retrieve (model, path, iter):
            entries.append (self.access [path [0]])

        self.selinfo.selected_foreach (retrieve)

        return entries


    def select_all (self):
        ''' select all the lines of the index '''
        
        self.clist.select_all ()
        return

    
    def button_press (self, clist, event, *arg):
        ''' handler for double-click and right mouse button '''

        if (event.type == GDK._2BUTTON_PRESS and event.button == 1):
            # select the item below the cursor
            couple = self.clist.get_selection_info (event.x, event.y)
            if couple:
                self.clist.select_row (couple [0], couple [1])
                self.issue ('edit-entry', [self.access [couple [0]]])
            return
        
        if (event.type == GDK.BUTTON_PRESS and event.button == 3):
            if not self.clist.selection:
                # select the item below the cursor
                couple = self.clist.get_selection_info (event.x, event.y)
                if couple:
                    self.clist.select_row (couple [0], couple [1])

            # what menu items are accessible ?

            if len (self.clist.selection) == 0:
                mask = (1, 0, 0)
            else:
                mask = (1, 1, 1)

            items = ('add', 'edit', 'delete')
            for i in range (3):
                self.set_menu_active (items [i], mask [i])

            self.menu.popup (None, None, None, event.button, event.time)
            return

        return


    def entry_new (self, * arg):
        self.set_menu_active ('add', 0)
        
        self.issue ('new-entry', map (lambda x, self=self: self.access [x],
                                       self.clist.selection))
        return

    
    def entry_edit (self, * arg):
        sel = self.selection
        if not sel: return

        self.issue ('edit-entry', sel)
        return

        
    def entry_delete (self, * arg):
        if not self.clist.selection: return
        
        self.issue ('delete-entry', map (lambda x, self=self: self.access [x],
                                       self.clist.selection))
        return


    def update_configuration (self):

#        for i in range (len (self.fields)):
#            Utils.config.set_int ('/apps/pybliographic/columns/%s' % self.fields [i],
#                                  self.field_width [i])
        return
