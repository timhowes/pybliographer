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

''' This module defines a Document class, corresponding to a
GnomeMDI Child '''

from gnome.ui import *
from gtk import *
from gnome import config

from Pyblio.GnomeUI import Index, Entry, Utils, FileSelector
from Pyblio import Connector, Open, Exceptions

import gettext, os, string

_ = gettext.gettext

class Document (Connector.Publisher):
    
    def __init__ (self, database, version = '0.0'):
        
        self.w = GnomeApp ('Pybliographic', 'Pybliographic')

        self.w.connect ('delete_event', self.close_document)
        
        file_menu = [
            UIINFO_MENU_NEW_ITEM     (_("New"), None, self.new_document),
            UIINFO_MENU_OPEN_ITEM    (self.open_document),
            UIINFO_MENU_SAVE_ITEM    (self.save_document),
            UIINFO_MENU_SAVE_AS_ITEM (self.save_document_as),
            UIINFO_SEPARATOR,
            UIINFO_SUBTREE           (_("Previous Documents"), []),
            UIINFO_SEPARATOR,
            UIINFO_MENU_CLOSE_ITEM   (self.close_document),
            UIINFO_MENU_EXIT_ITEM    (self.exit_application)
            ]
        
        help_menu = [
            UIINFO_ITEM_STOCK (_("About..."), None, self.about, STOCK_MENU_ABOUT),
            UIINFO_ITEM_STOCK (_("Submit a Bug Report"), None,
                               self.exec_bug_buddy, STOCK_MENU_TRASH_FULL),
            UIINFO_HELP ('pybliographic')
            ]

        edit_menu = [
            UIINFO_MENU_CUT_ITEM        (self.cut_entry),
            UIINFO_MENU_COPY_ITEM       (self.copy_entry),
            UIINFO_MENU_PASTE_ITEM      (self.paste_entry),
            UIINFO_MENU_CLEAR_ITEM      (self.clear_entries),
            UIINFO_MENU_SELECT_ALL_ITEM (self.select_all_entries),
            UIINFO_SEPARATOR,
            UIINFO_ITEM_STOCK(_("Add..."), None, self.add_entry,    STOCK_MENU_NEW),
            UIINFO_ITEM      (_("Edit..."),None, self.edit_entry),
            UIINFO_ITEM_STOCK(_("Delete"), None, self.delete_entry, STOCK_MENU_TRASH),
            UIINFO_SEPARATOR,
            UIINFO_MENU_FIND_ITEM (self.find_entries),
            ]

        menus = [
            UIINFO_SUBTREE (_("File"),     file_menu),
            UIINFO_SUBTREE (_("Edit"),     edit_menu),
            UIINFO_SUBTREE (_("Help"),     help_menu)
            ]
        
        toolbar = [
            UIINFO_ITEM_STOCK(_("Open"),  None, self.open_document,  STOCK_PIXMAP_OPEN),
            UIINFO_ITEM_STOCK(_("Save"),  None, self.save_document,  STOCK_PIXMAP_SAVE),
            UIINFO_SEPARATOR,
            UIINFO_ITEM_STOCK(_("Find"),  None, self.find_entries,   STOCK_PIXMAP_SEARCH),
            UIINFO_SEPARATOR,
            UIINFO_ITEM_STOCK(_("Close"), None, self.close_document, STOCK_PIXMAP_CLOSE),
            ]

        # Put information in Paned windows
        self.paned = GtkVPaned ()
        
        Utils.init_colors (self.paned.get_colormap ())

        # The Index list
        self.index = Index.Index ()
        self.paned.add1 (self.index.w)

        self.index.Subscribe ('new-entry',      self.add_entry)
        self.index.Subscribe ('edit-entry',     self.edit_entry)
        self.index.Subscribe ('delete-entry',   self.delete_entry)
        self.index.Subscribe ('select-entry',   self.update_display)
        self.index.Subscribe ('select-entries', self.freeze_display)

        # The text area
        self.display = Entry.Entry ()
        self.paned.add2 (self.display.w)

        # Status bar
        self.statusbar = GnomeAppBar (FALSE, TRUE)
        
        # fill the main app
        self.w.create_menus   (menus)
        self.w.create_toolbar (toolbar)
        
        self.w.set_contents   (self.paned)
        self.w.set_statusbar  (self.statusbar)

        # set window size
        ui_width  = config.get_int ('Pybliographer/UI/Width=-1')
        ui_height = config.get_int ('Pybliographer/UI/Height=-1')

        if ui_width != -1 and ui_height != -1:
            self.w.set_default_size (ui_width, ui_height)

        # set paned size
        paned_height = config.get_int ('Pybliographer/UI/Paned=-1')
        self.paned.set_position (paned_height)
        
        self.w.show_all ()
        
        # application variables
        self.data    = database
        self.version = version
        self.changed = 0
        
        # fill the Index with the current entries
        self.index.display (self.data.iterator ())

        self.update_status ()
        return

    def update_status (self):
        if self.data.key is None:
            text = _("New database")
        else:
            text = _("Database `%s'") % str (self.data.key)

        if self.changed:
            text = text + _(" [modified]")

        self.statusbar.set_default (text)
        return
    
    def confirm (self):
        if self.changed:
            cb = Utils.Callback ()
            self.w.question (_("The database has been modified.\nDiscard changes ?"),
                             cb.callback)

            return cb.answer ()
        
        return 1
        
    def new_document (self, * arg):
        self.issue ('new-document', self)
        return
    
    def open_document (self, * arg):
        if not self.confirm (): return

        # get a new file name
        (url, how) = FileSelector.URLFileSelection (_("Open file")).run ()

        Utils.set_cursor (self.w, 'clock')
        
        try:
            data = Open.bibopen (url, how = how)
        except (Exceptions.ParserError, Exceptions.FormatError), error:
            Utils.set_cursor (self.w, 'normal')
            Utils.error_dialog (_("Open error"), error)
            return

        Utils.set_cursor (self.w, 'normal')
        
        self.data    = data
        self.changed = 0
        self.index.display (self.data.iterator ())

        # eventually warn interested objects
        self.issue ('open-document', self)
        return
    
    def save_document (self, * arg):
        if self.data.key is None:
            self.save_document_as ()
            return

        Utils.set_cursor (self.w, 'clock')
        try:
            self.data.update ()
        except:
            Utils.set_cursor (self.w, 'normal')
            self.w.error (_("An internal error occured during saving\nTry to Save As..."))
            return

        Utils.set_cursor (self.w, 'normal')
        self.changed = 0
        self.update_status ()
        return
    
    
    def save_document_as (self, * arg):
        # get a new file name
        (url, how) = FileSelector.URLFileSelection (_("Open file"),
                                                    url = FALSE, has_auto = FALSE).run ()

        if os.path.exists (url):
            cb = Utils.Callback ()
            self.w.question (_("The file `%s' already exists.\nOverwrite it ?") % url,
                             cb.callback)

            if not cb.answer (): return

        try:
            file = open (url, 'w')
        except IOError, error:
            self.w.error (_("During opening:\n%s") % error [1])
            return

        Utils.set_cursor (self.w, 'clock')
        
        Open.bibwrite (self.data.iterator (), out = file, how = how)
        file.close ()
        
        if self.data.key is None:
            # we wrote an anonymous database. Lets reopen it !
            self.data = Open.bibopen (url, how = how)
            
        Utils.set_cursor (self.w, 'normal')

        self.changed = 0
        self.update_status ()
        return
                                      
    def close_document (self, * arg):
        self.issue ('close-document', self)
        return

    def close_document_request (self):
        return self.confirm ()
    
    def exit_application (self, * arg):
        self.issue ('exit-application', self)
        return
    
    def cut_entry (self, * arg):
        pass
    
    def copy_entry (self, * arg):
        pass
    
    def paste_entry (self, * arg):
        pass
    
    def clear_entries (self, * arg):
        pass
    
    def select_all_entries (self, * arg):
        pass
    
    def add_entry (self, * arg):
        pass
    
    def edit_entry (self, * arg):
        pass
    
    def delete_entry (self, * arg):
        pass
    
    def find_entries (self, * arg):
        pass
    
    def update_display (self, key):
        self.display.w.set_sensitive (1)
        self.display.display (self.data [key])
        return
    
    def freeze_display (self, keys):
        self.display.w.set_sensitive (0)
        return

    def update_configuration (self):
        ''' save current informations about the program '''
        
        # Save the graphical aspect of the interface
        # 1.- Window size
        alloc = self.w.get_allocation ()
        config.set_int ('Pybliographer/UI/Width',  alloc [2])
        config.set_int ('Pybliographer/UI/Height', alloc [3])

        # 2.- Proportion betzeen list and text
        height = self.paned.children () [0].get_allocation () [3]
        config.set_int ('Pybliographer/UI/Paned', height)
        config.sync ()
        return
    
    def exec_bug_buddy (self, *args):
        ''' run bug-buddy with the minimal configuration data '''
        
        # search the program in the current path
        exists = 0
        for d in string.split (os.environ ['PATH'], ':'):
            if os.path.exists (os.path.join (d, 'bug-buddy')):
                exists = 1
                break

        if not exists:
            self.w.error (_("Please install bug-buddy\nto use this feature"))
            return
        
        command = 'bug-buddy --package=pybliographer --package-ver=%s &' % self.version
        
        os.system (command)
        return
    
    def about (self, *arg):
        about = GnomeAbout ('Pybliographic', self.version,
                            _("This program is copyrighted under the GNU GPL"),
                            ['Frédéric Gobry'],
                            _("Gnome interface to the Pybliographer system."),
                            'pybliographic-logo.png')
        
        link = GnomeHRef ('http://www.gnome.org/pybliographer', _("Pybliographer Home Page"))
        link.show ()
        about.vbox.pack_start (link)
        about.show()
        return

