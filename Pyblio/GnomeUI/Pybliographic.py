# This file is part of pybliographer
# 
# Copyright (C) 1998 Frederic GOBRY
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

import string, os, urlparse, gettext

_ = gettext.gettext

from gnome.ui import *
from gnome import config

from gtk import *
import GtkExtra, GDK, GTK

from Pyblio import Open, Types, Base, Config, Autoload

from Pyblio.GnomeUI import Utils

from Pyblio.GnomeUI.Database import *
from Pyblio.GnomeUI.Entry  import *
from Pyblio.GnomeUI.Search import *


class URLFileSelection (GtkFileSelection):
    ''' Extended file selection dialog, with an URL field and a type
    selector. '''
    
    def __init__(self, title = _("File"), url=TRUE, modal=TRUE, has_auto=TRUE):
        
        GtkFileSelection.__init__(self)
        self.set_title (title)
        
        self.connect('destroy', self.quit)
        self.connect('delete_event', self.quit)
        self.cancel_button.connect('clicked', self.quit)
        self.ok_button.connect('clicked', self.ok_cb)

        if modal:
            grab_add (self)

        self.ret = None
        self.url = None
        
        vbox = self.main_vbox
        
        # url handler
        if url:
            hbox = GtkHBox ()
            hbox.set_spacing (5)
            hbox.pack_start (GtkLabel ('URL:'), expand = FALSE, fill = FALSE)
            self.url = GtkEntry ()
            hbox.pack_start (self.url)
            vbox.pack_start (hbox, expand = FALSE, fill = FALSE)

        # type selector
        hbox = GtkHBox ()
        hbox.set_spacing (5)
        hbox.pack_start (GtkLabel (_("Bibliography type:")),
                         expand = FALSE, fill = FALSE)
        self.menu = GtkOptionMenu ()
        hbox.pack_start (self.menu)
        vbox.pack_start (hbox, expand = FALSE, fill = FALSE)

        # menu content
        menu = GtkMenu ()
        self.menu.set_menu (menu)
        
        liste = Autoload.available ('format')
        liste.sort ()
        
        if has_auto:
            Utils.popup_add (menu, ' - Auto - ', self.menu_select, None)
            self.type = None
        else:
            self.type = liste [0]
            
        for avail in liste:
            Utils.popup_add (menu, avail, self.menu_select, avail)

        self.menu.set_history (0)
        return

    def menu_select (self, widget, selection):
        self.type = selection
        return
        
    def quit(self, *args):
        self.hide()
        self.destroy()
        mainquit()
        return
    
    def ok_cb(self, b):
        self.ret = self.get_filename()
        
        if self.ret [-1] == '/':
            if self.url:
                ret = self.url.get_text ()
                
                if ret == '':
                    self.ret = None
                    return
                
                # construct a nice URL
                if string.lower (ret [0:5]) != 'http:' and \
                   string.lower (ret [0:4]) != 'ftp:':
                    
                    if ret [0:2] != '//':
                        ret = '//' + ret
                        
                    ret = 'http:' + ret

                self.ret = ret
            else:
                self.ret = None
        
        self.quit()
        return
    
    def run (self):
        self.show_all ()
        mainloop ()
        
        return self.ret


class FormatFileSelection (GtkFileSelection):
    
    def __init__(self, title = _("Format")):
        
        GtkFileSelection.__init__(self)
        self.set_title (title)
        
        self.connect('destroy', self.quit)
        self.connect('delete_event', self.quit)
        self.cancel_button.connect('clicked', self.quit)
        self.ok_button.connect('clicked', self.ok_cb)

        grab_add (self)

        self.ret = None
        
        vbox = self.main_vbox
        
        # type selector
        hbox = GtkHBox ()
        hbox.set_spacing (5)
        hbox.pack_start (GtkLabel (_("Formatting Style:")),
                         expand = FALSE, fill = FALSE)
        self.type_menu = GtkOptionMenu ()
        hbox.pack_start (self.type_menu)
        vbox.pack_start (hbox, expand = FALSE, fill = FALSE)

        # menu content
        menu = GtkMenu ()
        self.type_menu.set_menu (menu)
        
        liste = Autoload.available ('style')
        liste.sort ()
        
        for avail in liste:
            Utils.popup_add (menu, avail, self.menu_select, avail)

        self.type_menu.set_history (0)
        self.type = liste [0]
        
        # type selector
        hbox = GtkHBox ()
        hbox.set_spacing (5)
        hbox.pack_start (GtkLabel (_("Output type:")),
                         expand = FALSE, fill = FALSE)
        self.output_menu = GtkOptionMenu ()
        hbox.pack_start (self.output_menu)
        vbox.pack_start (hbox, expand = FALSE, fill = FALSE)

        # menu content
        menu = GtkMenu ()
        self.output_menu.set_menu (menu)
        
        liste = Autoload.available ('output')
        liste.sort ()
        
        for avail in liste:
            Utils.popup_add (menu, avail, self.output_menu_select, avail)

        self.output_menu.set_history (0)
        self.output = liste [0]
        return

    def menu_select (self, widget, selection):
        self.type = selection
        return

    def output_menu_select (self, widget, selection):
        self.output = selection
        return

    def quit(self, *args):
        self.hide()
        self.destroy()
        mainquit()
        return
    
    def ok_cb(self, b):
        self.ret = self.get_filename()
        
        self.quit()
        return
    
    def run (self):
        self.show_all ()
        mainloop ()
        
        return self.ret
    
class Pybliographic (GnomeApp):
    ''' Main Class defining a Pybliographic window '''
    
    def __init__ (self, version = '0.0'):
        GnomeApp.__init__ (self, 'Pybliographer', 'Pybliographer')

        # get window size
        ui_width  = config.get_int ('Pybliographer/UI/Width=-1')
        ui_height = config.get_int ('Pybliographer/UI/Height=-1')
        ui_paned  = config.get_int ('Pybliographer/UI/Paned=-1')

        if ui_width != -1 and ui_height != -1:
            self.set_default_size (ui_width, ui_height)

        self.connect ('destroy', self.quit)
        self.connect ('delete_event', self.file_exit)

        self.set_title('Pybliographic')
        self.version = version

        self.lyx = None
        
        self.main_box = GtkVBox()
        self.set_contents (self.main_box)
        self.main_box.show()
        
        file_menu = [
            UIINFO_ITEM_STOCK ('New', None, self.file_new, STOCK_MENU_NEW),
            UIINFO_ITEM_STOCK ('Open', None, self.file_open, STOCK_MENU_OPEN),
            UIINFO_ITEM_STOCK ('Save', None, self.file_save, STOCK_MENU_SAVE),
            UIINFO_ITEM_STOCK ('Save As...', None, self.file_save_as,
                               STOCK_MENU_SAVE_AS),
            UIINFO_SEPARATOR,
            UIINFO_SEPARATOR,
            UIINFO_ITEM_STOCK ('Quit', None, self.file_exit, STOCK_MENU_QUIT),
            ]
        
        help_menu = [
            UIINFO_ITEM_STOCK('About...', None, self.help_about,
                              STOCK_MENU_ABOUT),
            UIINFO_HELP ('pybliographic'),
            UIINFO_ITEM_STOCK (_("Submit a Bug Report"), None, self.exec_bug_buddy,
                               STOCK_MENU_TRASH_FULL)
            ]

        edit_menu = [
            UIINFO_ITEM_STOCK('Copy', None, self.edit_copy, STOCK_MENU_COPY),
            UIINFO_ITEM_STOCK('Cut', None, self.edit_cut, STOCK_MENU_CUT),
            UIINFO_ITEM_STOCK('Paste', None, self.edit_paste,
                              STOCK_MENU_PASTE),
            UIINFO_SEPARATOR,
            UIINFO_ITEM_STOCK('New...', None, self.edit_new, STOCK_MENU_NEW),
            UIINFO_ITEM('Edit...', None, self.edit_entry, None),
            UIINFO_ITEM_STOCK('Delete', None, self.edit_delete,
                              STOCK_MENU_TRASH),
            UIINFO_SEPARATOR,
            UIINFO_ITEM_STOCK('Search...', None, self.edit_search,
                              STOCK_MENU_SEARCH),
            UIINFO_SEPARATOR,
            UIINFO_ITEM ('Sort by Key', None,  self.sort_by_key),
            UIINFO_ITEM ('Sort by Type', None, self.sort_by_type),
            ]

        format_menu = [
            UIINFO_ITEM_STOCK('Cite in LyX', None, self.edit_insert_lyx,
                              STOCK_MENU_CONVERT),
            UIINFO_SEPARATOR,
            UIINFO_ITEM_STOCK('Format', None, self.format_entries,
                              STOCK_MENU_SAVE),
            UIINFO_ITEM_STOCK('Format As...', None, self.format_entries_as,
                              STOCK_MENU_SAVE_AS),
            ]
        
        config_menu = [
            UIINFO_ITEM_STOCK('Preferences...', None, self.configure_prefs,
                              STOCK_MENU_PREF),
            ]
        
        menus = [
            UIINFO_SUBTREE('File', file_menu),
            UIINFO_SUBTREE('Edit', edit_menu),
            UIINFO_SUBTREE('Configure', config_menu),
            UIINFO_SUBTREE('Formatting', format_menu),
            UIINFO_SUBTREE('Help', help_menu)
            ]
        
        toolbar = [
            UIINFO_ITEM_STOCK('Open', None, self.file_open,
                              STOCK_PIXMAP_OPEN),
            UIINFO_ITEM_STOCK('Save', None, self.file_save,
                              STOCK_PIXMAP_SAVE),
            UIINFO_SEPARATOR,
            UIINFO_ITEM_STOCK('Search', None, self.edit_search,
                              STOCK_PIXMAP_SEARCH),
            UIINFO_ITEM_STOCK('Cite', None, self.edit_insert_lyx,
                              STOCK_PIXMAP_CONVERT),
            UIINFO_SEPARATOR,
            UIINFO_ITEM_STOCK('Exit', None, self.file_exit,
                              STOCK_PIXMAP_QUIT),
            ]
        
        self.create_menus (menus)
        self.create_toolbar (toolbar)

        
        # Put information in Paned windows
        self.paned = GtkVPaned ()

        # The List of data
        self.database = Database ()
        holder = GtkScrolledWindow ()
        holder.set_policy (POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        holder.add (self.database)
        holder.show ()

        self.database.connect ('button_press_event', self.popup_menu)
        self.database.connect ('key_press_event', self.key_handler)
        self.database.connect ('select_row', self.update_display)
        
        self.paned.add1 (holder)
        self.database.show ()

        # La zone de texte du bas
        self.display = GtkText ()
        self.display.set_word_wrap (1)
        self.display.show ()
        
        holder = GtkScrolledWindow ()
        holder.set_policy (POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        holder.add (self.display)
        holder.show ()
        
        self.paned.add2 (holder)

        self.main_box.pack_start (self.paned, expand=TRUE)

        if ui_paned != -1:
            self.paned.set_position (ui_paned)
        
        self.paned.show ()

        self.status = GnomeAppBar (FALSE)
        self.set_statusbar (self.status)
        self.status.set_default (_("Welcome to Pybliographic"))

        # Le popup menu
        self.menu = GtkMenu ()
        self.menu_item = {}
        self.menu_item ['add']    = \
                       popup_add (self.menu, _("New..."),  self.edit_new)
        self.menu_item ['edit']   = \
                       popup_add (self.menu, _("Edit..."), self.edit_entry)
        self.menu_item ['remove'] = \
                       popup_add (self.menu, _("Delete"),  self.edit_delete)
        self.menu.show ()

        Utils.init_colors (self.get_colormap ())

        self.directory = config.get_string ('Pybliographer/Base/Directory=.')
        self.modified  = 0

        self.search = None
        self.opened_files = []
        self.format = None
        
        files = list (config.get_vector ('Pybliographer/Base/History='))
        for f in files:
            if f == '': continue
            
            self.add_opened_file (f)
            
        return

    # --------------------------------------------------
    def add_opened_file (self, file):
        
        if self.opened_files.count (file):
            # remove the existing file from the list,
            # so that it will be placed first next time
            self.opened_files.remove (file)
        else:
            # add a new file to the menu list
            def opener (widget, self = self, file = file):
                self.open (file)
                return
            
            if len (file) > 20:
                s = os.path.split (file)
                shortfile = '...' + s [0] [-10:] + '/' + s [1]
            else:
                shortfile = file
            
            self.insert_menus ("File/<Separator>", [
                UIINFO_ITEM (shortfile, None, opener)])

        # add the file on top of the list
        self.opened_files.append (file)
        return
    
    # --------------------------------------------------
        
    def sort_by_key (self, *arg):
        self.database.sort_by (Base.SortByKey)
        return
    
    def sort_by_type (self, *arg):
        self.database.sort_by (Base.SortByType)
        return
    
    # --------------------------------------------------
        
    def quit (self, *arg):
        mainquit ()

    # --------------------------------------------------
    def update_status (self):
        
        if self.modified:
            self.status.set_default (_("Modified database `%s' [%s, %d]") %
                                     (self.filename, self.type,
                                      len (self.database.data)))
        else:
            self.status.set_default (_("Database `%s' [%s, %d]") %
                                     (self.filename,
                                      self.type,
                                      len (self.database.data)))
        return
    
    # --------------------------------------------------

    def file_new (self, *arg):
        win = URLFileSelection (_("New file"), FALSE, TRUE, FALSE)
        win.set_filename (self.directory)

        file = win.run ()
        if file:
            self.directory = os.path.split (file) [0] + '/'
            self.new (file, win.type)
        return


    def new (self, file, type):
        def callback (arg, self = self):
            if arg == 0: self.modified = 0
            return

        was_modified = self.modified
        
        if self.modified:
            d = GnomeQuestionDialog (_("Database is modified.\n") +
                                     _("Discard changes ?"), callback)
            d.run_and_close ()
            
        if self.modified: return

        try:
            self.database.set (Open.bibnew (file, type))
            self.database.grab_focus ()

            if self.search:
                self.search.create_root_item (self.database)
                
        except IOError, err:
            Utils.error_dialog ('Creation error', err)
            
            # recover modification status
            self.modified = was_modified
            return

        self.filename = file
        self.type     = type
        self.format   = None
        
        self.modified = 0
        self.update_status ()
        
        self.add_opened_file (file)
        return
    
    # --------------------------------------------------

    def open (self, file, how = None):
        ''' open a database '''
        
        def callback (arg, self = self):
            if arg == 0: self.modified = 0
            return

        if self.modified:
            d = GnomeQuestionDialog (_("Database is modified.\n") +
                                     _("Discard changes ?"), callback)
            d.run_and_close ()
            
        if self.modified: return

        Utils.set_cursor (self, 'clock')

        try:
            self.database.set (Open.bibopen (file, how))
            Utils.set_cursor (self, 'normal')
            self.database.grab_focus ()
            
            if self.search:
                self.search.create_root_item (self.database)
                
        except IOError, err:
            Utils.set_cursor (self, 'normal')

            Utils.error_dialog ('Open Error', err)
            return

        self.filename = file
        self.type     = self.database.data.id

        self.modified = 0
        self.format   = None
        
        self.update_status ()

        self.add_opened_file (file)
        return


    def file_open (self, *arg):
        ''' callback for the Open button '''
        
        win = URLFileSelection (_("Open"), TRUE, TRUE)
        win.set_filename (self.directory)

        file = win.run ()
        
        if file:
            self.directory = os.path.split (file) [0] + '/'
            self.open (file, win.type)

        
    # --------------------------------------------------

    def file_exit (self, *arg):
        def callback (arg, self = self):
            if arg == 0: self.modified = 0
            return

        if self.modified:
            d = GnomeQuestionDialog (_("Database is modified.\n") +
                                     _("Quit without saving ?"), callback)
            d.run_and_close ()

        if self.modified: return

        # Save the graphical aspect of the interface
        # 1.- Window size
        alloc = self.get_allocation ()
        config.set_int ('Pybliographer/UI/Width',  alloc [2])
        config.set_int ('Pybliographer/UI/Height', alloc [3])
        # 2.- Proportion betzeen list and text
        height = self.paned.children () [0].get_allocation () [3]
        config.set_int ('Pybliographer/UI/Paned', height)

        # save the 10 last files
        config.set_vector ('Pybliographer/Base/History',
                           self.opened_files [-10:])

        # save the working directory
        config.set_string ('Pybliographer/Base/Directory', self.directory)

        config.sync ()

        self.quit ()
        return
    

    # --------------------------------------------------

    def file_save (self, *arg):
        if not self.modified: return
        
        try:
            self.database.data.update ()
            self.modified = 0
            
            # redisplay the data to ensure coherence
            self.database.display (self.database.data)
            
        except IOError, err:
            d = GnomeErrorDialog (_("can't save file: %s") % str (err))
            d.run_and_close ()

        self.update_status ()
        return
    
    # --------------------------------------------------

    def file_save_as (self, *arg):
        win = URLFileSelection (_("Save As"), FALSE, TRUE, FALSE)
        win.set_filename (self.directory)

        file = win.run ()
        if not file: return
        
        if os.path.exists (file):
            var = []
                
            def callback (arg, var = var):
                if arg == 0: var.append (1)
                return

            d = GnomeQuestionDialog (_("File `%s' exists.\nOverwrite it ?") %
                                     file,
                                     callback)
            d.run_and_close ()

            if not var: return
                
        # write the file
        try:
            fh = open (file, 'w')    
            Open.bibwrite (self.database.data, how = win.type, out = fh)
            fh.close ()
        except IOError, msg:
            d = GnomeErrorDialog (_("Can't save file:\n%s") % msg)
            d.run_and_close ()
            return

        self.open (file, win.type)
        return
    
    # --------------------------------------------------
    # --------------------------------------------------

    def edit_copy (self, * arg):
        d = GnomeOkDialog (_("Not yet implemented..."))
        d.show ()
        return

    # --------------------------------------------------

    def edit_cut (self, * arg):
        d = GnomeOkDialog (_("Not yet implemented..."))
        d.show ()
        return

    # --------------------------------------------------

    def edit_paste (self, * arg):
        d = GnomeOkDialog (_("Not yet implemented..."))
        d.show ()
        return
    
    # --------------------------------------------------

    def edit_search (self, * arg):
        if self.search is None:
            self.search = SearchDialog (self.database)
        
        self.search.show_all ()
        return
    
    # --------------------------------------------------

    def edit_new (self, *arg):
        if self.database.data is None:
            d = GnomeOkDialog (_("Please, create a new database first.\nUse File/New for example"))
            d.show ()
            return
        
        selection = self.database.selection

        if not self.database.data.has_property ('add'):
            d = GnomeErrorDialog (_("edition is disabled in this database"), self)
            d.run_and_close ()
            return
        
        if not selection: 
            row = 0
        else:
            row = self.database.selected_rows () [0]

        entry = self.database.data.new_entry ()
        
        def callback (entry, self, selection = row):
            self.modified = 1
            
            self.database.data [entry.key] = entry
            self.database.insert (selection, entry)

            self.update_status ()
            return
        
        dialog = EntryDialog (entry, self.database.data, callback, self)
        dialog.show ()
        pass

    # --------------------------------------------------

    def edit_entry (self, *arg):
        selection = self.database.selection
        if not selection: return

        # if we have no right to edit
        if not self.database.data.has_property ('edit'): 
            d = GnomeErrorDialog (_("edition is disabled in this database"))
            d.run_and_close ()
            return

        row = self.database.selected_rows () [0]
        e = selection [0]
        oldkey = e.key
        
        def callback (entry, self, selection = row, oldkey = oldkey):
            self.modified = 1

            self.database.set_row (selection, entry)
            self.database.select_row (selection, 0)

            self.update_status ()
            return
        
        dialog = EntryDialog (e, self.database.data, callback, self)
        dialog.show ()

    # --------------------------------------------------

    def edit_insert_lyx (self, * arg):
        selection = self.database.selection
        if not selection: return

        if self.lyx is None:
            from Pyblio import LyX

            try:
                self.lyx = LyX.LyXclient ()
            except IOError, msg:
                d = GnomeErrorDialog (_("Can't connect to LyX:\n%s") % msg [1])
                return

        try:
            self.lyx ('citation-insert', selection [0].key.key)
        except IOError, msg:
            d = GnomeErrorDialog (_("Can't connect to LyX:\n%s") % msg [1])

        return
    
    # --------------------------------------------------

    def edit_delete (self, *arg):
        selection = self.database.selection
        if not selection: return

        if not self.database.data.has_property ('remove'): 
            d = GnomeErrorDialog (_("edition is disabled in this database"), self)
            d.run_and_close ()
            return

        entry = selection [0]
        self.__ans = 0
        def callback (arg, self = self):
            if arg == 0: self.__ans = 1
            return

        d = GnomeQuestionDialog (_("Really remove entry %s ?") %
                                 (entry.key.key), callback)
        d.run_and_close ()

        if self.__ans:
            self.database.remove (entry.key)
            self.modified = 1

            self.update_status ()
            self.update_display ()
        return
    
        
    # --------------------------------------------------

    def configure_prefs (self, * arg):
        d = GnomeOkDialog (_("Not yet implemented..."))
        d.show ()
        return

    # --------------------------------------------------

    def popup_menu (self, *arg):
        clist, event, = arg
        if self.database.data is None: return
        
        if (event.type == GDK._2BUTTON_PRESS and event.button == 1):
            # Always select the item below the cursor
            couple = self.database.get_selection_info (event.x, event.y)
            if couple:
                self.database.select_row (couple [0], couple [1])
                if not self.database.data.has_property ('edit'): return

                # else, do as if the Edit menu as been activated
                self.menu_item ['edit'].emit ('activate', None)
                return
        
        if (event.type == GDK.BUTTON_PRESS and event.button == 3):
            for f in ('add', 'edit', 'remove'):
                self.menu_item [f].set_sensitive \
                               (self.database.data.has_property (f))
            
            # Always select the item below the cursor
            couple = self.database.get_selection_info (event.x, event.y)
            if couple:
                self.database.select_row (couple [0], couple [1])
                
            self.menu.popup (None, None, None, event.button, event.time)

    # --------------------------------------------------

    def update_display (self, *arg):
    
        e = self.database.selection
        
        # Display this entry
        self.display.freeze ()
        self.display.delete_text (0, -1)
        
        if e:
            e = e [0]
            
            entry = e.type
                
            self.display.insert (None, Utils.color['blue'], None, entry.name)
            self.display.insert_defaults (' ['+ str (e.key.key) + ']\n\n')
            
            dico = e.keys ()

            # Search the longest field
            mlen = 0
            for f in dico:
                mlen = max (mlen, len (f))

            for f in entry.fields:
                
		field = string.lower (f.name)
                
		if e.has_key (field):
                    sp = ' ' * (mlen - len (f.name))
                    self.display.insert (None, Utils.color ['red'], None,
                                         f.name + ': ' + sp)
                    self.display.insert_defaults (str (e [field]) + '\n')
                    dico.remove (field)


            self.display.insert_defaults ('\n')
            
            for f in dico:
                sp = ' ' * (mlen - len (f))
                self.display.insert (None, Utils.color['red'], None,
                                     f + ': ' + sp)
                self.display.insert_defaults (str (e [f]) + '\n')

        self.display.thaw ()

        return
            
    # --------------------------------------------------

    def exec_bug_buddy (self, *args):
        command = 'bug-buddy --package=Pybliographic ' + \
                  ('--package-ver=%s' % self.version)
        
        if os.system (command) != 0:
            GnomeErrorDialog (_("Please install bug-buddy\nto use this feature"))
        
        return
    
    def help_about (self, *arg):
        about = GnomeAbout ('Pybliographic', self.version,
                            _("This program is copyrighted under the GNU GPL"),
                            ['Frédéric Gobry'],
                            _("Gnome interface to the Pybliographer system."),
                            'pybliographic-logo.png')
        
        vbox = GtkVBox (TRUE, 0)
        button = GtkButton(_("Submit a bug report\n using bug-buddy"))
        
        link = GnomeHRef ('http://www.idiap.ch/~gobry/pybliographer.php3',
                          _("Pybliographer Home Page"))
        link.show ()
        about.vbox.pack_start (link)
        about.show()
        return
    
    def key_handler (self, * arg):
        event = arg [1]
        if event.keyval == GDK.Return:
             self.database.select_row (self.database.focus_row, 0)
        return
    
    # --------------------------------------------------

    def format_entries (self, * arg):
        if self.database.data is None: 
            d = GnomeErrorDialog (_("Please open a database first"))
            d.run_and_close ()
            return
        
        if not self.format:
            self.format_entries_as ()
            return

        try:
            fh = open (self.format [0], 'w')
        except IOError, err:
            d = GnomeErrorDialog (_("Can't save file:\n%s") % msg)
            d.run_and_close ()
            return

        style  = Autoload.get_by_name ('style',  self.format [1])
        output = Autoload.get_by_name ('output', self.format [2])

        formatter = output.data (fh)
        
        Utils.set_cursor (self, 'clock')
        ordered = Base.Reference ()
        ordered.add (self.database.data, self.database.access)
        
        style.data (_("Bibliography"), formatter, ordered)
        Utils.set_cursor (self, 'normal')

        fh.close ()
        return
    
    def format_entries_as (self, * arg):
        win = FormatFileSelection ()
        win.set_filename (self.directory)

        file = win.run ()
        if not file: return
        
        if os.path.exists (file):
            var = []
                
            def callback (arg, var = var):
                if arg == 0: var.append (1)
                return

            d = GnomeQuestionDialog (_("File `%s' exists.\nOverwrite it ?") % file,
                                     callback)
            d.run_and_close ()

            if not var: return
            
        self.format = (file, win.type, win.output)
        self.format_entries ()
        return
