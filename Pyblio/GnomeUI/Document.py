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

from gnome import ui
import gtk
import gtk.glade

from Pyblio.GnomeUI import Index, Entry, Utils, FileSelector, Editor
from Pyblio.GnomeUI import Search, Format
from Pyblio.GnomeUI.Sort import SortDialog
from Pyblio.GnomeUI.Config import ConfigDialog
from Pyblio.GnomeUI.Fields import FieldsDialog, EntriesDialog

from Pyblio import Connector, Open, Exceptions, Selection, Sort, Base, Config
from Pyblio import version, Fields, Types, Query

import Pyblio.Style.Utils

import gettext, os, string, copy, types, sys, traceback, stat

_ = gettext.gettext

import cPickle

pickle = cPickle
del cPickle

printable = string.lowercase + string.uppercase + string.digits

class Document (Connector.Publisher):
    
    def __init__ (self, database):

        self.xml = gtk.glade.XML ('glade/pyblio.glade', 'main')
        self.xml.signal_autoconnect (self)

        self.w = self.xml.get_widget ('main')
        self.paned = self.xml.get_widget ('main_pane')

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

        self.paned.show_all ()

#        # The text area
        self.display = Entry.Entry ()
        self.paned.add2 (self.display.w)

        # Status bar
        self.statusbar = self.xml.get_widget ('statusbar')
        
        # set window size
        ui_width  = Utils.config.get_int ('/apps/pybliographic/ui/width') or -1
        ui_height = Utils.config.get_int ('/apps/pybliographic/ui/height') or -1

        if ui_width != -1 and ui_height != -1:
            self.w.set_default_size (ui_width, ui_height)

        # set paned size
        paned_height = Utils.config.get_int ('/apps/pybliographic/ui/paned') or -1
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

        self.incremental_start  = None
        self.incremental_search = ''
        
        self.modification_date = None

        # set the default sort method
        default = Utils.config.get_string ('/apps/pybliographic/sort/default')
        if default is not None: default = pickle.loads (default)

        self.sort_view (default)
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

#        self.w.remove_menus (_("File") + '/' + _("Previous Documents") + '/',
#                             100)
#
#        menuinfo = []
#        for item in history:
#            def callback (widget, self = self, file = item [0], how = item [1]):
#                if not self.confirm (): return
#                self.open_document (file, how)
#                return
#
#            filename = item [0]
#            
#            menuinfo.append (UIINFO_ITEM_STOCK (filename, None, callback, STOCK_MENU_OPEN))
#
#        self.w.insert_menus (_("File") + '/' + _("Previous Documents") + '/',
#                             menuinfo)
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
            iter    = self.selection.iterator (self.data.iterator ())
            entries = []
            
            e = iter.first ()
            while e:
                entries.append (e.key)
                e = iter.next ()

        url = Fields.URL (style)

        try:
            Pyblio.Style.Utils.generate (url, format, self.data, entries, file)
        except RuntimeError, err:
            print err
            self.w.error (_("Error while parsing `%s':\n%s") % (style, err))
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


    def query_database (self, * arg):
        ''' callback corresponding to the "Query..." button '''

        if not self.confirm (): return

        def dlg_cb_2 (dummy): return
        
        #################################################
        # Changes to Document.py by John Vu starts here #
        #################################################
        
        # Load up the past search queries by reading the file
        # .pybsearchhis in the user's home directory; otherwise, the
        # list will be empty via the searchhistory = [''] command
        try:
            pybsearchhis = open(os.path.expanduser('~')+'/.pybsearchhis', 'r')
            searchhistory = pybsearchhis.readlines()
            pybsearchhis.close()
        except IOError:
            searchhistory = ['']
        
        # get rid of newline character so that search history is
        # displayed correctly in the combobox
        for x in range(0,len(searchhistory)):
            searchhistory[x] = string.replace(searchhistory[x],'\n','') 

        dlg = ui.OkCancelDialog (_("Enter your Medline query"), dlg_cb_2, self.w)
        key_w_combo = GtkCombo()
        # make it a combo box so that past search entries can be
        # viewed
        key_w_combo.set_popdown_strings(searchhistory)
        key_w = key_w_combo.entry
        # the query string will be loaded onto key_w assigned here
        key_w.set_text ('')
        # the entry should be empty; if this option is not set, the
        # first list item will show instead
        key_w.set_editable (True)
        adj1   = GtkAdjustment (100, 0, 10000, 1.0, 100.0, 0.0)
        adj2   = GtkAdjustment (1, 0, 10000, 1.0, 100.0, 0.0)
        max_w = GtkSpinButton (adj=adj1, digits=0)
        # max_w is the max number of returns the user wants
        disp_s = GtkSpinButton (adj=adj2, digits=0)
        # disp_s is the starting number of the entry to begin
        # displaying; e.g. if for a certain query there is a total of
        # 550 results, if the max_w is set to 100 and the disp_s is
        # set to 400, there will be 100 results shown starting from
        # result number 400 and ending at 499

        hbox1 = GtkHBox()
        hbox1.pack_start (GtkLabel (_("Search PubMed for: ")))
        hbox1.pack_start (key_w_combo)
        hbox1.pack_start (GtkLabel (_("Maximum number\nof results: ")))
        hbox1.pack_start (max_w)
        hbox1.pack_start (GtkLabel (_("Start listing at\nresult number: ")))
        hbox1.pack_start (disp_s)
        dlg.vbox.pack_start (hbox1)
        
        hseparator1 = GtkHSeparator()
        dlg.vbox.pack_start (hseparator1)

        # Print partial instructions on use of the limits
        hbox2 = GtkHBox()
        instructions = GtkLabel ("o   Leave options below unchanged if you do not want your search limited.\no   Use the \"All Fields\" pull-down menu to specify a field.\no   Boolean operators AND, OR, NOT must be in upper case.\no   If search fields tags are used, enclose in square brackets with no space\n     between the search term and the tag, e.g., rubella[ti].\no   Search limits may exclude \"in process\" and \"publisher supplied\" citations.\no   For more help goto: http://www.ncbi.nlm.nih.gov:80/entrez/query/static/help/pmhelp.html")
        instructions.set_justify (0) # LEFT justify the instructions
        hbox2.pack_start (instructions)
        dlg.vbox.pack_start (hbox2)

        hseparator2 = GtkHSeparator()
        dlg.vbox.pack_start (hseparator2)
        dlg.vbox.pack_start (GtkLabel (_("Limited to:")))

        # Below are all the limits allowable. All entries are not
        # editable, except for the date entries.
        hbox3 = GtkHBox()
        field_combo = GtkCombo()
        field_combo.set_popdown_strings (['All Fields', 'Affiliation', 'Author Name', 'EC/RN Number', 'Entrez Date', 'Filter', 'Issue', 'Journal Name', 'Language', 'MeSH Date', 'MeSH Major Topic', 'MeSH Subheading', 'MeSH Terms', 'Pagination', 'Publication Date', 'Publication Type', 'Secondary Source ID', 'Substance Name', 'Text Word', 'Title', 'Title/Abstract', 'UID', 'Volume'])
        field_combo_entry = field_combo.entry
        field_combo_entry.set_text ('All Fields')
        GtkEditable.set_editable(field_combo_entry,0)
        # command to prevent the user from editing the limit
        hbox3.pack_start (field_combo)
        checkbutton1 = GtkCheckButton (label='Only items\nwith abstracts')
        hbox3.pack_start (checkbutton1)
        checkbutton2 = GtkCheckButton (label='Only items\nahead of print')
        hbox3.pack_start (checkbutton2)
        dlg.vbox.pack_start (hbox3)

        hbox4 = GtkHBox()
        pub_type_combo = GtkCombo()
        
        pub_type_combo.set_popdown_strings (['Publication Types', 'Addresses', 'Bibliography', 'Biography', 'Classical Article', 'Clinical Conference', 'Clinical Trial', 'Clinical Trial, Phase I', 'Clinical Trial, Phase II', 'Clinical Trial, Phase III', 'Clinical Trial, Phase IV', 'Comment', 'Congresses', 'Consensus Development Conference', 'Consensus Development Conference, NIH', 'Controlled Clinical Trial', 'Corrected and Republished Article', 'Dictionary', 'Directory', 'Duplicate Publication', 'Editorial', 'Evaluation Studies', 'Festschrift', 'Government Publications', 'Guideline', 'Historical Article', 'Interview', 'Journal Article', 'Lectures', 'Legal Cases', 'Legislation', 'Letter', 'Meta-Analysis', 'Multicenter Study', 'News', 'Newspaper Article', 'Overall', 'Periodical Index', 'Practice Guideline', 'Published Erratum', 'Randomized Controlled Trial', 'Retraction of Publication', 'Retracted Publication', 'Review', 'Review, Academic', 'Review Literature', 'Review, Multicase', 'Review of Reported Cases', 'Review, Tutorial', 'Scientific Integrity Review', 'Technical Report', 'Twin Study', 'Validation Studies'])
        
        pub_type_combo_entry = pub_type_combo.entry
        pub_type_combo_entry.set_text ('Publication Types')
        GtkEditable.set_editable (pub_type_combo_entry,0) # again, entry not editable, only selectable
        hbox4.pack_start (pub_type_combo)
        lang_combo = GtkCombo ()
        lang_combo.set_popdown_strings (['Languages', 'English', 'French', 'German', 'Italian', 'Japanese', 'Russian', 'Spanish'])
        lang_combo_entry = lang_combo.entry
        lang_combo_entry.set_text ('Languages')
        GtkEditable.set_editable (lang_combo_entry,0)
        hbox4.pack_start (lang_combo)
        subset_combo = GtkCombo()
        subset_combo.set_popdown_strings (['Subsets', 'AIDS', 'AIDS/HIV journals', 'Bioethics', 'Bioethics journals',  'Biotechnology journals', 'Communication disorders journals', 'Complementary and Alternative Medicine', 'Consumer health journals', 'Core clinical journals', 'Dental journals', 'Health administration journals', 'Health tech assessment journals', 'History of Medicine', 'History of Medicine journals', 'In process', 'Index Medicus journals', 'MEDLINE', 'NASA journals', 'Nursing journals', 'PubMed Central', 'Reproduction journals', 'Space Life Sciences', 'Supplied by Publisher', 'Toxicology'])
        subset_combo_entry = subset_combo.entry
        subset_combo_entry.set_text ('Subsets')
        GtkEditable.set_editable (subset_combo_entry,0)
        hbox4.pack_start (subset_combo)
        dlg.vbox.pack_start (hbox4)

        hbox5 = GtkHBox()
        age_range_combo = GtkCombo ()
        age_range_combo.set_popdown_strings (['Ages', 'All Infant: birth-23 month', 'All Child: 0-18 years', 'All Adult: 19+ years', 'Newborn: birth-1 month', 'Infant: 1-23 months', 'Preschool Child: 2-5 years', 'Child: 6-12 years', 'Adolescent: 13-18 years', 'Adult: 19-44 years', 'Middle Aged: 45-64 years', 'Aged: 65+ years', '80 and over: 80+ years'])
        age_range_combo_entry = age_range_combo.entry
        age_range_combo_entry.set_text ('Ages')
        GtkEditable.set_editable (age_range_combo_entry,0)
        hbox5.pack_start (age_range_combo)
        human_animal_combo = GtkCombo ()
        human_animal_combo.set_popdown_strings (['Human or Animal', 'Human', 'Animal'])
        human_animal_combo_entry = human_animal_combo.entry
        human_animal_combo_entry.set_text ('Human or Animal')
        GtkEditable.set_editable (human_animal_combo_entry,0)
        hbox5.pack_start (human_animal_combo)
        gender_combo = GtkCombo ()
        gender_combo.set_popdown_strings (['Gender', 'Female', 'Male'])
        gender_combo_entry = gender_combo.entry
        gender_combo_entry.set_text ('Gender')
        GtkEditable.set_editable (gender_combo_entry,0)
        hbox5.pack_start (gender_combo)
        dlg.vbox.pack_start (hbox5)

        hbox6 = GtkHBox ()
        entrez_date_combo = GtkCombo ()
        entrez_date_combo.set_popdown_strings (['Entrez Date', '30 Days', '60 Days', '90 Days', '180 Days', '1 Year', '2 Years', '5 Years', '10 Years'])
        entrez_date_combo_entry = entrez_date_combo.entry
        entrez_date_combo_entry.set_text ('Entrez Date')
        GtkEditable.set_editable (entrez_date_combo_entry,0)
        hbox6.pack_start (entrez_date_combo)
        dlg.vbox.pack_start (hbox6)

        hbox7 = GtkHBox ()
        pub_date_combo = GtkCombo ()
        pub_date_combo.set_popdown_strings (['Publication Date', 'Entrez Date'])
        pub_date_combo_entry = pub_date_combo.entry
        pub_date_combo_entry.set_text ('Publication Date')
        GtkEditable.set_editable (pub_date_combo_entry,0)
        hbox7.pack_start (pub_date_combo)
        hbox7.pack_start (GtkLabel (_("From:")))
        from_date_entry = GtkEntry ()
        hbox7.pack_start (from_date_entry)
        hbox7.pack_start (GtkLabel (_("To:")))        
        to_date_entry = GtkEntry ()
        hbox7.pack_start (to_date_entry)
        dlg.vbox.pack_start (hbox7)

        hbox8 = GtkHBox ()
        hbox8.pack_start (GtkLabel (_("Use the format YYYY/MM/DD; month and day are optional.")))
        dlg.vbox.pack_start (hbox8)
        
        dlg.show_all ()
        dlg.run_and_close ()
        
        keyword  = string.strip (key_w.get_text ())
        maxcount = max_w.get_value_as_int ()
        displaystart = disp_s.get_value_as_int ()
        field = field_combo_entry.get_text ()
        abstract = checkbutton1.get_active ()
        epubahead = checkbutton2.get_active ()
        pubtype = pub_type_combo_entry.get_text ()
        language = lang_combo_entry.get_text ()
        subset = subset_combo_entry.get_text ()
        agerange = age_range_combo_entry.get_text ()
        humananimal = human_animal_combo_entry.get_text ()
        gender = gender_combo_entry.get_text ()
        entrezdate = entrez_date_combo_entry.get_text ()
        pubdate = pub_date_combo_entry.get_text ()
        fromdate = from_date_entry.get_text ()
        todate = to_date_entry.get_text ()

        # Add an ending newline character to each query listed in the
        # search history. This makes sure that when each item is
        # written to the file, a separator is also written so that
        # when read again later in another query (by readlines()), it
        # is properly separated into the searchhistory list
        
        for x in range(0,len(searchhistory)):
            searchhistory[x] = searchhistory[x] + '\n'

        if keyword == "": return
        else: # save keyword to medline search history if it's a valid keyword
            
            if len(searchhistory) < 10:
                # I only want a maximum of the 10 most recent keywords
                
                searchhistory.insert(0,keyword+'\n')
                # I don't want to append to the list, I want to add
                # the most recent search term at the top of the list
                
            else:
                searchhistory[9] = ''
                # essentially remove the 10th item before adding the
                # most recent search query, I just want the 10 past
                # search histories saved
                
                searchhistory.insert(0,keyword+'\n')
            try:
                pybsearchhis = open(os.path.expanduser('~')+'/.pybsearchhis','w')
                # save the search history to the .pybsearchhis file in
                # the user's home dir
                pybsearchhis.writelines(searchhistory)
                pybsearchhis.close()
            except IOError:
                print "Can't save search history."

        # Call the actual function to do the search and then return
        # the results into url: 16 parameters passed altogether

        url = Query.medline_query (keyword,maxcount,displaystart,field,
                                   abstract,epubahead,pubtype,language,
                                   subset,agerange,humananimal,gender,
                                   entrezdate,pubdate,fromdate,todate)

        ###############################################
        # Changes to Document.py by John Vu ends here #
        ###############################################
        
        self.open_document (url, 'medline', no_name = True)
        return


    def merge_database (self, * arg):
        ''' add all the entries of another database to the current one '''
        # get a new file name
        (url, how) = FileSelector.URLFileSelection (_("Merge file"),
                                                    url = True, has_auto = True).run ()

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

    
    def open_document (self, url, how = None, no_name = False):
        
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

        if no_name: data.key = None
        
        self.data    = data
        self.redisplay_index (0)
        
        # eventually warn interested objects
        self.issue ('open-document', self)
        return

    
    def save_document (self, * arg):
        if self.data.key is None:
            self.save_document_as ()
            return

        file = self.data.key.url [2]
        
        if self.modification_date:
            mod_date = os.stat (file) [stat.ST_MTIME]
            
            if mod_date > self.modification_date:
                if not Utils.Callback (_("The database has been externally modified.\nOverwrite changes ?"),
                                       self.w).answer ():
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

        # get the current modification date
        self.modification_date = os.stat (file) [stat.ST_MTIME]
        
        self.update_status (0)
        return
    
    
    def save_document_as (self, * arg):
        # get a new file name
        (url, how) = FileSelector.URLFileSelection (_("Save As..."),
                                                    url = False, has_auto = False).run ()

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
        return 1


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
        self.index.set_scroll (entries [-1])
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

        self.freeze_display (None)

        self.redisplay_index (1)
        self.index.select_item (new)
        return
    
    
    def delete_entry (self, * arg):
        ''' removes the selected list of items after confirmation '''
        entries = self.index.selection ()
        l = len (entries)
        if l == 0: return

        offset = self.index.get_item_position (entries [-1])

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
        self.index.select_item (offset)
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
        if sort is None:
            self.selection.sort = None
        else:
            self.selection.sort = Sort.Sort (sort)
        
        self.redisplay_index ()
        return
    

    def sort_by_field (self, field):
        if field == '-key-':
            mode = Sort.KeySort ()
        elif field == '-type-':
            mode = Sort.TypeSort ()
        else:
            mode = Sort.FieldSort (field)
            
        self.selection.sort = Sort.Sort ([mode])
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


    def key_pressed (self, app, event):
        # filter out special keys
        if (event.string < 'a' or event.string > 'z') and \
           (event.string < '0' or event.string > '9'): return 1

        if self.selection.sort is None:
            app.flash ("Select a column to search in first.")
            return 1
        
        if event.string in printable:
            # the user searches the first entry in its ordering that starts with this letter
            if self.incremental_search == '':
                self.incremental_search = event.string
                self.incremental_start  = event.time
            else:
                if event.time - self.incremental_start > 1000:
                    self.incremental_search = event.string
                else:
                    # two keys in a same shot: we search for the composition of the words
                    self.incremental_search = self.incremental_search + event.string
                
                self.incremental_start  = event.time

            # search first occurence
            if self.index.go_to_first (self.incremental_search,
                                       self.selection.sort.fields [0]):
                app.flash ("Searching for '%s...'" % self.incremental_search)
            else:
                app.flash ("Cannot find '%s...'" % self.incremental_search)
                
        return 1


    def update_configuration (self):
        ''' save current informations about the program '''
        
        # Save the graphical aspect of the interface
        # 1.- Window size
        alloc = self.w.get_allocation ()
        Utils.config.set_int ('/apps/pybliographic/ui/width',  alloc [2])
        Utils.config.set_int ('/apps/pybliographic/ui/height', alloc [3])

        # 2.- Proportion betzeen list and text
        height = self.paned.get_position ()
        Utils.config.set_int ('/apps/pybliographic/ui/paned', height)

        # updates the index's config
        self.index.update_configuration ()

        # ...and the search window
        if self.search_dg:
            self.search_dg.update_configuration ()
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
        about = ui.About ('Pybliographic', version.version,
                            _("This program is copyrighted under the GNU GPL"),
                            ['Frédéric Gobry'],
                            _("Gnome interface to the Pybliographer system."),
                            'pybliographic-logo.png')
        about.set_parent (self.w)
        
        link = ui.HRef ('http://www.gnome.org/pybliographer',
                        _("Pybliographer Home Page"))
        link.show ()
        about.vbox.pack_start (link)
        about.show()
        return

