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


""" This module is a formatter for AbiWord """


from Pyblio import Formatter, Autoload
import string


class AbiWord (Formatter.Formatter):

    coding = 'abiword'
    
    def write (self, text, style = None):
        if   style == 'bold':
            self.out.write ('<c props="font-weight:bold">%s</c>' % text)
        elif style == 'italic' or style == 'slanted':
            self.out.write ('<c props="font-style:italic">%s</c>' % text)
        elif style == 'emph':
            self.out.write ('<c props="font-weight:bold">%s</c>' % text)
        else:
            self.out.write (text)

    def start_group (self, id, table = None):
        self.out.write ('<section>\n')
        return
    
    def end_group (self):
        self.out.write ('</section>\n')
        return

    def start (self, key, entry):
        if key is None: key = self.next_key ()
        self.out.write ('<p props="text-align:justify; margin-left:0.7in; text-indent:-0.7in">')
        self.out.write ('[%s]\t' % key)
        return

    def end (self):
        self.write ('</p>\n')
        return

    def separator (self):
        self.out.write (' ')
        return

    
Autoload.register ('output', 'abiword', AbiWord)

