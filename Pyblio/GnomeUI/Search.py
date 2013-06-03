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


""" This module implements the Search dialog """

import os

from gi.repository import Gdk, Gtk, GObject

import string, re, sys, traceback, copy

from Pyblio import Types, Search, Config, \
     Connector, TextUI, version

from Pyblio.GnomeUI import Utils


class SearchDialog (Connector.Publisher, Utils.GladeWindow):

    ''' The actual Search Dialog. This dialog is created once, and
    only hidden, not destroyed, to keep it always available in the
    same state.

    This dialog emits a "search-data" signal when a new search
    criterion is selected.
    
    '''

    gladeinfo = { 'file': 'search.ui',
                  'root': '_w_search',
                  'name': 'search'
                  }
    
    def __init__(self, parent=None):
        Utils.GladeWindow.__init__(self, parent)

        # the tree model contains a string that explains the query,
        # and a python object representing the actual query.
        
        self._model = Gtk.TreeStore(str, GObject.TYPE_PYOBJECT)
        self._w_tree.set_model(self._model)

        # the view does not display the python column, of course.
        col = Gtk.TreeViewColumn('field', Gtk.CellRendererText(), text=0)
        self._w_tree.append_column(col)

        self._w_tree.expand_all()
        
        # The root of the search tree is the full database
        self._model.append(None, (_("Full database"), None))


        # Monitor the selected items
        self._selection = self._w_tree.get_selection()
        self._selection.connect('changed', self.selection)

        field_items = [' - any field - '] + \
                      list(Config.get('gnome/searched').data) + \
                      [' - type - ', ' - key - ']
        for fields in field_items:
            self._w_field.append_text(fields)

        self._w_field.set_active(0)

        # connect a menu to the right button
        self.menu = Gtk.Menu()
        self.delete_button = Utils.popup_add(self.menu, _("Delete"),
                                             self.search_delete)

        # We are set up.
        self.show()


    def show(self):
        ''' Invoked to show the interface again when it has been closed '''
        
        self._w_search.show()
        return


    def close_cb(self, widget):
        ''' Invoked to hide the interface when clicking on "Close" '''

        self.size_save()
        self._w_search.hide()
        return
    

    def apply_cb(self, widget):

        ''' Construct the new query and add it to the query tree '''
        
        page = self._w_notebook.get_current_page()

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
            
            search = self._w_expert.get_active_text().encode('latin-1')
            
            try:
                exec ('tester = ' + search, user_global)
            except:
                etype, value, tb = sys.exc_info()
                traceback.print_exception(etype, value, tb)

                d = Gtk.MessageDialog(self._w_search,
                                      Gtk.DialogFlags.DESTROY_WITH_PARENT | Gtk.DialogFlags.MODAL,
                                      Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                                      _("internal error during evaluation"))
                d.run()
                d.destroy()
                return

            test = user_global['tester']

        # Simple Search
        elif page == 0:
            
            field = self._w_field.get_active_text().lower()
            match = self._w_pattern.get_active_text()
            
            if match == '': return

            error = 0

            if field == ' - any field - ' or field == '':
                try:
                    test = Search.AnyTester(match.encode('latin-1'))
                except re.error, err:
                    error = 1
                    
                name = 'any ~ ' + match

            elif field == ' - type - ':
                # get the type description
                the_type = Types.get_entry(string.lower(match), 0)

                if the_type is None:
                    err = ['No such Entry type']
                    error = 1
                else:
                    try:
                        test = Search.TypeTester(the_type)
                    except re.error, err:
                        error = 1

            elif field == ' - key - ':
                try:
                    test = Search.KeyTester(match)
                except re.error, err:
                    error = 1

            else:
                try:
                    test = Search.Tester(field, match)
                except re.error, err:
                    error = 1
                
            if error:
                d = Gtk.MessageDialog(self._w_search,
                                      Gtk.DialogFlags.DESTROY_WITH_PARENT | Gtk.DialogFlags.MODAL,
                                      Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                                      _("while compiling %s\nerror: %s") %
                                      (match, err [0]))
                d.run()
                d.destroy()
                return
            
        # No search
        else:
            return

        if name is None:
            name = str(test)

        # Get the path to the query being refined
        s, parent = self._selection.get_selected()
        if parent is None: parent = s.get_iter((0,))

        parent_path = s.get_path(parent)

        # If we are refining a previous query, build the new query as
        # a logical and of the previous and new query.
        
        current = self._model[parent_path][1]
        if current: test = current & test

        # Add the new query in the tree and ensure it is visible and selected.
        child = self._model.append(parent, (name, test))
        path = s.get_path(child)
        
        self._w_tree.expand_row(parent_path, True)
        self._selection.select_path(path)
        return

    
    def selection(self, *arg):

        ''' Called when the user clicks on a specific query '''
        
        s, i = self._selection.get_selected()
        if i is None: return
        
        data = self._model[s.get_path (i)]

        self.issue('search-data', * data)
        return

    
    def popup_menu(self, w, event, *arg):

        ''' Called when the user right-clicks in the query tree '''
        
        if (event.type != Gdk.EventType.BUTTON_PRESS or
            event.button != 3): return
        
        self.menu.popup (None, None, None, None, event.button, event.time)

        # Only allow removal when a valid query is selected
        s, i = self._selection.get_selected()
        self.delete_button.set_sensitive(i is not None and
                                         s [i][1] is not None)
        return
    

    def search_delete(self, *arg):
        
        ''' Called when the user deletes a query in the tree '''

        s, i = self._selection.get_selected()
        if i is None: return

        # Do not allow removal of the root.
        if s [i][1] is None: return
        
        self._model.remove(i)
        return


