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

''' Main Module holding all the documents '''

import gettext, copy

_ = gettext.gettext

from Pyblio.GnomeUI import Document
from Pyblio import Base, Config

from gtk import *
from gnome import config, history

class Pybliographic:
    ''' Main class holding all the documents and performing
    general tasks '''

    def __init__ (self):
        self.documents = []
        self.opened    = []
        
        histsize = Config.get ('gnome/history').data

        for i in range (1, histsize + 1):
            file = config.get_string  ('Pybliographic/History/File%d=' % i)
            fmat = config.get_string  ('Pybliographic/History/Type%d=' % i)

            if not file: continue
            
            if not fmat: fmat = None
            self.opened.append ((file, fmat))

        if not self.opened:
            # get the old format of history
            self.opened = map (lambda x: (x, None),
                               filter (lambda x: x,
                                       list (config.get_vector ('Pybliographic/Base/History='))))
        return


    def new_document (self, * arg):
        db  = Base.DataBase (None)
        doc = Document.Document (db)

        # register several callbacks
        doc.Subscribe ('new-document',     self.new_document)
        doc.Subscribe ('open-document',    self.cb_open_document)
        doc.Subscribe ('close-document',   self.close_document)
        doc.Subscribe ('exit-application', self.exit_application)

        doc.update_history (self.opened)
        
        self.documents.append (doc)
        return doc

    def cb_open_document (self, doc):
        ''' a document has been opened '''

        file = str (doc.data.key)
        fmat = doc.data.id
        
        history.recently_used (file, 'application/x-bibtex',
                               'pybliographic', 'Bibliography')
                              
        try:
            self.opened.remove ((file, fmat))
        except ValueError:
            pass
        
        self.opened.insert (0, (file, fmat))

        # warn all the documents
        for doc in self.documents:
            doc.update_history (self.opened)
        return

    
    def open_document (self, url, how = None):
        doc = self.new_document ()
        doc.open_document (url, how)
        
        return doc

    
    def close_document (self, document):
        ''' close one specified document '''
        
        if len (self.documents) == 1:
            self.exit_application (document)
            return
        
        if not document.close_document_request ():
            return
        
        document.w.destroy ()
        self.documents.remove (document)
        return


    def exit_application (self, document):
        document.update_configuration ()

        i = 1
        for file in self.opened [0:Config.get ('gnome/history').data]:
            name = file [0]
            fmat = file [1] or ''
            
            config.set_string ('Pybliographic/History/File%d' % i, name)
            config.set_string ('Pybliographic/History/Type%d' % i, fmat)
            i = i + 1
        
        config.sync ()

        doclist = copy.copy (self.documents)
        
        for doc in doclist:
            if not doc.close_document_request ():
                return
            
            doc.w.destroy ()
            self.documents.remove (doc)

        mainquit ()
        return
    
