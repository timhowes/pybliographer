# This file is part of pybliographer
# 
# Copyright (C) 2002, Peter Schulte-Stracke
# Email : peter.schulte-stracke@t-online.de
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

"""TaggedReader -- read data from records with tags (Marc, Medline, etc.)

      ##################################################
      #                                                #
      #           E X P E R I M E N T A L              #
      #                                                #
      ##################################################

Class TaggedReader -- base class for input modules that read data that
contain a category code in front of the data. Typical examples are
classical MARC, Medline, MAB, Refer and many more.

XXXX Update description in Todo 

"""
from Pyblio import Import
import re, string

_discard_tag = []
_discard_rx = ''



class TaggedReader(Import.ImportReader):
    """
    Parameters are (missing):

    """
    def __init__(self, tagcol=0,
                 discard_tag=None, discard_rx=None,
                 *args, **argh):

        self.cache = {'': self.do_leader} 
        self.tagcol = tagcol
        discards = discard_tag or _discard_tag
        discardr = discard_rx or _discard_rx
        if discardr:
            discards.append(discardr)
        if discards:
            self.discardrx = re.compile(string.join(discards,'|'))
        else:
            self.discardrx = None
        print discards

        Import.ImportReader.__init__(self, *args, **argh)
        return

    # input to parse is an entry (note that connection to the rest of the
    # system is via self) and the data that comes essentially in two
    # forms: a sequence of text lines (e.g. for Text Reader), and a
    # sequence of sequences, the head of which being the tag (empty
    # string for the leader).

    def start_file (self, *args, **argh):
        if self.test_iso2709 (self.source):
            pass
        
        
    def parse (self, e, x):

        self.begin_record(e, x)
       
## it may be convenient, if the read_next routine already assembles
## continuation lines. Let's assume this

        for i in x:

            tag = i[0]
            data = i[1:]
            if self.discardrx and self.discardrx.match(tag):
                continue
                      
            if len(data) > 1:
                data = self.prepare_data(data)

            if self.cache.has_key(tag):
                self.cache[tag] (tag, data)
            else:
                methname = 'do_'+str(tag)

                if hasattr(self, methname):
                    method = getattr(self, methname)
                else :
                    method = self.do_tag
                    
                method (tag, data)
                self.cache[tag] = method

        self.end_record(e, x)
        print '--------------------------------------------------'
        print `e`
        return self.entry


### In need of subclass implementation
    
    def read_next (self):
        """ """
        raise NotImplementedError
    
    def do_leader (self, tag, data):
        
        raise NotImplementedError

    def do_tag (self, tag, data):
        #### ???? generically put the stuff into extra data 
        raise NotImplementedError

    def unpack_iso2709 (self, data):
    
        """Standard ISO 2709  unpack routine"""

        leader = data.read(24)
        length = int (leader[0:5])
        basead = int (leader[12:17])
        direct = data.read(basead - 24)
        assert direct[-1] == ''
        content= data.read(length - basead)
        assert content [-1] == ''

        lines = [['', leader]]

        l1, l2, l3 = int(leader[20]), int(leader[21]), int(leader[22])
        pos = 0
        while pos < len(direct)-1:
            p1 = pos + 3
            p2 = p1 + l1
            p3 = p2 + l2
            p4 = p3 + l3
            tag     = direct[pos:p1]
            flength = int(direct[p1:p2]) - 1 # last character is 0x1d
            fbegin  = int(direct[p2:p3])
            pos = p4
            lines.append((tag, content[fbegin: fbegin+flength]))
        self.control.set_progress(add=length)
        return lines

    def test_iso2709 (self, data):

        try:
            leader = data.read(24)
            length = int (leader[0:5])
            basead = int (leader[12:17])
            record = data.read(length-24)
            if record [-2:] == '' and record [basead-25] == '':
                data.seek(0)
                return 1
        except : pass # traceback.print_exc()
        return None

 
            
