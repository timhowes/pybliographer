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

import gettext

_ = gettext.gettext

from Pyblio.GnomeUI import Document
from Pyblio import Base

from gtk import *

class Pybliographic:
    ''' Main class holding all the documents and performing
    general tasks '''

    def __init__ (self, version):
        self.version   = version
        self.documents = []

        return

    def new_document (self, * arg):
        db  = Base.DataBase (None)
        doc = Document.Document (db, self.version)

        # register several callbacks
        doc.Subscribe ('new-document',     self.new_document)
        doc.Subscribe ('close-document',   self.close_document)
        doc.Subscribe ('open-document',    self.open_document)
        doc.Subscribe ('exit-application', self.exit_application)

        self.documents.append (doc)
        return

    def open_document (self, document):
        pass

    
    def close_document (self, document):
        if not document.close_document_request ():
            return
        
        self.documents.remove (document)

        if not self.documents:
            self.exit_application (document)
        return

    def exit_application (self, document):
        document.update_configuration ()
        
        for doc in self.documents:
            if not doc.close_document_request ():
                return
            
            self.documents.remove (doc)

        mainquit ()
        return
    
