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

from __future__ import nested_scopes

import GTK

from gtk import *
from gnome.ui import *
from gnome import config

from libglade import GladeXML
from Pyblio import version, Exceptions
from Pyblio.QueryEngine import Connection
from Pyblio.GnomeUI import Utils

from Pyblio import QueryEngine

import os, pickle

path = os.path.join ('Pyblio', 'GnomeUI', 'query.glade')

if not os.path.exists (path):
    path = os.path.join (version.prefix, path)


class QueryUI:

    def __init__ (self, parent = None):
        ''' Create a generic Query interface '''
        
        self.xml = GladeXML (path, 'query')
        self.xml.signal_autoconnect ({ 'search'  : self.search,
                                       'cancel'  : self.cancel,
                                       'destroy' : self.close,
                                       'edit'    : self.cnx_edit })
        
        self.w_search = self.xml.get_widget ('query')
        self.w_cnx    = None

        if parent:
            self.w_search.set_parent (parent)


        ui_width  = config.get_int ('Pybliographic/Query/Width=-1')
        ui_height = config.get_int ('Pybliographic/Query/Height=-1')

        # set window size
        if ui_width != -1 and ui_height != -1:
            self.w_search.set_usize(ui_width, ui_height)


        # get the previous connection settings
        self.current_cnx = None
        
        self.file = os.path.expanduser ('~/.pybliographer/connections')
        self.load ()
        
        # ...and display them in the dropdown menu
        self.update ()

        self.w_search.show ()
        return

    def load (self):
        ''' Load the list of known connections '''
        
        if os.path.exists (self.file):
            self.cnx = pickle.load (open (self.file, 'r'))
        else:
            self.cnx = []
        return

    def save (self):
        ''' Save the list of known connections '''

        pickle.dump (self.cnx, open (self.file, 'w'))
        return


    def update (self):
        ''' Update the optionmenu of available connections '''
        
        # display in the dropdown menu
        option = self.xml.get_widget ('query_option')
        menu   = GtkMenu ()

        for cnx in self.cnx:
            item = GtkMenuItem (cnx.name)
            item.set_data ('cnx', cnx)
            item.connect ('activate', self.activate_cnx_cb)
            item.show ()
            
            menu.append (item)

        option.set_menu (menu)
        option.set_history (0)

        if self.cnx:
            self.show_cnx_query (self.cnx [0])
        return


    def activate_cnx_cb (self, menu):
        ''' Invoked when another connection is selected by the user '''
        
        self.show_cnx_query (menu.get_data ('cnx'))
        return

    def show_cnx_query (self, cnx):
        ''' Display the available query fields for the specified connection '''

        if self.current_cnx == cnx: return
        self.current_cnx = cnx

        box = self.xml.get_widget ('query_vbox')

        for child in box.children (): child.destroy ()
        
        cnx.default.display (box)
        box.show_all ()

        extra = self.xml.get_widget ('extra_query')
        extra.set_sensitive (cnx.extended is not None)
        return
    
        
    def search (self, * arg):
        ''' Perform the actual search operation '''
        
        cnx = self.current_cnx
        if cnx is None: return
        
        engine = cnx.engine ()

        # display a progress bar...
        xml = GladeXML (path, 'progress')

        w = xml.get_widget ('progress')
        w.set_parent (self.w_search)
        w.show ()
        
        bar = xml.get_widget ('progressbar')
        
        def show_progress (progress):
            bar.update (progress)
            while events_pending (): mainiteration ()
            return

        def cancel_query (widget):
            engine.cancel ()
            return

        xml.signal_autoconnect ({ 'cancel' : cancel_query })
        
        engine.Subscribe ('progress', show_progress)
        show_progress (0.0)
        
        if not engine.search ({}):
            # close the progress bar but do not destroy the search
            w.destroy ()
            return

        # the song is over, turn off the lights
        w.destroy ()
        
        if self.w_cnx:
            self.w_cnx.destroy ()
        self.w_search.destroy ()
        return


    def cancel (self, * arg):
        if self.w_cnx:
            self.w_cnx.destroy ()
        self.w_search.destroy ()
        return

    def close (self, * arg):
        
        # save the size of the window
        alloc = self.w_search.get_allocation ()
        config.set_int ('Pybliographic/Query/Width',  alloc [2])
        config.set_int ('Pybliographic/Query/Height', alloc [3])
        config.sync ()
        
        self.w_cnx = None
        return

    def cnx_validate (self, * arg):
        self.w_cnx.destroy ()

        self.save ()
        self.update ()
        return

    def cnx_cancel (self, * arg):
        # reload the default list
        self.load ()

        self.w_cnx.destroy ()
        return

    def cnx_closed (self, * arg):
        ''' Called when the connection editor is closed '''

        # save the size of the window
        alloc = self.w_cnx.get_allocation ()
        config.set_int ('Pybliographic/QueryCnx/Width',  alloc [2])
        config.set_int ('Pybliographic/QueryCnx/Height', alloc [3])
        config.sync ()
        
        self.w_cnx = None
        return
    
    def cnx_entry (self, * arg):
        file = arg [0].get_text ()

        try:
            cnx = Connection (file, QForm)
        except Exceptions.SyntaxError, msg:
            GnomeErrorDialog ("In the XML Connection '%s':\n%s" %
                              (os.path.basename (file), msg),
                              parent = self.w_cnx).show ()
            return
        
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
                                         'destroy'   : self.cnx_closed,
                                         })
        
        self.w_cnx = self.x_cnx.get_widget ('connections')

        ui_width  = config.get_int ('Pybliographic/QueryCnx/Width=-1')
        ui_height = config.get_int ('Pybliographic/QueryCnx/Height=-1')

        accelerator = GtkAccelGroup ()
        self.w_cnx.add_accel_group (accelerator)

        # the invisible delete button
        delete = self.x_cnx.get_widget ('delete')
        delete.add_accelerator ('clicked', accelerator,
                                GDK.D, GDK.CONTROL_MASK, 0)

        self.cnx_update ()

        # set window size
        if ui_width != -1 and ui_height != -1:
            self.w_cnx.set_usize(ui_width, ui_height)

        self.w_cnx.set_parent (self.w_search)
        self.w_cnx.show ()
        return
        


class QOperator (QueryEngine.QOperator):
    ''' Allowed operators for a field search '''

    def display (self, box):
        return

    
class QField (QueryEngine.QField):

    CL = {
        'QOperator' : QOperator
        }
    
    ''' A specific field that can be searched '''

    def display (self, box):
        return



class QFields (QueryEngine.QFields):

    CL = {
        'QOperator'  : QOperator,
        'QField'     : QField,
        }
    
    ''' Sets of fields the user can search on '''

    def display (self, box):

        self.current = []

        vbox = GtkVBox (spacing = 5)
        
        # the fields are displayed in a table
        self.w_table = GtkTable (1, 3)
        vbox.pack_start (self.w_table)
        
        if self.title:
            vbox.set_border_width (5)

            frame = GtkFrame (self.title.encode ('latin-1'))
            frame.add (vbox)
        else:
            frame = vbox

        # add the function buttons below
        hbox = GtkHButtonBox ()
        hbox.set_layout_default (GTK.BUTTONBOX_END)
        hbox.set_spacing_default (5)
        
        hbox.pack_end (GtkButton ("Add"))
        hbox.pack_end (GtkButton ("Remove"))

        # ...and add a first field, so that it does not look too
        # strange.
        self.set_field (0)

        vbox.pack_start (hbox)
        box.pack_start (frame)
        return


    def set_field (self, row):

        # Operator menu
        o_holder = GtkOptionMenu ()
        self.w_table.attach (o_holder, 1, 2, row, row + 1)

        # Field menu
        holder = GtkOptionMenu ()
        menu   = GtkMenu ()
        
        holder.set_menu (menu)

        for item in self.content:
            w = GtkMenuItem (item.title.encode ('latin-1'))

            w.connect ('activate', self.activate_field, item, o_holder)
            menu.add (w)
        
        self.w_table.attach (holder, 0, 1, row, row + 1)

        # ...and attach the entry widget
        text = GtkEntry ()
        self.w_table.attach (text, 2, 3, row, row + 1)

        # display the first field by default
        holder.set_history (0)
        self.activate_field (None, self.content [0], o_holder)
        return


    def activate_field (self, w, field, holder):
        menu   = GtkMenu ()
        holder.set_menu (menu)

        for op in field.operators:
            w = GtkMenuItem (op.title.encode ('latin-1'))
            menu.add (w)

        menu.show_all ()
        
        holder.set_history (0)
        return


class QSelection (QueryEngine.QSelection):

    ''' A selection between several choices '''

    def display (self, box):
        hbox = GtkHBox ()
        hbox.set_spacing (5)

        if self.title:
            hbox.pack_start (GtkLabel (self.title.encode ('latin-1')),
                             expand = FALSE, fill = FALSE)
        
        holder = GtkOptionMenu ()
        menu   = GtkMenu ()
        
        holder.set_menu (menu)

        for item in self.content:
            w = GtkMenuItem (item [1].encode ('latin-1'))
            menu.add (w)

        holder.set_history (0)
        
        hbox.pack_start (holder, expand = TRUE, fill = TRUE)
        box.pack_start (hbox, expand = TRUE, fill = TRUE)
        return


class QToggle (QueryEngine.QToggle):

    ''' A selection between two choices '''

    def display (self, box):
        toggle = GtkCheckButton (self.title.encode ('latin-1'))
        toggle.set_active (self.enabled)

        box.pack_start (toggle, expand = TRUE, fill = TRUE)
        return


class QGroup (QueryEngine.QGroup):
    CL = {
        'QFields' : QFields,
        'QSelection' : QSelection,
        'QToggle' : QToggle,
        }

    ''' Grouping of several query forms '''

    def display (self, box):

        hbox = GtkHBox ()
        hbox.set_spacing (5)
        
        if self.title:
            frame = GtkFrame (self.title.encode ('latin-1'))
            hbox.set_border_width (5)
            
            frame.add (hbox)
        else:
            frame = hbox

        for part in self.content:
            part.display (hbox)

        box.pack_start (frame)
        return


class QForm (QueryEngine.QForm):
    ''' Complete description of a query form '''

    CL = {
        'QFields'    : QFields,
        'QGroup'     : QGroup,
        'QSelection' : QSelection,
        'QOperator'  : QOperator,
        'QToggle'    : QToggle,
        }


    def display (self, box):

        for part in self.content:
            part.display (box)
        return
    
