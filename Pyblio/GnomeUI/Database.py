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

from Pyblio import Types, Config

from Pyblio.GnomeUI import FieldsInfo, Utils
from gtk import *

from string import *

class Database (GtkCList):
    ''' Complete database display '''
    
    def __init__ (self, fields = None):
        ''' Creates a new list of entries '''

        fields = fields or Config.get ('gnomeui/columns').data
        
        self.fields = fields
        lcfields = map (lower, fields)

        GtkCList.__init__ (self, len (self.fields), self.fields)
        
        for c in range (len (self.fields)):
            self.set_column_width (c, FieldsInfo.fieldinfo (
                lower (self.fields [c])).width)

        self.connect ('click_column', self.sort)
        
        self.data = None
        
        targets = [
            ('text/plain', 0, 0),
            ('application/x-pybkey', 0, 1)
            ]
        
        self.connect ('drag_data_get', self.dnd_drag_data_get)
        
        self.drag_source_set (GDK.BUTTON1_MASK|GDK.BUTTON3_MASK,
                              targets, GDK.ACTION_COPY)

        return

    def dnd_drag_data_get (self, list, context, selection, info, time):
        # get the current entry
        row   = self.focus_row
        if row < 0: return

        entry = self.data [self.access [row]]
        
        if info:
            # must return a key
            selection.set (selection.target, 8, str (entry.key.key))
        else:
            selection.set (selection.target, 8, str (entry))
        return
    
    # --------------------------------------------------

    def display (self, data):

        self.access = []
        self.clear ()

        def add_data (entry, self):
            row = []
            et  = entry.type
            
            for f in self.fields:
                lcf = lower (f)
                
                if entry.has_key (lcf):
                    t = Types.gettype (et, f)
                    
                    if t == Types.TypeAuthor:
                        text = join (map (lambda a: str (a.last), entry [lcf]),
                                     ', ')
                    else:
                        text = str (entry [lcf])
                        
                    row.append (text)
                else:
                    row.append ('')

            self.append (row)
            self.access.append (entry.key)

        self.freeze ()
        data.foreach (add_data, self)
        self.thaw ()
        return
    
    def set (self, data):
        self.data = data
        self.display (data)
        return
    
    def set_row (self, rownum, entry):
        col = 0
        et  = entry.type
        
        for f in self.fields:
            lcf = lower (f)
            
            if entry.has_key (lcf):
                t = Types.gettype (et, f)
                
                if t == Types.TypeAuthor:
                    def __toname (author):
                        return str (author.last)
                    text = join (map (__toname, entry [lcf]), ', ')
                else:
                    text = str (entry [lcf])
                    
                self.set_text (rownum, col, text)

            col = col + 1

        self.access [rownum] = entry.key
        return
    
    # --------------------------------------------------

    def __getattr__(self, attr):
        if attr == 'selection':
            if self.data is None: return
            
            entries = []
            for s in GtkCList.__getattr__ (self, attr):
                try:
                    entries.append (self.data [self.access [s]])
                except KeyError:
                    GtkCList.remove (self, row)
                    self.access.remove (key)
                    
            return entries
        
        return GtkCList.__getattr__(self, attr)

    def selected_rows (self):
        return GtkCList.__getattr__ (self, 'selection')

        
    def sort (self, widget, column):
        if self.data is None: return

        Utils.set_cursor (self, 'clock')

        field = lower (self.fields [column])
        keys = self.data.sort (field)
        
        self.display (keys)

        Utils.set_cursor (self, 'normal')

        return

    def sort_by (self, sorttype):
        if self.data is None: return

        Utils.set_cursor (self, 'clock')

        keys = self.data.sort (sorttype)
        
        self.display (keys)

        Utils.set_cursor (self, 'normal')
        return
        
    def remove (self, key):
        if self.data is None: return

        row = self.access.index (key)
        
        GtkCList.remove (self, row)
        self.access.remove (key)

        del self.data [key]
        return

    def insert (self, rownum, entry):
        et  = entry.type
        row = []
        
        for f in self.fields:
            lcf = lower (f)
                
            if entry.has_key (lcf):
                t = Types.gettype (et, f)
                    
                if t == Types.TypeAuthor:
                    def __toname (author):
                        return str (author.last)
                    text = join (map (__toname, entry [lcf]), ', ')
                else:
                    text = str (entry [lcf])
                        
                row.append (text)
            else:
                row.append ('')

        GtkCList.insert (self, rownum, row)
        self.access.insert (rownum, entry.key)
