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

# Extension module for MARC files

from Pyblio import Base, Fields, Types, Autoload, Open, Iterator, Utils, Config

import re, string,sys

field_match = re.compile ('[\W\w ]+')
year_match = re.compile ('(\d\d\d\d)')

one_to_one = Config.get ('marc/mapping').data

Status_Tag = {'a':'Increase in encoding level','c':'Corrected or revised','d':'Deleted','n':'New','p':'Increase in encoding level from prepublication'}

RecType_Tag = {'a':'Language material','c':'Notated music','d':'Manuscript notated music','e':'Cartographic material','f':'Manuscript cartographic material','g':'Projected medium','i':'Nonmusical sound recording','j':'Musical sound recording','k':'Two-dimensional nonprojectable graphic','m':'Computer file','o':'Kit','p':'Mixed material','r':'Three-dimensional artifact or naturally occurring object','t':'Manuscript language material'}

RecordType = {'a':'Book','c':'Misc','d':'Misc','e':'Misc','f':'Misc','g':'Misc','i':'Misc','j':'Misc','k':'Misc','m':'Misc','o':'Misc','p':'Misc','r':'Misc','t':'Book'}

BibLevel_Tag = {'a':'Monographic component part','b':'Serial component part','c':'Collection','d':'Subunit','i':'Integrating resource','m':'Monograph/item','s':'Serial'}

ControlType_Tag = {' ':'No specific type','#':'No specific type','a':'Archival'}

EncLevel_Tag = {' ':'Full level','1':'Full level, material not examined','2':'Less-than-full level, material not examined','3':'Abbreviated level','4':'Core level','5':'Partial (preliminary) level','7':'Minimal level','8':'Prepublication level','u':'Unknown','z':'Not applicable'}

CatalogForm_Tag = {' ':'Non-ISBD','#':'Non-ISBD','a':'AACR 2','i':'ISBD','u':'Unknown'}

LinkedRecRequire_Tag = {' ':'Related record not required','#':'Related record not required','r':'Related record required'}

class MARC (Base.DataBase):
    '''Read a MARC format database from an URL.'''
    id = 'MARC'

    properties = {
        'change_id'   : 0,
        'change_type' : 0
        }

    def __init__ (self, url):
        Base.DataBase.__init__ (self, url)

        iter = iterator (url, 0)

        entry = iter.first ()
        while entry:
            self.add (entry)
            entry = iter.next ()

        return

class MARCIterator (Iterator.Iterator):

    def __init__ (self, file):
        #self.marc = s
        self.file = file
        return
    
    def first (self):
        #rewind the file
        self.file.seek (0)

        return self.next ()
    
    def next (self):
        current = None
        data    = ''

        table = {}
        norm = {}

        uniformtitle = 0

        # Skip whitespace
        while 1:
            self.marc = self.file.readline ()
            if self.marc == '': return table

            self.marc = string.rstrip (self.marc)
            if self.marc != '': break

        if RecordType.has_key(self.marc[6]): type = Types.get_entry (RecordType[self.marc[6]])
        else: type = Types.get_entry ('Book')
        norm ['Raw MARC data'] = self.marc #no preprocessing for the original data
        try:
            assert (self.marc[9] == ' ') # 'a' would be UCS/Unicode
        except AssertionError:
            return
        assert (self.marc[10] == '2' and self.marc[11] == '2')
        baseaddr = self.extract_int (12, 16)
        assert (self.marc[20:22] == '45')
        pos = 24
        while pos < baseaddr:
            tag = self.marc[pos:pos+3]
            if tag [0] == '\035' or tag [0] == '\036':
                break
            fieldlen = self.extract_int (pos + 3, pos + 6)
            startpos = self.extract_int (pos + 7, pos + 11)
            pos = pos + 12
            printline = self.marc[baseaddr + startpos:baseaddr + startpos + fieldlen]
            while printline[-1] == '\036' or printline [-1] == '\035':
                printline = printline [:-1]
            printline = string.replace (printline, '\035', '~')
            printline = string.replace (printline, '\036', '^')
            printline = string.replace (printline, '\026', ' ') #some records have this character code which is CTRL-Z or EOF, and this causes pyblio to complain about an early EOF
            subfields = re.split('\037', printline[1:]) # Subfields are separated by control key \037. Why split from printline[1:] and not printline[0:]? Because you'd get an empty subfield first and it'll spit out errors

            for subfield in subfields:
                subfield = string.strip (subfield)
                if subfield <> '':
                    subtag = tag + subfield[0]
                    field_text = field_match.search (subfield[1:])
                    if field_text: data = field_text.group ()
                    else: data = ''
                    data = string.strip (data)
                    if data <> '':
                        if data[-1] == ',' or data[-1] == ';' or data[-1] == ':' or data[-1] == '/': data = data[0:-1] #these trailing characters are ugly
                        data = string.strip (data)
                        if data[0] == '[' and data[-1] == ']': data = data[1:-1] #brackets are also ugly
                        if data[0] == '(' and data[-1] == ')': data = data[1:-1] #brackets are also ugly
                        if one_to_one.has_key (subtag):
                            if table.has_key (subtag):
                                table [subtag].append (data)
                            else:
                                table [subtag] = [data]
                        else:
                            if table.has_key (tag):
                                table [tag].append (data)
                            else:
                                table [tag] = [data]

        # Author field
        if table.has_key ('100a'):
            norm [one_to_one ['100a']] = Fields.Author (table ['100a'][0])
            del table ['100a']

        # Date/Year field
        if table.has_key ('260c') and table.has_key ('240f'):
            yr_date = year_match.search (table ['260c'][0])
            if not yr_date:
                yr_date = year_match.search (table ['240f'][0])
                if yr_date: norm [one_to_one ['240f']] = Fields.Date (yr_date.group(1))
            else:
                norm [one_to_one ['260c']] = Fields.Date (yr_date.group(1))
            del table ['260c'], table ['240f']
        elif table.has_key ('260c'):
            yr_date = year_match.search (table ['260c'][0])
            if yr_date: norm [one_to_one ['260c']] = Fields.Date (yr_date.group(1))
            del table ['260c']
        elif table.has_key ('240f'):
            yr_date = year_match.search (table ['240f'][0])
            if yr_date: norm [one_to_one ['240f']] = Fields.Date (yr_date.group(1))
            del table ['240f']

        # Title field
        if table.has_key ('245a'):
            if table.has_key ('245b'):
                fulltitle = table ['245a'][0] + ': ' + table ['245b'][0]
                del table ['245a'], table ['245b']
            else:
                fulltitle = table ['245a'][0]
                del table ['245a']
            fulltitle = string.replace (fulltitle, '/', '')
            fulltitle = string.replace (fulltitle, ' :', ': ')
            fulltitle = string.capwords (fulltitle)
            fulltitle = string.strip (fulltitle)
            norm [one_to_one ['245a']] = Fields.Text (fulltitle)

        #Keywords field
        if table.has_key ('650'):
            fullkeylist = ''
            for keyword in table ['650']:
                if keyword[-1] == '.':
                    fullkeylist = fullkeylist + keyword[0:-1] + ' ; '
                else:
                    fullkeylist = fullkeylist + keyword + ' -- '
            fullkeylist = fullkeylist[0:-3]
            norm [one_to_one ['650']] = Fields.Text (string.strip (fullkeylist))
            del table ['650']

        # The simple fields...
        for f in table.keys ():
            if one_to_one.has_key (f):
                norm [one_to_one [f]] = Fields.Text (string.join (table [f], " ; "))
            else:
                norm ['marc-' + string.lower (f)] = \
                     Fields.Text (string.join (table [f], " ; "))

        return Base.Entry (None, type, norm)

    def extract_int (self, start, end):
        return string.atoi (self.marc[start:end+1])

def opener (url, check):
	
    base = None
	
    if (not check) or (url.url [2] [-5:] == '.marc'):
        base = MARC (url)
		
    return base

def iterator (url, check):
    ''' This methods returns an iterator that will parse the
    database on the fly (useful for merging or to parse broken
    databases '''

    if check and url.url [2] [-5:] != '.marc': return

    return  MARCIterator (open (Open.url_to_local (url), 'r'))

#def writer (iter, output):
    
#    mapping = Config.get ('marc/mapping').data
#    writer (iter, output, mapping)

#    return

        
Autoload.register ('format', 'MARC', {'open'  : opener,
#                                      'write' : writer,
                                      'iter'  : iterator})
