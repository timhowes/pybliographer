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

''' This module defines a Document class '''

from gnome.ui import *
from gtk import *
from gnome import config

from Pyblio.GnomeUI import Index, Entry, Utils, FileSelector, Editor
from Pyblio.GnomeUI import Search, Format
from Pyblio.GnomeUI.Sort import SortDialog
from Pyblio.GnomeUI.Config import ConfigDialog
from Pyblio.GnomeUI.Fields import FieldsDialog, EntriesDialog

from Pyblio import Connector, Open, Exceptions, Selection, Sort, Base, Config
from Pyblio import version, Fields, Types

import Pyblio.Style.Utils

import gettext, os, string, copy, types, sys, traceback

_ = gettext.gettext

class Document (Connector.Publisher):
    
    def __init__ (self, database):
        
        self.w = GnomeApp ('Pybliographic', 'Pybliographic')

        self.w.connect ('delete_event', self.close_document)
        
        file_menu = [
            UIINFO_MENU_NEW_ITEM     (_("_New"), None, self.new_document),
            UIINFO_MENU_OPEN_ITEM    (self.ui_open_document),
            UIINFO_ITEM              (_("_Merge with..."),None, self.merge_database),
            UIINFO_MENU_SAVE_ITEM    (self.save_document),
            UIINFO_MENU_SAVE_AS_ITEM (self.save_document_as),
            UIINFO_SEPARATOR,
            UIINFO_SUBTREE           (_("_Previous Documents"), []),
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
            UIINFO_ITEM_STOCK(_("_Add..."), None, self.add_entry,    STOCK_MENU_NEW),
            UIINFO_ITEM      (_("_Edit..."),None, self.edit_entry),
            UIINFO_ITEM_STOCK(_("_Delete"), None, self.delete_entry, STOCK_MENU_TRASH),
            UIINFO_SEPARATOR,
            UIINFO_MENU_FIND_ITEM (self.find_entries),
            UIINFO_ITEM           (_("S_ort..."),None, self.sort_entries),
            ]

        cite_menu = [
            UIINFO_ITEM_STOCK(_("_Cite"), None, self.lyx_cite,            STOCK_MENU_CONVERT),
            UIINFO_ITEM_STOCK(_("_Format..."), None, self.format_entries, STOCK_MENU_REFRESH),
            ]

        settings_menu = [
            UIINFO_ITEM      (_("_Fields..."),  None, self.set_fields),
            UIINFO_ITEM      (_("_Entries..."), None, self.set_entries),
            UIINFO_SEPARATOR,
            UIINFO_MENU_PREFERENCES_ITEM   (self.set_preferences),
            ]
            
        menus = [
            UIINFO_SUBTREE (_("_File"),     file_menu),
            UIINFO_SUBTREE (_("_Edit"),     edit_menu),
            UIINFO_SUBTREE (_("_Cite"),     cite_menu),
            UIINFO_SUBTREE (_("_Settings"), settings_menu),
            UIINFO_SUBTREE (_("_Help"),     help_menu)
            ]
        
        toolbar = [
            UIINFO_ITEM_STOCK(_("Open"),  None, self.ui_open_document, STOCK_PIXMAP_OPEN),
            UIINFO_ITEM_STOCK(_("Save"),  None, self.save_document,    STOCK_PIXMAP_SAVE),
            UIINFO_SEPARATOR,
            UIINFO_ITEM_STOCK(_("Find"),  None, self.find_entries,     STOCK_PIXMAP_SEARCH),
            UIINFO_ITEM_STOCK(_("Cite"), None, self.lyx_cite,          STOCK_MENU_CONVERT),
            UIINFO_SEPARATOR,
            UIINFO_ITEM_STOCK(_("Close"), None, self.close_document,   STOCK_PIXMAP_CLOSE),
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
        self.index.Subscribe ('drag-received',  self.drag_received)
        self.index.Subscribe ('drag-moved',     self.drag_moved)
        self.index.Subscribe ('click-on-field', self.sort_by_field)

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
        ui_width  = config.get_int ('Pybliographic/UI/Width=-1')
        ui_height = config.get_int ('Pybliographic/UI/Height=-1')

        if ui_width != -1 and ui_height != -1:
            self.w.set_default_size (ui_width, ui_height)

        # set paned size
        paned_height = config.get_int ('Pybliographic/UI/Paned=-1')
        self.paned.set_position (paned_height)
        
        self.w.show_all ()
        
        # application variables
        self.data      = database
        self.selection = Selection.Selection ()
        self.search_dg = None
        self.format_dg = None
        self.sort_dg   = None
        self.lyx       = None
        self.changed   = 0
        self.directory = None
        
        self.redisplay_index ()
        return


    def set_preferences (self, * arg):
        w = ConfigDialog (self.w)
        return


    def set_fields (self, * arg):
        w = FieldsDialog (self.w)
        return
    

    def set_entries (self, * arg):
        w = EntriesDialog (self.w)
        return
    

    def update_history (self, history):
        ''' fill the " Previous Documents " menu with the specified list of documents '''
        
        self.w.remove_menus (_("File") + '/' + _("Previous Documents") + '/',
                             100)

        menuinfo = []
        for item in history:
            def callback (widget, self = self, file = item [0], how = item [1]):
                if not self.confirm (): return
                self.open_document (file, how)
                return

            filename = item [0]
            
            menuinfo.append (UIINFO_ITEM_STOCK (filename, None, callback, STOCK_MENU_OPEN))

        self.w.insert_menus (_("File") + '/' + _("Previous Documents") + '/',
                             menuinfo)
        return

    
    def redisplay_index (self, changed = -1):
        ''' redisplays the index. If changed is specified, set the
        self.changed status to the given value '''
        
        if changed != -1:
            self.changed = changed
        
        self.index.display (self.selection.iterator (self.data.iterator ()))
        self.update_status ()
        return


    def format_query (self, style, format, output):
        try:
            file = open (output, 'w')
        except IOError, err:
            self.w.error (_("can't open file `%s' for writing:\n%s")
                          % (output, str (err)))
            return
        
        entries = map (lambda x: x.key, self.index.selection ())
        
        if not entries:
            entries = self.data.keys ()

        url = Fields.URL (style)
        
        Pyblio.Style.Utils.generate (url, format, self.data, entries, file)
        return


    def format_entries (self, * arg):
        if self.format_dg is None:
            self.format_dg = Format.FormatDialog (self.w)
            self.format_dg.Subscribe ('format-query', self.format_query)
            
        self.format_dg.show ()
        return

    
    def update_status (self, status = -1):
        ''' redisplay status bar according to the current status '''

        if status != -1: self.changed = status
        
        if self.data.key is None:
            text = _("New database")
        else:
            text = str (self.data.key)

        li = len (self.index)
        ld = len (self.data)
        
        if li == ld:
            if   ld == 0: num = _("[no entry]")
            elif ld == 1: num = _("[1 entry]")
            else:         num = _("[%d entries]")    %  ld
        else:
            if   ld == 0: num = _("[no entry]")
            elif ld == 1: num = _("[%d/1 entry]")    % li
            else:         num = _("[%d/%d entries]") % (li, ld)

        text = text + ' ' + num
        
        if self.changed:
            text = text + ' ' + _("[modified]")

        self.statusbar.set_default (text)
        return

    
    def confirm (self):
        ''' eventually ask for modification cancellation '''
        
        if self.changed:
            return Utils.Callback (_("The database has been modified.\nDiscard changes ?"),
                                   self.w).answer ()
        
        return 1

        
    def new_document (self, * arg):
        ''' callback corresponding to the "New Document" button '''
        
        self.issue ('new-document', self)
        return


    def merge_database (self, * arg):
        ''' add all the entries of another database to the current one '''
        # get a new file name
        (url, how) = FileSelector.URLFileSelection (_("Merge file"),
                                                    url = TRUE, has_auto = TRUE).run ()

        if url is None: return
        
        try:
            iterator = Open.bibiter (url, how = how)
            
        except (Exceptions.ParserError,
                Exceptions.FormatError,
                Exceptions.FileError), error:
            
            Utils.error_dialog (_("Open error"), error,
                                parent = self.w)
            return

        # loop over the entries
        errors = []
        try:
            entry = iterator.first ()
        except Exceptions.ParserError, msg:
            errors = errors + msg.errors
        
        while entry:
            self.data.add (entry)
            while 1:
                try:
                    entry = iterator.next ()
                    break
                except Exceptions.ParserError, msg:
                    errors = errors + list (msg.errors)
                    continue

        self.redisplay_index (1)

        if errors:
            Utils.error_dialog (_("Merge status"), string.join (errors, '\n'),
                                parent = self.w)
        return

        
    def ui_open_document (self, * arg):
        ''' callback corresponding to "Open" '''
        
        if not self.confirm (): return

        # get a new file name
        (url, how) = FileSelector.URLFileSelection (_("Open file"),
                                                    directory = self.directory).run ()

        if url is None: return
        self.open_document (url, how)

        # memorize the current path in the case of a file
        url = Fields.URL (url)
        if url.url [0] == 'file':
            self.directory = os.path.split (url.url [2]) [0] + '/'
        return

    
    def open_document (self, url, how = None):
        
        Utils.set_cursor (self.w, 'clock')
        
        try:
            data = Open.bibopen (url, how = how)
            
        except (Exceptions.ParserError,
                Exceptions.FormatError,
                Exceptions.FileError), error:
            
            Utils.set_cursor (self.w, 'normal')
            Utils.error_dialog (_("Open error"), error,
                                parent = self.w)
            return

        Utils.set_cursor (self.w, 'normal')
        
        self.data    = data
        self.redisplay_index (0)
        
        # eventually warn interested objects
        self.issue ('open-document', self)
        return
    
    def save_document (self, * arg):
        if self.data.key is None:
            self.save_document_as ()
            return

        Utils.set_cursor (self.w, 'clock')
        try:
            try:
                self.data.update (self.selection.sort)
            except (OSError, IOError), error:
                Utils.set_cursor (self.w, 'normal')
                self.w.error (_("Unable to save `%s':\n%s") % (str (self.data.key),
                                                               str (error)))
                return
        except:
            etype, value, tb = sys.exc_info ()
            traceback.print_exception (etype, value, tb)
            
            Utils.set_cursor (self.w, 'normal')
            self.w.error (_("An internal error occured during saving\nTry to Save As..."))
            return

        Utils.set_cursor (self.w, 'normal')

        self.update_status (0)
        return
    
    
    def save_document_as (self, * arg):
        # get a new file name
        (url, how) = FileSelector.URLFileSelection (_("Save As..."),
                                                    url = FALSE, has_auto = FALSE).run ()

        if url is None: return
            
        if os.path.exists (url):
            if not Utils.Callback (_("The file `%s' already exists.\nOverwrite it ?")
                                   % url, parent = self.w).answer ():
                return

        try:
            file = open (url, 'w')
        except IOError, error:
            self.w.error (_("During opening:\n%s") % error [1])
            return

        Utils.set_cursor (self.w, 'clock')

        iterator = Selection.Selection (sort = self.selection.sort)
        Open.bibwrite (iterator.iterator (self.data.iterator ()),
                       out = file, how = how)
        file.close ()
        
        if self.data.key is None:
            # we wrote an anonymous database. Lets reopen it !
            try:
                self.data = Open.bibopen (url, how = how)
                
            except (Exceptions.ParserError,
                    Exceptions.FormatError,
                    Exceptions.FileError), error:
                    
                Utils.set_cursor (self.w, 'normal')
                Utils.error_dialog (_("Reopen error"), error,
                                    parent = self.w)
                return
            
            self.redisplay_index ()
            self.issue ('open-document', self)
            
        Utils.set_cursor (self.w, 'normal')

        self.update_status (0)
        return

                                      
    def close_document (self, * arg):
        self.issue ('close-document', self)
        return


    def close_document_request (self):
        return self.confirm ()

    
    def exit_application (self, * arg):
        self.issue ('exit-application', self)
        return


    def drag_moved (self, entries):
        if not entries: return
        
        for e in entries:
            del self.data [e.key]

        self.redisplay_index (1)
        return

    
    def drag_received (self, entries):
        for entry in entries:
            
            if self.data.would_have_key (entry.key):
                if not Utils.Callback (_("An entry called `%s' already exists.\nRename and add it anyway ?")
                                       % entry.key.key, parent = self.w).answer ():
                    continue
                
            self.changed = 1
            self.data.add (entry)

        self.redisplay_index ()
        return

                
    def cut_entry (self, * arg):
        entries = self.index.selection ()
        if not entries: return
        
        self.index.selection_copy (entries)
        for entry in entries:
            del self.data [entry.key]
            
        self.redisplay_index (1)
        pass

    
    def copy_entry (self, * arg):
        self.index.selection_copy (self.index.selection ())
        return

    
    def paste_entry (self, * arg):
        self.index.selection_paste ()
        return

    
    def clear_entries (self, * arg):
        if len (self.data) == 0: return

        if not Utils.Callback (_("Really remove all the entries ?"),
                               parent = self.w).answer ():
            return

        keys = self.data.keys ()
        for key in keys:
            del self.data [key]

        self.redisplay_index (1)
        return
    
    
    def select_all_entries (self, * arg):
        self.index.select_all ()
        return
    
    
    def add_entry (self, * arg):
        entry = self.data.new_entry (Config.get ('base/defaulttype').data)
        
        edit = Editor.Editor (self.data, entry, self.w, _("Create new entry"))
        edit.Subscribe ('commit-edition', self.commit_edition)
        return

    
    def edit_entry (self, entries):
        if not (type (entries) is types.ListType):
            entries = self.index.selection ()
        
        l = len (entries)

        if l == 0: return
        
        if l > 5:
            if not Utils.Callback (_("Really edit %d entries ?" % l)):
                return

        for entry in entries:
            edit = Editor.Editor (self.data, entry, self.w)
            edit.Subscribe ('commit-edition', self.commit_edition)

        return


    def commit_edition (self, old, new):
        ''' updates the database and the display '''

        if old.key != new.key:
            if self.data.has_key (old.key):
                del self.data [old.key]

        if new.key:
            self.data [new.key] = new
        else:
            self.data.add (new)

        self.redisplay_index (1)
        self.freeze_display (None)
        return
    
    
    def delete_entry (self, * arg):
        ''' removes the selected list of items after confirmation '''
        entries = self.index.selection ()

        l = len (entries)
        if l == 0: return
        
        if l > 1:
            question = _("Remove all the %d entries ?") % len (entries)
        else:
            question = _("Remove entry `%s' ?") % entries [0].key.key
            
        if not Utils.Callback (question,
                               parent = self.w).answer ():
            return

        for entry in entries:
            del self.data [entry.key]
            
        self.redisplay_index (1)
        return
    
    
    def find_entries (self, * arg):
        if self.search_dg is None:
            self.search_dg = Search.SearchDialog (self.w)
            self.search_dg.Subscribe ('search-data', self.limit_view)
        else:
            self.search_dg.show ()
        return


    def limit_view (self, search):
        self.selection.search = search
        self.redisplay_index ()
        return

    
    def sort_entries (self, * arg):
        if self.sort_dg is None:
            self.sort_dg = SortDialog (self.selection.sort, self.w)
            self.sort_dg.Subscribe ('sort-data', self.sort_view)
        self.sort_dg.show ()
        return


    def sort_view (self, sort):
        self.selection.sort = Sort.Sort (sort)
        self.redisplay_index ()
        return
    

    def sort_by_field (self, field):
        self.selection.sort = Sort.Sort ([Sort.FieldSort (field)])
        self.redisplay_index ()
        return


    def lyx_cite (self, * arg):
        entries = self.index.selection ()
        if not entries: return
        
        if self.lyx is None:
            from Pyblio import LyX

            try:
                self.lyx = LyX.LyXClient ()
            except IOError, msg:
                self.w.error (_("Can't connect to LyX:\n%s") % msg [1])
                return

        keys = string.join (map (lambda x: x.key.key, entries), ', ')
        try:
            self.lyx ('citation-insert', keys)
        except IOError, msg:
            self.w.error (_("Can't connect to LyX:\n%s") % msg [1])
        return
    

    def update_display (self, entry):
        self.display.display (entry)
        return

    
    def freeze_display (self, entry):
        self.display.clear ()
        return


    def update_configuration (self):
        ''' save current informations about the program '''
        
        # Save the graphical aspect of the interface
        # 1.- Window size
        alloc = self.w.get_allocation ()
        config.set_int ('Pybliographic/UI/Width',  alloc [2])
        config.set_int ('Pybliographic/UI/Height', alloc [3])

        # 2.- Proportion betzeen list and text
        height = self.paned.children () [0].get_allocation () [3]
        config.set_int ('Pybliographic/UI/Paned', height)
        config.sync ()
        return

    
    def exec_bug_buddy (self, *args):
        ''' run bug-buddy in background, with the minimal configuration data '''
        
        # search the program in the current path
        exists = 0
        for d in string.split (os.environ ['PATH'], ':'):
            if os.path.exists (os.path.join (d, 'bug-buddy')):
                exists = 1
                break

        if not exists:
            self.w.error (_("Please install bug-buddy\nto use this feature"))
            return
        
        command = 'bug-buddy --package=pybliographer --package-ver=%s &' % version.version
        
        os.system (command)
        return

    
    def about (self, *arg):
        about = GnomeAbout ('Pybliographic', version.version,
                            _("This program is copyrighted under the GNU GPL"),
                            ['Frédéric Gobry'],
                            _("Gnome interface to the Pybliographer system."),
                            'pybliographic-logo.png')
        about.set_parent (self.w)
        
        link = GnomeHRef ('http://www.gnome.org/pybliographer',
                          _("Pybliographer Home Page"))
        link.show ()
        about.vbox.pack_start (link)
        about.show()
        return

