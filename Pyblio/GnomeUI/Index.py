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

''' Main index containing the columned view of the entries '''

### TODO:

# 1. combined fields
# 2. new base class C_Index
# 3. separate routines to set columns and rows
# 4. GTK 2.0 ?



from Pyblio import Fields, Config, Connector, Types, Sort, userformat

from gnome.ui import *
from gnome import config

from Pyblio.GnomeUI import FieldsInfo, Utils, Mime
from gtk import *
import GTK, GDK

from string import *

import gettext, cPickle, string

pickle = cPickle
del cPickle

_ = gettext.gettext

class C_Index (Connector.Publisher):

    """ A listing view of a database or subset thereof.
    """

    def __init__ (self, mark = 1):

        self.columns, self.column_width = self.get_columns()
        self.clist = GtkCList (len (self.columns), self.columns)
        self.clist.set_selection_mode (GTK.SELECTION_EXTENDED)
        self.column_origin = not mark
        
        self.w = GtkScrolledWindow ()
        self.w.set_policy (POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        self.w.add (self.clist)

        self.access = []
        self.backref = {}
        self.menu_position = {
            'add'    : 0,
            'edit'   : 1,
            'delete' : 2,
            'toggle' : 3,
            }
        
        self.menu = GnomePopupMenu ([
            UIINFO_ITEM_STOCK(_("Add..."), None, self.entry_new,    STOCK_MENU_NEW),
            UIINFO_ITEM      (_("Edit..."),None, self.entry_edit),
            UIINFO_ITEM_STOCK(_("Delete"), None, self.entry_delete, STOCK_MENU_TRASH),
            UIINFO_ITEM      (_("Toggle..."),None, self.entry_toggle),
            ])
        
        self.menu.show ()
        
        # resize the columns
        for c in range (len (self.columns)):
            self.clist.set_column_width (c, self.column_width[c])
            self.clist.set_column_justification (
                c, FieldsInfo.justification (self.columns [c]))

        # some events we want to react to...
        self.clist.connect ('click_column',       self.click_column)
        self.clist.connect ('resize_column',      self.resize_column)
        self.clist.connect ('select_row',         self.select_row)
        self.clist.connect ('button_press_event', self.button_press)

        # ---------- DnD configuration

        targets = (
            (Mime.KEY_TYPE,   0, Mime.KEY),
            (Mime.ENTRY_TYPE, 0, Mime.ENTRY),
            )

        accept = (
            (Mime.ENTRY_TYPE, 0, Mime.ENTRY),
            )

        self.clist.drag_dest_set (DEST_DEFAULT_MOTION |
                                  DEST_DEFAULT_HIGHLIGHT |
                                  DEST_DEFAULT_DROP,
                                  accept,
                                  GDK.ACTION_COPY | GDK.ACTION_MOVE)
        self.clist.connect ("drag_data_received", self.drag_received)


        self.clist.drag_source_set (GDK.BUTTON1_MASK | GDK.BUTTON3_MASK,
                                    targets, GDK.ACTION_COPY | GDK.ACTION_MOVE)
        self.clist.connect ('drag_data_get', self.dnd_drag_data_get)

        # ---------- Copy/Paste configuration

        self.selection_buffer = None
        
        self.clist.connect ('selection_received', self.selection_received)
        self.clist.connect ('selection_get', self.selection_get)
        self.clist.connect ('selection_clear_event', self.selection_clear)

        self.clist.selection_add_target (1, Mime.atom ['STRING'], 0)
        self.clist.selection_add_target (1, Mime.atom [Mime.ENTRY_TYPE],
                                         Mime.ENTRY)
        return

    def display (self, iterator):

        # clear the access table
        self.access = []

        Utils.set_cursor (self.w, 'clock')
        
        self.clist.freeze ()
        self.clist.clear ()

        rowindex = 0
        entry = iterator.first ()
        while entry:
            
            row = self.set_row(entry)
            self.clist.append  (row)
            self.access.append (entry)
            self.clist.set_row_data(rowindex, entry)
            self.backref [entry.key.key] = rowindex
            if self.column_origin:
                if is_marked(entry):
                    self.clist.set_text(rowindex, 0,' ')
                else:
                    self.clist.set_text(rowindex, 0, 'X')

            entry = iterator.next ()
            rowindex = rowindex + 1
            
        self.clist.thaw ()
        Utils.set_cursor (self.w, 'normal')
        return

    def redisplay_entry(self, entry):
        """Change one row of displayed list."""

        if self.backref.has_key(entry.key.key):

            rowindex = self.backref[entry.key.key]
            row = self.set_row(entry)
            for i in range (self.column_origin, len(row)):
                self.clist.set_text(
                    rowindex, i, row[i])
        else:
            print 'redisplay failed'
        self.access[rowindex] = entry 
        self.select_item(entry)
        return

    
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
        
        self.clist.select_row (item, 0)
        self.set_scroll (item)
        self.issue ('select-entry', self.access[item])
        return
                                    
class Index (C_Index):
    
    ''' Graphical index of an iterator '''
    
    def __init__ (self, fields = None):
        ''' Creates a new list of entries '''
        self.fields = fields or Config.get ('gnome/columns').data
        if self.fields[0] != '-mark-':
            self.fields.insert(-1,'-mark-')

        self.fieldnames = ['X'] + map (lambda x: ' %s ' % x, self.fields[1:])

        C_Index.__init__(self)

        return

    def get_columns (self):
        widths = []
        for c in range (len (self.fieldnames)):
            width = config.get_int ('Pybliographic/Columns/%s=-1'
                                    % self.fields [c])

            if width == -1:
                width = FieldsInfo.width (self.fields [c])
            widths.append(width)
        return self.fieldnames, widths

    def set_row (self, entry):
        if is_marked(entry):
            row = ['X']
        else:
            row =['']

        for f in self.fields[1:]:
            f = string.lower (f)
            
            if f == '-key-':
                row.append (str (entry.key.key))
                    
            elif f == '-type-':
                row.append (str (entry.type.name))

            elif f == '-combined-':
                row.append (userformat.simple_combined_format(entry))

            elif entry.has_key (f):
                
                if Types.get_field (f).type == Fields.AuthorGroup:
                    text = join (map (lambda a: str (a.last), entry [f]), ', ')
                else:
                    text = str (entry [f])
                        
                row.append (text)
            else:
                row.append ('')

        return row
    
    def selection_clear (self, * arg):
        self.selection_buffer = None
        return

    
    def selection_received (self, widget, selection, info):
        if selection.length < 0: return
 
        entries = pickle.loads (selection.data)
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
            elif Config.get('gnome/paste-sutr').data:
                text = userformat.simple_untagged_format(item, width=50)
            else:
                # else, return the full entries
                text = join (map (str, self.selection_buffer), '\n\n')

        selection.set (1, 8, text)
        return


    def selection_copy (self, entries):
        self.clist.selection_owner_set (1, 0)
        self.selection_buffer = entries
        return


    def selection_paste (self):
        self.clist.selection_convert (1, Mime.atom [Mime.ENTRY_TYPE], 0)
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
        
        if info == Mime.KEY:
            # must return a set of keys
            data = join (map (lambda e: str (e.key.base or '') + '\0' +
                              str (e.key.key), entries), '\n')
            selection.set (selection.target, 8, data)
            
        elif info == Mime.ENTRY:
            data = pickle.dumps (entries)
            selection.set (selection.target, 8, data)

        if context.action == GDK.ACTION_MOVE:
            self.issue ('drag-moved', entries)
        
        return
    
    # --------------------------------------------------

    
        
    def set_scroll (self, item):
        if type (item) is not type (1):
            item = self.get_item_position (item)

        if item == -1: return
            
        self.clist.moveto (item, 0, .5, 0)
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
        
    
    def click_column (self, clist, column, * data):
        ''' handler for column title selection '''
        
        self.issue ('click-on-field', self.columns [column])
        return


    def resize_column (self, clist, column, width):
        self.column_width [column] = width
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
        if not self.clist.selection: return

        self.issue ('edit-entry', map (lambda x, self=self: self.access [x],
                                       self.clist.selection))
        return

        
    def entry_delete (self, * arg):
        if not self.clist.selection: return
        
        self.issue ('delete-entry', map (lambda x, self=self: self.access [x],
                                       self.clist.selection))
        return


    def entry_toggle (self, * arg):
        if not self.clist.selection: return
        
        #self.issue ('toggle-entry', map (lambda x, self=self: self.access [x],
        #             self.clist.selection))
        for i in self.clist.selection:
            if is_marked(self.access[i]):
                self.clist.set_text(i,0,' ')
                del self.access[i]['_attrib']
            else:
                self.clist.set_text(i,0,'X')
                self.access[i]['_attrib'] = 'marked'

        return


    def update_configuration (self):

        for i in range (len (self.fields)):

            config.set_int ('Pybliographic/Columns/%s' % self.fields [i],
                            self.column_width [i])
        
        return

######################################################################
def is_marked (entry):

    return entry.has_key('_attrib') and entry['_attrib'] == 'marked'

def set_marked(entry):
    entry['_attrib'] = 'marked'
    return

def toggle_mark(entry):
    if is_marked(entry):
        del entry['_attrib']
        
    else:
        entry['_attrib'] = 'marked'
    return
    
