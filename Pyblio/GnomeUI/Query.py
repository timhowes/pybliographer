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

from Pyblio import QueryEngine, Connector

import os, pickle, string, copy

path = os.path.join ('Pyblio', 'GnomeUI', 'query.glade')

if not os.path.exists (path):
    path = os.path.join (version.prefix, path)


class QueryUI (Connector.Publisher):

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
        # if ui_width != -1 and ui_height != -1:
        #    self.w_search.set_usize(ui_width, ui_height)


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

        for name, content in (('query_default', cnx.default),
                              ('query_extended', cnx.extended)):
            
            box = self.xml.get_widget (name)
            for child in box.children (): child.destroy ()

            if content:
                content.display (box)
                box.show_all ()
        return
    
        
    def search (self, * arg):
        ''' Perform the actual search operation '''
        
        cnx = self.current_cnx
        if cnx is None: return

        # get back the user query 
        query = cnx.default.query_get ()
        
        if cnx.extended:
            query = cnx.extended.query_get (query)

        # get the query engine
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

        
        try:
            retval = engine.search (query)
        except Exceptions.SyntaxError, msg:
            GnomeErrorDialog ("%s" % msg).show ()
            retval = 0
        
        if not retval:
            # close the progress bar but do not destroy the search
            w.destroy ()
            return

        # the song is over, turn off the lights
        w.destroy ()
        
        if self.w_cnx:
            self.w_cnx.destroy ()
        self.w_search.destroy ()

        # warn the caller we got a result
        self.issue ('result', retval)
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
        


class Picklable:

    def __getstate__ (self):
        dict = copy.copy (self.__dict__)

        for key in self.non_picklable:
            try:
                del dict [key]
            except KeyError: pass
            
        return dict

    
    
class QOperator (QueryEngine.QOperator):
    ''' Allowed operators for a field search '''

    def display (self, box):
        return

    def query_get (self, query):
        return query

    
class QField (QueryEngine.QField):

    CL = {
        'QOperator' : QOperator
        }
    
    ''' A specific field that can be searched '''

    def display (self, box):
        return

    def query_get (self, query):
        return query



class QFields (QueryEngine.QFields, Picklable):

    CL = {
        'QOperator'  : QOperator,
        'QField'     : QField,
        }

    non_picklable = ('w_table', 'w_remove', 'w_add', 'w_rows')

    
    ''' Sets of fields the user can search on '''


    def display (self, box):

        self.current = []
        
        vbox = GtkVBox (spacing = 5)
        
        # the fields are displayed in a table
        self.w_table = GtkTable (1, 3)
        self.w_table.set_row_spacings (5)

        self.row_max = 1
        
        vbox.pack_start (self.w_table, fill = FALSE, expand = FALSE)
        
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

        self.w_add = GtkButton ("Add")
        self.w_add.connect ('clicked', self.field_add)
        hbox.pack_end (self.w_add)
        if self.max == 1:
            self.w_add.set_sensitive (FALSE)
        
        self.w_remove = GtkButton ("Remove")
        self.w_remove.connect ('clicked', self.field_remove)
        self.w_remove.set_sensitive (FALSE)
        
        hbox.pack_end (self.w_remove)
        
        # ...and add a first field, so that it does not look too
        # strange.
        self.w_rows = [ self.set_field (0) ]

        vbox.pack_start (hbox, fill = FALSE, expand = FALSE)
        box.pack_start (frame)
        return


    def field_add (self, * arg):
        r, c = self.w_table ['n_rows'], self.w_table ['n_columns']

        # there is no row left in the GtkTable, allocate one more
        if r == self.row_max:
            self.w_table.resize (r + 1, c)

        self.w_rows.append (self.set_field (self.row_max))
        self.w_table.show_all ()

        self.row_max = self.row_max + 1

        if self.max == self.row_max:
            self.w_add.set_sensitive (FALSE)

        self.w_remove.set_sensitive (TRUE)
        return

    
    def field_remove (self, * arg):
        if self.row_max == 1: return
        
        self.row_max = self.row_max - 1
        if self.row_max == 1: self.w_remove.set_sensitive (FALSE)

        self.w_add.set_sensitive (TRUE)

        for w in self.w_rows [-1]: w.destroy ()
        del self.w_rows [-1]

        self.w_table.show_all ()
        return
    

    def query_get (self, query):

        user_query = []
        
        for f, o, t in self.w_rows:
            fv = f.get_menu ().get_active ().get_data ('value')
            ov = o.get_menu ().get_active ().get_data ('value')
            tv = string.strip (t.gtk_entry ().get_text ())

            if not tv: continue
            
            user_query.append ((fv, ov, tv))
            
        query [self.name] = user_query
            
        return query


    def set_field (self, row):

        # Operator menu
        o_holder = GtkOptionMenu ()
        self.w_table.attach (o_holder, 1, 2, row, row + 1)

        # Field menu
        holder = GtkOptionMenu ()
        menu   = GtkMenu ()

        menu.show ()
        
        for item in self.content:
            w = GtkMenuItem (item.title.encode ('latin-1'))
            w.set_data ('value', item.name)
            
            w.connect ('activate', self.activate_field, item, o_holder)
            w.show ()
            menu.add (w)

        holder.set_menu (menu)


        self.w_table.attach (holder, 0, 1, row, row + 1)

        # ...and attach the entry widget
        text = GnomeEntry (self.name)
        self.w_table.attach (text, 2, 3, row, row + 1)

        # display the first field by default
        holder.set_history (0)
        self.activate_field (None, self.content [0], o_holder)

        return holder, o_holder, text


    def activate_field (self, w, field, holder):
        menu   = GtkMenu ()
        menu.show ()

        for op in field.operators:
            w = GtkMenuItem (op.title.encode ('latin-1'))
            w.set_data ('value', op.name)
            w.show ()
            
            menu.add (w)

        holder.set_menu (menu)
        
        holder.set_history (0)
        return


class QSelection (QueryEngine.QSelection, Picklable):

    ''' A selection between several choices '''

    non_picklable = ('menu', )
    
    def display (self, box):
        hbox = GtkHBox ()
        hbox.set_spacing (5)

        if self.title:
            hbox.pack_start (GtkLabel (self.title.encode ('latin-1')),
                             expand = FALSE, fill = FALSE)
        
        holder = GtkOptionMenu ()
        self.menu = GtkMenu ()
        self.menu.show ()
        
        for item in self.content:
            w = GtkMenuItem (item [1].encode ('latin-1'))
            w.set_data ('value', item [0])
            w.show ()
            
            self.menu.add (w)

        holder.set_menu (self.menu)

        holder.show ()
        holder.set_history (0)
        
        hbox.pack_start (holder, expand = TRUE, fill = TRUE)
        box.pack_start (hbox, expand = TRUE, fill = TRUE)
        return


    def query_get (self, query):
        query [self.name] = self.menu.get_active ().get_data ('value')
        return query


class QToggle (QueryEngine.QToggle, Picklable):

    ''' A selection between two choices '''

    non_picklable = ('w',)
    
    def display (self, box):
        self.w = GtkCheckButton (self.title.encode ('latin-1'))
        self.w.set_active (self.enabled)

        box.pack_start (self.w, expand = TRUE, fill = TRUE)
        return

    def query_get (self, query):
        query [self.name] = self.w.get_active ()
        return query


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

        box.pack_start (frame, expand = FALSE, fill = FALSE)
        return


    def query_get (self, query):
        for part in self.content:
            part.query_get (query)

        return query


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
    
    def query_get (self, q = None):
        query = q or {}

        for part in self.content:
            part.query_get (query)

        return query
        
