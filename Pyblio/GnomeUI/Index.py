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

from Pyblio import Fields, Config, Connector

from gnome.ui import *
from Pyblio.GnomeUI import FieldsInfo, Utils
from gtk import *
import GTK, GDK

from string import *

import gettext, cPickle

pickle = cPickle
del cPickle

_ = gettext.gettext


PYBLIOKEY   = 1
PYBLIOENTRY = 2

class Index (Connector.Publisher):
    ''' Graphical index of an iterator '''
    
    def __init__ (self, fields = None):
        ''' Creates a new list of entries '''

        fields = fields or Config.get ('gnomeui/columns').data
        self.fields = map (lower, fields)

        self.clist = GtkCList (len (fields), fields)
        self.clist.set_selection_mode (GTK.SELECTION_EXTENDED)
        
        self.w = GtkScrolledWindow ()
        self.w.set_policy (POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        self.w.add (self.clist)

        self.access = []

        self.menu_position = {
            'add'    : 0,
            'edit'   : 1,
            'delete' : 2,
            }
        
        self.menu = GnomePopupMenu ([
            UIINFO_ITEM_STOCK(_("Add..."), None, self.entry_new,    STOCK_MENU_NEW),
            UIINFO_ITEM      (_("Edit..."),None, self.entry_edit),
            UIINFO_ITEM_STOCK(_("Delete"), None, self.entry_delete, STOCK_MENU_TRASH),
            ])
        
        self.menu.show ()

        # resize the columns
        for c in range (len (self.fields)):
            self.clist.set_column_width (c, FieldsInfo.fieldinfo (
                self.fields [c]).width)

        # some events we want to react to...
        self.clist.connect ('click_column',       self.click_column)
        self.clist.connect ('select_row',         self.select_row)
        self.clist.connect ('button_press_event', self.button_press)

        # DnD configuration
        targets = (
            # request for a Key
            ('application/x-pybliokey',    0, PYBLIOKEY),
            # request for a full entry
            ('application/x-pybliography', 0, PYBLIOENTRY),
            )

        accept = (
            ('application/x-pybliography', 0, PYBLIOENTRY),
            )

        self.clist.drag_dest_set (DEST_DEFAULT_MOTION |
                                  DEST_DEFAULT_HIGHLIGHT |
                                  DEST_DEFAULT_DROP,
                                  accept,
                                  GDK.ACTION_COPY)

        self.clist.connect ("drag_data_received", self.drag_received)


        self.clist.drag_source_set (GDK.BUTTON1_MASK | GDK.BUTTON3_MASK,
                                targets, GDK.ACTION_COPY)

        self.clist.connect ('drag_data_get', self.dnd_drag_data_get)
        
        return


    def set_menu_active (self, item, value):
        ''' This method sets the sensitivity of each popup menu item '''

        self.menu.children () [self.menu_position [item]].set_sensitive (value)
        return
    

    def drag_received (self, * arg):
        selection = arg [4]
        info      = arg [5]

        if info == PYBLIOENTRY:
            entries = pickle.loads (selection.data)
            self.issue ('drag-received', entries)

        return
    
    def dnd_drag_data_get (self, list, context, selection, info, time):
        ''' send the selected entries as dnd data '''
        
        entries = self.selection ()
        if not entries: return
        
        if info == PYBLIOKEY:
            # must return a set of keys
            data = join (map (lambda e: str (e.key.base) + '\0' + str (e.key.key), entries), '\0')
            selection.set (selection.target, 8, data)
            
        elif info == PYBLIOENTRY:
            data = pickle.dumps (entries)
            selection.set (selection.target, 8, data)
            
        return
    
    # --------------------------------------------------

    def display (self, iterator):

        # clear the access table
        self.access = []

        Utils.set_cursor (self.w, 'clock')
        
        self.clist.freeze ()
        self.clist.clear ()

        entry = iterator.first ()
        while entry:
            row = []
            
            for f in self.fields:
                if entry.has_key (f):
                    
                    if entry.type (f) == Fields.AuthorGroup:
                        text = join (map (lambda a: str (a.last), entry [f]), ', ')
                    else:
                        text = str (entry [f])
                        
                    row.append (text)
                else:
                    row.append ('')

            self.clist.append  (row)
            self.access.append (entry)

            entry = iterator.next ()
            
        self.clist.thaw ()
        Utils.set_cursor (self.w, 'normal')
        return

    
    def click_column (self, clist, column, * data):
        ''' handler for column title selection '''
        
        self.issue ('sort-by-field', self.fields [column])
        return

    
    def select_row (self, clist, row, column, * data):
        ''' handler for row selection '''
        
        # multiple selections are not handled like single selections
        if len (self.clist.selection) > 1:
            self.issue ('select-entries',
                        map (lambda x, self=self: self.access [x],
                             self.clist.selection))
            return
        
        self.issue ('select-entry', self.access [row])
        return


    def selection (self):
        ''' returns the current selection '''
        
        return map (lambda x, self=self: self.access [x],
                    self.clist.selection)

    
    def button_press (self, clist, event, *arg):
        ''' handler for double-click and right mouse button '''
        
        if (event.type == GDK._2BUTTON_PRESS and event.button == 1):
            self.issue ('edit-entry', self.access [self.clist.focus_row])
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
        if not self.clist.selection: return
        
        self.issue ('edit-entry', map (lambda x, self=self: self.access [x],
                                       self.clist.selection))
        return
        
    def entry_delete (self, * arg):
        if not self.clist.selection: return
        
        self.issue ('delete-entry', map (lambda x, self=self: self.access [x],
                                       self.clist.selection))
        return
