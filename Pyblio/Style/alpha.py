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


""" This module implements the alpha and abbrv styles """

import string

from Pyblio import Autoload, Types
from Pyblio.Style import Utils

class Writer (Utils.SimpleWriter):

    def full_publisher (self, entry):
        self.ewrite (entry, 'publisher')
        self.ewrite (entry, 'address', pre = ', ')
        self.ewrite (entry, 'edition', pre = ', ', post = ' edition')
        self.dwrite (entry, pre = ', ')
        return

    def full_title (self, entry, book = 0, chapter = 1, pre = None):
        
        if book: self.ewrite (entry, 'booktitle', style = 'emph', pre = pre)
        else:    self.ewrite (entry, 'title',     style = 'emph', pre = pre)
            
        if entry.has_key ('series'):
            self.write (', ', count = 0)
            
            if entry.has_key ('volume'):   self.ewrite (entry, 'volume',
                                                        pre = 'volume ', post = ' of ')
            elif entry.has_key ('number'): self.ewrite (entry, 'number',
                                                        pre = 'number ', post = ' in ')
                
            self.ewrite (entry, 'series', style = 'emph')

        if chapter:
            self.ewrite (entry, 'chapter', pre = ', type ')
            
            if entry.has_key ('pages'):
                text = self.text (entry ['pages'])
                
                if string.find (text, '-') == -1: pre = ', page '
                else:                             pre = ', pages '
                
                self.ewrite (entry, 'pages',   pre = pre)
        return

        
    def write_one (self, entry, key):

        # write the start of the entry
        self.fmt.start (key = key, entry = entry)

        if entry.type != Types.getentry ('proceedings'):
            self.awrite (entry, 'author')
            self.new_group ()

        # ==================================================
        if entry.type == Types.getentry ('proceedings'):

            if entry.has_key ('editor'):
                group = entry ['editor']
                
                if len (group) > 1: ed = ', editors'
                else:               ed = ', editor'
                    
                self.awrite (entry, 'editor', post = ed, force = 1)
            self.new_group ()

            # --------------------------------------------------

            self.full_title (entry, chapter = 0)
            self.ewrite (entry, 'address', pre = ', ')
            self.dwrite (entry, pre = ', ')
            self.new_group ()
                    
            # --------------------------------------------------
            
            if entry.has_key ('organization') or entry.has_key ('publisher'):
                self.ewrite (entry, 'organization')
                self.ewrite (entry, 'publisher', pre = ', ')
                
            self.new_group ()
                    

        # ==================================================
        elif entry.type == Types.getentry ('article'):
            self.ewrite (entry, 'title')
            self.new_group ()
            
            if entry.has_key ('journal'):
                self.ewrite (entry, 'journal', style = 'emph')
                self.ewrite (entry, 'volume', pre = ', ')
                self.ewrite (entry, 'number', pre = '(', post = ')')
                self.ewrite (entry, 'pages',  pre = ':')

            self.dwrite (entry, pre = ', ')
            self.new_group ()


        # ==================================================
    	elif entry.type == Types.getentry ('book') or \
             entry.type == Types.getentry ('inbook'):

            self.full_title (entry)
            self.new_group ()

            self.full_publisher (entry)
            self.new_group ()
            

        # ==================================================
    	elif entry.type == Types.getentry ('booklet'):
            
            self.ewrite (entry, 'title')
            self.new_group ()
            
            self.ewrite (entry, 'howpublished')
            self.ewrite (entry, 'address', pre = ', ')
            self.dwrite (entry, pre = ', ')
            self.new_group ()


        # ==================================================
    	elif entry.type == Types.getentry ('incollection'):
            self.ewrite (entry, 'title')
            self.new_group ()

            if entry.has_key ('editor'):
                group = entry ['editor']
                
                if len (group) > 1: ed = ', editors'
                else:               ed = ', editor'
                    
                self.awrite (entry, 'editor', pre = 'In ', post = ed, force = 1)
            
            self.full_title (entry, book = 1, pre = ', ')
            self.new_group ()

            self.full_publisher (entry)
            self.new_group ()
            

        # ==================================================
    	elif entry.type == Types.getentry ('inproceedings'):
            self.ewrite (entry, 'title')
            self.new_group ()

            if entry.has_key ('editor'):
                group = entry ['editor']
                
                if len (group) > 1: ed = ', editors'
                else:               ed = ', editor'
                    
                self.awrite (entry, 'editor', pre = 'In ', post = ed, force = 1)
            
            self.full_title (entry, book = 1, pre = ', ')
            self.new_group ()

            self.ewrite (entry, 'address')
            self.dwrite (entry, pre = ', ')
            self.new_group ()

            if entry.has_key ('organization') or entry.has_key ('publisher'):
                self.ewrite (entry, 'organization')
                self.ewrite (entry, 'publisher', pre = ', ')
            self.new_group ()
                    

        else:
            if entry.type == Types.getentry ('manual') or \
               entry.type == Types.getentry ('phdthesis'):
                style = 'emph'
            else:
                style = None
                
            self.ewrite (entry, 'title', style = style)
            self.new_group ()

            if entry.type == Types.getentry ('masterthesis') or \
               entry.type == Types.getentry ('phdthesis'):
            
                self.ewrite (entry, 'type')
                self.ewrite (entry, 'school',  pre = ', ')
                self.ewrite (entry, 'address', pre = ', ')
                    
            elif entry.type == Types.getentry ('manual'):
                
                self.ewrite (entry, 'organization')
                self.ewrite (entry, 'address', pre  = ', ')
                self.ewrite (entry, 'edition',  pre = ', ')

            elif entry.type == Types.getentry ('techreport'):

                if entry.has_key ('type'):
                    self.ewrite (entry, 'type')
                else:
                    self.write ('Technical report')
                    
                for f in ('number', 'institution', 'address'):
                    self.ewrite (entry, f, pre = ', ')


            elif entry.type == Types.getentry ('misc'):
                self.ewrite (entry, 'howpublished')
                
            # ended by date
            self.dwrite (entry, pre = ', ')
            self.new_group ()
            

        # ==================================================
        self.ewrite (entry, 'note', post = '.')


        self.fmt.end ()
        return
    

def alpha_writer (id, fmt, database):
    w = Writer (fmt, database)

    w.run (id)
    return

def abbrv_writer (id, fmt, database):
    w = Writer (fmt, database)

    w.initials = 1
    w.run (id)
    return


Autoload.register ('style', 'Alpha', alpha_writer)
Autoload.register ('style', 'Abbrv', abbrv_writer)
