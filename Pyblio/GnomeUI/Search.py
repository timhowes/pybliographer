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

from gnome import ui

import gtk

import string, re, sys, traceback, copy

from Pyblio import Types, Search, Config, Connector, TextUI

from Pyblio.GnomeUI import Utils

import gettext
_ = gettext.gettext


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

    
class SearchDialog (ui.Dialog, Connector.Publisher):
    ''' Search Dialog '''
    
    def __init__ (self, parent = None):

        ui.Dialog.__init__ (self, _("Search"),
                            ui.STOCK_PIXMAP_SEARCH,
                            ui.STOCK_BUTTON_CLOSE)
        self.set_policy (TRUE, TRUE, FALSE)
        
        if parent: self.set_parent (parent)

        self.button_connect (0, self.apply_button_cb)
        self.button_connect (1, self.close_cb)
        self.set_default (0)
        self.close_hides (1)
        self.set_close (0)
        
        self.pairs   = []
        
        # user levels
        self.notebook = gtk.Notebook ()
        self.vbox.pack_start (self.notebook, expand = FALSE, fill = FALSE)

        # Simple search
        table = GtkTable (2,2)
        table.set_border_width (5)
        table.set_col_spacings (5)
        
        table.attach (GtkLabel (_("Field")), 0, 1, 0, 1)
        table.attach (GtkLabel (_("Pattern")), 1, 2, 0, 1)
        
        self.field = GtkCombo ()
        table.attach (self.field, 0, 1, 1, 2)

        self.text = GnomeEntry ('match')
        self.text.load_history ()
        
        table.attach (self.text, 1, 2, 1, 2)
        self.text.gtk_entry ().connect ('activate', self.apply_cb)

        # fill the combo
        self.field.set_popdown_strings ([' - any field - '] +
                                        list (Config.get
                                              ('gnome/searched').data) +
                                        [' - type - ', ' - key - '])

        self.notebook.append_page (table, GtkLabel (_("Simple Search")))
        
        # extended search
        hbox = GtkHBox (spacing=5)
        hbox.pack_start (GtkLabel (_("Search command:")),
                         expand=FALSE, fill=FALSE)
        self.expert = GnomeEntry ('expert-search')
        self.expert.gtk_entry ().connect ('activate', self.apply_cb)
        hbox.pack_start (self.expert)
        
        self.notebook.append_page (hbox, GtkLabel (_("Expert Search")))


        # database
        self.root_tree = GtkTree ()
        self.root_tree.connect ('selection_changed', self.selection)
        
        holder = GtkScrolledWindow ()
        holder.set_policy (POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        holder.add_with_viewport (self.root_tree)

        self.vbox.pack_start (holder)

        # connect a menu to the right button
        self.root_tree.connect ('button_press_event', self.popup_menu)

        self.menu = GtkMenu ()
        self.delete_button = Utils.popup_add (self.menu, _("Delete"),  self.search_delete)
        self.menu.show ()

        self.root_item = None
        self.create_root_item (None)

        self.show_all ()
        return


    def update_configuration (self):
        self.text.save_history ()
        return

        
    def create_root_item (self, data):
        if self.root_item:
            self.root_item.remove_subtree ()
            self.root_tree.remove (self.root_item)
            
        # initialize the tree with the full database
        self.root_item = ItemStorage (_("Full database"), None)
        self.root_tree.append (self.root_item)
        self.root_item.show ()
        return


    def close_cb (self, widget):
        self.close ()
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

    
    def popup_menu (self, *arg):
        clist, event, = arg

        if (event.type == GDK.BUTTON_PRESS and event.button == 3):
            sel = self.root_tree.get_selection ()
            if len (sel) == 0:
                self.delete_button.set_sensitive (FALSE)
            else:
                self.delete_button.set_sensitive (TRUE)
                
            self.menu.popup (None, None, None, event.button, event.time)
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


