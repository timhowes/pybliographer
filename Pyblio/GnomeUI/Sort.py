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

''' This module implements a Dialog to define Sort criterions '''

from gtk import *
from gnome.ui import *
from gnome import config

import gettext, string
_ = gettext.gettext

from Pyblio import Connector, Sort, Config
from Pyblio.GnomeUI import Utils

import cPickle

pickle = cPickle
del cPickle


class SortDialog (Connector.Publisher):
    
    def __init__ (self, current_sort, parent = None):

        if current_sort:
            current_sort = current_sort.fields
        else:
            current_sort = []
        
        self.window = GnomeDialog (_("Select sort criterions"),
                                   STOCK_BUTTON_OK,
                                   STOCK_BUTTON_CANCEL)
        
        if parent: self.window.set_parent (parent)

        self.window.button_connect (0, self.apply)
        self.window.set_close (1)
        self.window.close_hides (1)
        self.window.set_policy (TRUE, TRUE, FALSE)
        
        self.list = GtkCList (2, (_("Sort direction"),_("Sort criterions")))
        self.list.column_titles_passive ()
        self.list.set_column_justification (0, JUSTIFY_CENTER)
        self.list.set_reorderable (1)
        self.list.set_selection_mode (SELECTION_BROWSE)
        self.list.connect ('select_row', self.select_row)
        
        # fill in the lists
        criterions = [
            [ 0, Sort.TypeSort () ],
            [ 0, Sort.KeySort ()  ],
            ]

        criterions [0][1].name = _("[Entry Type]")
        criterions [1][1].name = _("[Key Value]")
        
        fields = map (lambda x: x.name,
                      Config.get ('base/fields').data.values ())
        fields.sort ()
        
        for field in fields:
            sort = Sort.FieldSort (string.lower (field))
            sort.name = field
            criterions.append ([current_sort.count (sort), sort])

        self.set_criterions (criterions)
        self.reorder_items ()
        
        scroll = GtkScrolledWindow ()
        scroll.set_policy (POLICY_NEVER, POLICY_AUTOMATIC)
        scroll.add (self.list)
        (width, height) = scroll.size_request ()
        scroll.set_usize (width, height * 4)
        self.window.vbox.pack_start (scroll)

        # operation buttons
        box = GtkHButtonBox ()
        box.set_layout_default (BUTTONBOX_SPREAD)
        
        b = GtkButton (_("Reorder"))
        Utils.set_tip (b, _("Groups the active fields on the top of the list"))
        b.connect ('clicked', self.reorder_items)
        box.pack_start (b)

        b = GtkButton (_("Unselect all"))
        Utils.set_tip (b, _("Removes all the sort criterions"))
        b.connect ('clicked', self.unselect_items)
        box.pack_start (b)

        b = GtkButton (_("Set as default"))
        Utils.set_tip (b, _("Use this sort criterion as the default"
                            " for new files"))
        b.connect ('clicked', self.set_as_default)
        box.pack_start (b)

        self.window.vbox.pack_start (box, FALSE, FALSE)
        self.window.show_all ()
        return


    def select_row (self, w, row, column, * arg):
        if column != 0: return

        data = self.list.get_row_data (row)
        data [0] = ((data [0] + 2) % 3) - 1
        if   data [0] == -1:
            self.list.set_text (row, 0, '<')
        elif data [0] == +1:
            self.list.set_text (row, 0, '>')
        else:
            self.list.set_text (row, 0, '')
        return
    

    def get_criterions (self):
        criterions = []
        for i in range (0, self.list.rows):
            data = self.list.get_row_data (i)
            if not data: break

            criterions.append (data)
        return criterions

    def set_criterions (self, criterions):
        self.list.freeze ()
        self.list.clear ()
        i = 0
        for c in criterions:
            status = ''
            if   c [0] == +1:
                status = '>'
            elif c [0] == -1:
                status = '<'
            self.list.append ((status, c [1].name))
            self.list.set_row_data (i, c)
            i = i + 1
        self.list.thaw ()
        return

    
    def reorder_items (self, * arg):
        crit = self.get_criterions ()
        select = []
        unselect = []
        for c in crit:
            if c [0]:
                select.append (c)
            else:
                unselect.append (c)
        unselect.sort (lambda x, y: cmp (string.lower (x [1].name),
                                         string.lower (y [1].name)))
        self.set_criterions (select + unselect)
        return
    

    def unselect_items (self, * arg):
        crit = self.get_criterions ()
        for c in crit: c [0] = 0
        self.set_criterions (crit)
        return


    def show (self):
        self.reorder_items ()
        self.window.show ()
        return


    def get_result (self):
        data   = filter (lambda x: x [0], self.get_criterions ())
        result = []
        for d in data:
            d [1].ascend = d [0]
            result.append (d [1])

        if result == []: result = None
        
        return result


    def set_as_default (self, * arg):
        config.set_string ('Pybliographic/Sort/Default',
                           pickle.dumps (self.get_result ()))
        config.sync ()
        return
    
    
    def apply (self, * arg):
        self.issue ('sort-data', self.get_result ())
        self.window.close ()
        return
    
