# This file is part of pybliographer
# 
# Copyright (C) 1998-2003 Frederic GOBRY
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

import os

from gnome import ui
import gtk, gobject

import string, re, sys, traceback, copy

from Pyblio import Types, Search, Config, \
     Connector, TextUI, version

from Pyblio.GnomeUI import Utils


class ItemStorage:

    ''' Extension to TreeItem that stores additional information about
    the search nodes '''
    
    def __init__ (self, name, data):
        self.name   = name
        self.data   = data
        self.parent = None
        self.children = []
        return

    def add (self, new):
        self.children.append (new)
        new.parent = self
        return

    def remove (self, child):
        self.children.remove (child)

        for c in child.children:
            child.remove (c)
        return

    def search (self, node, path):
        if self == node: return path

        i = 0
        for c in self.children:
            r = c.search (node, path + (i,))
            if r is not None:
                return r
            i = i + 1
        return None

    def get (self, path):
        if len (path) == 1:
            return self.children [path [0]]

        return self.children [path [0]].get (path [1:])


class SearchTree (gtk.GenericTreeModel):

    ''' Data Model of the Search Tree '''
    
    def __init__(self):
	gtk.GenericTreeModel.__init__(self)

        self.tree = ItemStorage (_("Full database"), None)
        return

    def add (self, path, node):
        parent = self.on_get_iter (path)
        parent.add (node)

        path = self.on_get_path (node)
        iter = self.get_iter (path)

        self.emit ('row-inserted', path, iter)
        return path
    
    def remove (self, node):
        path = self.on_get_path (node)

        parent = node.parent
        parent.remove (node)

        self.emit ('row-deleted', path)
        return
    

    def on_get_flags(self):
	'''returns the GtkTreeModelFlags for this particular type of model'''
	return 0
    
    def on_get_n_columns(self):
	'''returns the number of columns in the model'''
	return 1
    
    def on_get_column_type(self, index):
	'''returns the type of a column in the model'''
	return gobject.TYPE_STRING
    
    def on_get_path(self, node):
	'''returns the tree path (a tuple of indices at the various
	levels) for a particular node.'''
	return self.tree.search (node, (0,))
    
    def on_get_iter(self, path):
        '''returns the node corresponding to the given path.  In our
        case, the node is the path'''
        if path == (0,): return self.tree
        if len (path) < 2: return None
        
        return self.tree.get (path [1:])
    
    def on_get_value(self, node, column):
	'''returns the value stored in a particular column for the node'''
	assert column == 0

        if node is None: return ''
	return node.name
    
    def on_iter_next(self, node):
	'''returns the next node at this level of the tree'''
        if node.parent is None: return None

        p = node.parent
        i = p.children.index (node)

        if len (p.children) <= i: return None
        try:
            return p.children [i+1]
        except IndexError:
            return None
    
    def on_iter_children(self, node):
	'''returns the first child of this node'''
	if node == None: return self.tree
        try:
            return node.children [0]
        except IndexError:
            return None
    
    def on_iter_has_child(self, node):
	'''returns true if this node has children'''
	return self.on_iter_n_children (node) > 0
    
    def on_iter_n_children(self, node):
	'''returns the number of children of this node'''
        if node is None: return 1
	return len (node.children)
        
    def on_iter_nth_child(self, node, n):
	'''returns the nth child of this node'''
        if node == None:
            if n == 0: return self.tree
            return None

        try:
            return node.children [n]
        except IndexError:
            return None
        
    def on_iter_parent(self, node):
	'''returns the parent of this node'''
        if node is None: return None
        return node.parent

    
class SearchDialog (Connector.Publisher, Utils.GladeWindow):
    ''' Search Dialog '''

    gladeinfo = { 'name': 'search',
                  'file': 'search.glade',
                  'root': '_w_search'
                  }
    
    def __init__ (self, parent = None):

        Utils.GladeWindow.__init__ (self, parent)

        col = gtk.TreeViewColumn ('field', gtk.CellRendererText (), text = 0)
        self._w_tree.append_column (col)
        self._w_tree.expand_all ()
        
        # the tree model only has the query as displayed data
        self._model = SearchTree ()
        self._w_tree.set_model (self._model)

        # Monitor the selected items
        self._selection = self._w_tree.get_selection ()
        self._selection.connect ('changed', self.selection)
        
        # fill the combo
        self._w_field.set_popdown_strings ([' - any field - '] +
                                          list (Config.get
                                                ('gnome/searched').data) +
                                          [' - type - ', ' - key - '])

        # connect a menu to the right button
        self.menu = gtk.Menu ()
        self.delete_button = Utils.popup_add (self.menu, _("Delete"),
                                              self.search_delete)
        self.menu.show ()

        # We are set up.
        self.show ()
        return


    def show (self):
        ''' Invoked to show the interface again when it has been closed '''
        self._w_search.show ()
        return


    def update_configuration (self):
        return


    def close_cb (self, widget):

        self.size_save ()
        self._w_search.hide ()
        return
    

    def apply_cb (self, widget):
        page = self._w_notebook.get_current_page ()

        name = None
        
        # Expert search
        if page == 1:
            
            user_global = {
                's'   :      TextUI._split_req,
                'has' :      TextUI.has,
                'any_has'  : TextUI.any_has,
                'has_key'  : TextUI.has_key,
                'has_type' : TextUI.has_type,
                'before' :   TextUI.before,
                'after' :    TextUI.after,
                }
            
            search = self._w_expert_text.get_text ()
            try:
                exec ('tester = ' + search, user_global)
            except:
                etype, value, tb = sys.exc_info ()
		traceback.print_exception (etype, value, tb)

                d = gtk.MessageDialog (self._w_search,
                                       gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_MODAL,
                                       gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                       _("internal error during evaluation"))
                d.run ()
                d.destroy ()
                return

            test = user_global ['tester']

        # Simple Search
        elif page == 0:
            
            field = self._w_field_text.get_text ().lower ()
            match = self._w_pattern_text.get_text ()
            
            if match == '': return

            error = 0

            if field == ' - any field - ' or field == '':
                try:
                    test = Search.AnyTester (match)
                except re.error, err:
                    error = 1
                    
                name = 'any ~ ' + match

            elif field == ' - type - ':
                # get the type description
                the_type = Types.get_entry (string.lower (match), 0)

                if the_type is None:
                    err = ['No such Entry type']
                    error = 1
                else:
                    try:
                        test = Search.TypeTester (the_type)
                    except re.error, err:
                        error = 1

            elif field == ' - key - ':
                try:
                    test = Search.KeyTester (match)
                except re.error, err:
                    error = 1

            else:
                try:
                    test = Search.Tester (field, match)
                except re.error, err:
                    error = 1
                
            if error:
                d = gtk.MessageDialog (self._w_search,
                                       gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_MODAL,
                                       gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                       _("while compiling %s\nerror: %s") %
                                       (match, err [0]))
                d.run ()
                d.destroy ()
                return
            
        # No search
        else:
            return

        if name is None:
            name = str (test)
            
        s, i = self._selection.get_selected ()
        if i is None: i = (0,)
        else:         i = s.get_path (i)
        
        selection = self._model.on_get_iter (i)
        
        if selection.data: test = selection.data & test

        item = ItemStorage (name, test)
        path = self._model.add (i, item)

        self._w_tree.expand_row (path [:-1], True)
        self._selection.select_path (path)
        return

    
    def selection (self, *arg):
        s, i = self._selection.get_selected ()
        if i is None: return
        
        data = self._model.on_get_iter (s.get_path (i)).data

        self.issue ('search-data', data)
        return

    
    def popup_menu (self, w, event, *arg):

        if (event.type != gtk.gdk.BUTTON_PRESS or
            event.button != 3): return
        
        self.menu.popup (None, None, None, event.button, event.time)

        s, i = self._selection.get_selected ()
        self.delete_button.set_sensitive (i is not None)
        return
    

    def search_delete (self, *arg):
        s, i = self._selection.get_selected ()
        if i is None: return
        
        selection = self._model.on_get_iter (s.get_path (i))
        if selection.data is None: return
        
        self._model.remove (selection)
        return


