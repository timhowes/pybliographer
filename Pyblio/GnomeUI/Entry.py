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

from gtk import *
import string

from Pyblio.GnomeUI import Utils
from Pyblio import Config, recode, Fields

from gnome import url

has_gtkhtml = 1

try:    from gtkhtml import *
except: has_gtkhtml = 0


# This is the new HTML-based entry

class HTMLEntry:
    ''' Displays a bibliographic entry as simple text '''

    header = '<html><body bgcolor="#ffffff">'
    
    def __init__ (self):
        ''' Create the graphical widget '''
        
        self.text = GtkHTML ()
        self.text.load_empty ()
        self.text.connect('link_clicked', self.link_clicked)
        
        self.w = GtkScrolledWindow ()
        
        self.w.set_policy (POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        self.w.add (self.text)

        self.text.show ()
        
        # currently, nothing to display
        self.entry = None
        return

    def link_clicked (self, html, link):
        url.show (link)
        return

    
    def display (self, entry):
        self.entry = entry

        # Display this entry
        content = self.text.begin ()

        self.text.write (content, self.header)
        
        self.text.write (content, ('<font color="#0000ff"><h1>%s [' % entry.type.name) +
                         html (str (entry.key.key)) + '] </h1></font>')
        
        dico = entry.keys ()

        self.text.write (content, '<table>')
        
        for f in entry.type.fields:
            
            field = string.lower (f.name)
            
            if entry.has_key (field):
                self.text.write (content, '<tr><td><font color="#ff0000">' +
                                 html (f.name) + '</font>&nbsp;</td>')

                data = entry [field]
                if isinstance (data, Fields.URL):
                    print "url: %s" % str (data)
                    data = '<a href="%s">%s</a>' % (str (data), html (str (data)))
                else:
                    data = html (str (data))
                    
                self.text.write (content, '<td>' + data + '</td></tr>')
                dico.remove (field)

        self.text.write (content, '</table><hr><table>')

        for f in dico:
            self.text.write (content, '<tr><td><font color="#ff0000">' +
                             html (f) + '</font>&nbsp;</td>')

            data = entry [f]
            if isinstance (data, Fields.URL):
                data = '<a href="%s">%s</a>' % (str (data), html (str (data)))
            else:
                data = html (str (data))
                
            self.text.write (content, '<td>' + data + '</td></tr>')

        self.text.write (content, '</table>')
        
        self.text.end (content, HTML_STREAM_OK)
        return

    def clear (self):
        self.text.load_from_string (self.header)
        return


# This is the old GtkText-based entry

class ClassicEntry:
    ''' Displays a bibliographic entry as simple text '''

    def __init__ (self):
        ''' Create the graphical widget '''
        
        self.text = GtkText ()
        self.text.set_word_wrap (1)
        
        self.w = GtkScrolledWindow ()
        self.w.set_policy (POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        self.w.add (self.text)

        self.text.show ()

        # currently, nothing to display
        self.entry = None
        return

    def display (self, entry):
        self.entry = entry

        if not self.entry:
            self.text.delete_text (0, -1)
            return
        
        # Display this entry
        self.text.freeze ()
        self.text.delete_text (0, -1)
        
        self.text.insert (Config.get ('gnomeui/monospaced').data,
                          Utils.color['blue'], None,
                          entry.type.name)
        self.text.insert_defaults (' ['+ str (entry.key.key) + ']\n\n')
        
        dico = entry.keys ()
        
        # Search the longest field
        mlen = 0
        for f in dico:
            mlen = max (mlen, len (f))

        for f in entry.type.fields:
            
            field = string.lower (f.name)
            
            if entry.has_key (field):
                sp = ' ' * (mlen - len (f.name))
                self.text.insert (Config.get ('gnomeui/monospaced').data,
                                  Utils.color ['red'], None,
                                  f.name + ': ' + sp)
                self.text.insert_defaults (str (entry [field]) + '\n')
                dico.remove (field)


        self.text.insert_defaults ('\n')
            
        for f in dico:
            sp = ' ' * (mlen - len (f))
            self.text.insert (Config.get ('gnomeui/monospaced').data,
                              Utils.color['red'], None,
                              f + ': ' + sp)
            self.text.insert_defaults (str (entry [f]) + '\n')

        self.text.thaw ()
        return

    def clear (self):
        self.text.delete_text (0, -1)
        return

if has_gtkhtml:
    html = recode.recode ("latin1..html")
    Entry = HTMLEntry
else:
    Entry = ClassicEntry


        
