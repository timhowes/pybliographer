# This file is part of pybliographer
# 
# Copyright (C) 1998-2002 Frederic GOBRY
# Email : gobry@users.sf.net
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

''' Manage the generic query interface. '''

from gtk import *
from gnome.ui import *

from libglade import GladeXML
from Pyblio import version, Exceptions
from Pyblio.QueryEngine import Connection
from Pyblio.GnomeUI import Utils

import os, pickle

path = os.path.join ('Pyblio', 'GnomeUI', 'query.glade')

if not os.path.exists (path):
    path = os.path.join (version.prefix, path)


class QueryUI:

    def __init__ (self, parent = None):
        self.xml = GladeXML (path, 'query')
        self.xml.signal_autoconnect ({ 'search' : self.search,
                                       'cancel' : self.cancel,
                                       'edit'   : self.cnx_edit })
        
        self.w_search = self.xml.get_widget ('query')
        self.w_cnx    = None

        if parent:
            self.w_search.set_parent (parent)

        # get the previous connection settings
        self.file = os.path.expanduser ('~/.pybliographer/connections')
        self.load ()
        
        # ...and display them in the dropdown menu
        self.update ()

        self.w_search.show ()
        return

    def load (self):
        if os.path.exists (self.file):
            self.cnx = pickle.load (open (self.file, 'r'))
        else:
            self.cnx = []
        return

    def save (self):
        pickle.dump (self.cnx, open (self.file, 'w'))
        return

    def update (self):
        # display in the dropdown menu
        option = self.xml.get_widget ('query_option')
        menu   = GtkMenu ()

        for cnx in self.cnx:
            item = GtkMenuItem (cnx.name)
            item.set_data ('cnx', cnx)
            item.show ()
            
            menu.append (item)

        option.set_menu (menu)
        option.set_history (0)
        return

        
    def search (self, * arg):
        menu = self.xml.get_widget ('query_option').get_menu ()
        cnx = menu.get_active ().get_data ('cnx')

        engine = cnx.engine ()

        # display a progress bar...
        engine.Subscribe ('progress', self.search_progress)

        engine.search ({})
        
        if self.w_cnx:
            self.w_cnx.destroy ()
        self.w_search.destroy ()
        return

    def search_progress (self, progress):
        print "Progress: %d" % progress
        return
    

    def cancel (self, * arg):
        if self.w_cnx:
            self.w_cnx.destroy ()
        self.w_search.destroy ()
        return



    def cnx_validate (self, * arg):
        self.save ()
        
        self.w_cnx.destroy ()
        self.w_cnx = None
        return

    def cnx_cancel (self, * arg):
        # reload the default list
        self.load ()

        self.w_cnx.destroy ()
        self.w_cnx = None
        return

    def cnx_entry (self, * arg):
        file = arg [0].get_text ()

        try:
            cnx = Connection (file)
        except Exceptions.SyntaxError, msg:
            w = GnomeErrorDialog ("In the XML Connection '%s':\n%s" %
                                  (os.path.basename (file), msg),
                                  parent = self.w_cnx)
            w.show_all ()

        self.cnx.insert (0, cnx)
        self.cnx_update ()
        return

    def cnx_update (self):
        list = self.x_cnx.get_widget ('cnx_list')
        list.freeze ()
        list.clear ()

        for cnx in self.cnx:
            list.append ((cnx.name.encode ('latin-1'),
                          cnx.type.encode ('latin-1'),
                          cnx.host.encode ('latin-1')))

        list.thaw ()
        return

    def cnx_delete (self, * arg):
        list = self.x_cnx.get_widget ('cnx_list')

        if not list.selection: return
        
        row = list.selection [0]
        list.remove (row)
        
        del self.cnx [row]
        return
    

    def cnx_edit (self, * arg):
        if self.w_cnx: return

        self.x_cnx = GladeXML (path, 'connections')

        self.x_cnx.signal_autoconnect ({ 'validate'  : self.cnx_validate,
                                         'cancel'    : self.cnx_cancel,
                                         'cnx_entry' : self.cnx_entry,
                                         'delete'    : self.cnx_delete,
                                         })
        
        self.w_cnx = self.x_cnx.get_widget ('connections')

        accelerator = GtkAccelGroup ()
        self.w_cnx.add_accel_group (accelerator)

        # the invisible delete button
        delete = self.x_cnx.get_widget ('delete')
        delete.add_accelerator ('clicked', accelerator,
                                GDK.D, GDK.CONTROL_MASK, 0)

        self.cnx_update ()
        
        self.w_cnx.set_parent (self.w_search)
        self.w_cnx.show ()
        return
        
