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
import gtk

import string, re, sys, traceback, copy

from Pyblio import Types, Search, Config, \
     Connector, TextUI, version

from Pyblio.GnomeUI import Utils


class ItemStorage (gtk.TreeModel):

    ''' Extension to TreeItem that stores additional information about
    the search nodes '''
    
    def __init__ (self, name, data):
        TreeItem.__init__ (self, name)

        self.data   = data
        self.parent = None
        self.children = []
        self.tree     = None

        return

    def add (self, new):
        ret = None

        # eventually create the new tree
        if not self.tree:
            self.tree = GtkTree ()
            self.set_subtree (self.tree)
            ret = self.tree
            
        self.children.append (new)
        self.tree.append (new)

        new.parent = self
        return ret

    def remove (self, child):
        # eventually remove the item
        if self.tree:
            # recursively proceed
            child.remove_subtree ()
            
            self.tree.remove_item (child)
            self.children.remove (child)
        
            # clear an empty group
            if len (self.children) == 0:
                self.remove_subtree ()
        return

    def remove_subtree (self):
        if not self.tree: return

        # remove the children also
        for child in copy.copy (self.children):
            # recursively proceed
            child.remove_subtree ()
            
            self.tree.remove_item (child)
            self.children.remove (child)

        self.tree = None
        return
    
    def search (self, name):
        if self == name:
            return self

        for other in self.children:
            ret = other.search (name)
            if ret: return ret
            
        return None

    
class SearchDialog (Connector.Publisher):
    ''' Search Dialog '''
    
    def __init__ (self, parent = None):

        gp = os.path.join (version.prefix, 'glade', 'search.glade')
        
        self.xml = gtk.glade.XML (gp)
        self.xml.signal_autoconnect (self)

        self.w = self.xml.get_widget ('search')
        if parent: self.w.set_transient_for (parent)

        self.pairs   = []

        # fill the combo
        self.field = self.xml.get_widget ('field')
        self.field.set_popdown_strings ([' - any field - '] +
                                        list (Config.get
                                              ('gnome/searched').data) +
                                        [' - type - ', ' - key - '])


        self.root_tree = self.xml.get_widget ('tree')
        
        # database
#        self.root_tree.connect ('selection_changed', self.selection)


        # connect a menu to the right button
        self.menu = gtk.Menu ()
        self.delete_button = Utils.popup_add (self.menu, _("Delete"),  self.search_delete)
        self.menu.show ()


        self.root_item = None
        self.create_root_item (None)

        self.w.show_all ()
        return


    def update_configuration (self):
        return

        
    def create_root_item (self, data):

        return
    
        if self.root_item:
            self.root_item.remove_subtree ()
            self.root_tree.remove (self.root_item)
            
        # initialize the tree with the full database
        self.root_item = ItemStorage (_("Full database"), None)
        self.root_tree.append (self.root_item)
        self.root_item.show ()
        return


    def close_cb (self, widget):
        self.w.hide ()
        return
    

    def apply_button_cb (self, widget):
        if self.notebook.get_current_page () == 0:
            self.text.append_history (TRUE, self.text.gtk_entry ().get_text ())

        self.apply_cb (widget)
        return
    
    def apply_cb (self, widget):
        page = self.notebook.get_current_page ()

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
            
            search = self.expert.gtk_entry ().get_text ()
            try:
                exec ('tester = ' + search, user_global)
            except:
                etype, value, tb = sys.exc_info ()
		traceback.print_exception (etype, value, tb)
                dialog = GnomeErrorDialog (_("internal error during evaluation"),
                                           parent = self)
                return

            test = user_global ['tester']

        # Simple Search
        elif page == 0:
            field = string.lower (self.field.entry.get_text ())
            match = self.text.gtk_entry ().get_text ()
            
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
                dialog = GnomeErrorDialog (_("while compiling %s\nerror: %s") %
                                           (match, err [0]))
                dialog.run_and_close ()
                return
            
        # No search
        else:
            return

        if name is None:
            name = str (test)
            
        # get selection
        selection = self.root_tree.get_selection ()
        
        if len (selection) == 0:
            selection = self.root_item
        else:
            selection = selection [0]

        selection = self.root_item.search (selection)
        if selection.data:
            test = selection.data & test

        item = ItemStorage (name, test)
        item.show ()
        
        tree = selection.add (item)
        
        if tree:
            # if we created a new subtree
            tree.connect ('button_press_event', self.popup_menu)
            selection.expand ()

        selection.tree.select_child (item)
        return

    
    def selection (self, *arg):
        selection = self.root_tree.get_selection ()

        if len (selection) == 0:
            return

        selection = selection [0]
        
        data = self.root_item.search (selection).data
        
        self.issue ('search-data', data)
        return

    
    def popup_menu (self, w, event, *arg):

        if (event.type != gtk.gdk.BUTTON_PRESS or
            event.button != 3): return
        
        self.menu.popup (None, None, None, event.button, event.time)

        #sel = self.root_tree.get_selection ()
        #if len (sel) == 0:
        #    self.delete_button.set_sensitive (FALSE)
        #else:
        #    self.delete_button.set_sensitive (TRUE)
                
        return
    

    def delete_search (self, sel):
        if sel == self.root_item:
            sel.remove_subtree ()
            return
        
        sel.parent.remove (sel)
        return
        
    def search_delete (self, *arg):
        sel = self.root_tree.get_selection () [0]
        sel = self.root_item.search (sel)
        
        self.delete_search (sel)
        return


