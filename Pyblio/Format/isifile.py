#This file is part of Pybliographer
# 
# Copyright (C) 2001 Peter Schulte-Stracke
# Email : Peter.Schulte-Stracke@t-online.de
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

import getpass, re, rfc822, string, time, types

from Pyblio import Autoload, Base, Coco, Fields, Iterator, Open, Types, Utils
from Pyblio.Format.TaggedReader import TaggedReader
from Pyblio.Import import add_simple_field, add_simple_field_nr

login_name = getpass.getuser()

key_map = {
    'AB' : ('abstract', ' '),
    'AU' : ('author', '  '),
    'CR' : ('citedref', ' ; '),
    'C1' : ('authoraddress', ' ; '),
    'DE' : ('keywords', ' '),
    'IS' : ('number', ' ; '),
    'LA' : ('language', ' ; '),
    'PD' : ('month', ' ; '),
    'PY' : ('date', ' ; '),
    'SE' : ('series', ' '),
    'SN' : ('issn', ' ; '),
    'SO' : ('journal', ' ; '),
    'TI' : ('title', ' '),
    'UT' : ('sourceid', ' ; '),
    'VL' : ('volume', ' ; ')}

xheader  = re.compile('^(\w\w|\w\w+:)( (.*))$')
header   = re.compile('^(\w\w)( (.*))$')
contin   = re.compile('^   (.*)$') 
sporadic = re.compile('^isifile-(..)$')

field_map = None

def reverse_mapping(map):
    remap = {}
    for key in map.keys():
        remap[map[key][0]] = key
    return remap


output = None                  # set by 

def output_write(key, text):
    # A text is either a string or a list:
    if type(text) == types.ListType:
        output.write ('%2s %s\n' %(key, text[0]))
        for t in text[1:]:
            output.write ('   %s\n' %(t))
    elif str(text):    
        output.write ('%2s %s\n' % (key, Utils.format(
            str (text), 70, 0, 3)))
pagenum  = re.compile('(\d) p\.')
keywds   = re.compile('(.*)\[ISI:\] *(.*);;(.*)')


class IsifileIterator(TaggedReader):
    ''' This class exports two functions: first and next,
    each of which returns an bibliographic entry from the input file.
    In addition is saves extraneous text (pre- and postamble).'''

    def __init__(self, file, control=None):
        self.extraneous = []
        self.isifileformat = None
        self.isifileinfo = None
        TaggedReader.__init__ (self,
            file=file, control=control,
            tagcol=5
        )
        self.current_line = ''
        self.firstpg, self.lastpg, self.numberpg = [''], [''], ['']

## the following could go into __init__ as well
        
    def start_file(self, *args, **argh):
        self.source.seek(0)
        self.current_line = self.source.readline()
        print self.current_line
        file_notes, file_time, file_version, file_format = ('','','','')
        while self.current_line:

            assert self.current_line != ''
            head = xheader.match(self.current_line)
            if not head :
                pass
            elif head.group(1) == 'Date:':
                file_time = time.strftime(
                    "%Y-%m-%d %H:%M", rfc822.parsedate(head.group(2)))
            elif head.group(1) == 'Notes:':
                file_notes = string.strip(head.group(2))
            elif head.group(1) == 'FN':
                file_format = head.group(2)
            elif head.group(1) == 'VR':
                file_version = head.group(2)
            elif len(head.group(1)) == 2 :
                break
            else :
                pass
            self.extraneous.append(self.current_line)
            self.current_line = self.source.readline()
            print self.current_line

        self.isifileformat = self.isifileformat or "Isifile format %s(%s)" % (
            file_format, file_version)
        self.isifileinfo = self.isifileinfo or "ISI %s (%s) %s" %(
            file_time, file_notes, login_name)
        return 

    def read_next (self):
        
        lines = []
        line = []
        print 'READ NEXT FIRST:', self.current_line
        while self.current_line == '\n':
            self.current_line = self.source.readline()
        if not self.current_line : return None

        while self.current_line != '\n':
            head = xheader.match(self.current_line)

            if head :
                # tag available
                tag = head.group(1)
                if line: lines.append(line)
                line  = [tag, head.group(3)]

            else:
                # no tag
                cont = contin.match(self.current_line)
                if cont : 
                    val = cont.group(1)
                    line.append(val)

            self.current_line = self.source.readline()
        while self.current_line == '\n':
            self.current_line = self.source.readline()
        lines.append (line)
        return lines


    def do_AU (self, tag, data):
        #print 'DO_AU: ', tag, data
        group = Fields.AuthorGroup()
        for item in data:
            if string.strip(item) =='[Anon]' :
                auth = item ### this is dubious, isn't it?
            else:        
                name, firstn = string.split (item, ',')
                auth = name + ', '
                for i in string.strip(firstn):
                    auth = auth + i +'. '
                    group.append (Fields.Author(auth))
        #print `group`
        #print `self.entry.dict`
        self.entry.dict['author'] = group
        return

    def do_BP (self, tag, data):
        self.firstpg = data
        return

    def do_EP (self, tag, data):
        self.lastpg = data
        return

    def do_PG (self, tag, data):
        self.numberpg = data
        return

    def do_PT (self, tag, data):
        print 'PT:', data
        if string.strip(data[0]) != 'J':
            print
            'Warning: Unknown type of entry (%s) -- may need editing.' %(
                data)
        return

    def do_TI (self, tag, data):

        add_simple_field_nr(self.entry, 'title', data)
        return
    
    def do_tag (self, tag, data):

        print 'DO_TAG:', tag, data
        in_table = {}
        type = Types.get_entry ('article')
        self.entry.type = type    


##         if tag == 'PY':
##             val = lines[key][0]
##             in_table['date'] = Fields.Date(val)
##             del lines[key]

##         if tag == 'ID':
##             val = "[ISI:] %s ;;" %(string.lower(string.join(lines[key], ' ')))
##             if lines.has_key('DE'):
##                 lines['DE'].append ('; ' + val)
##             else :
##                 lines['DE'] = [val]
##             del lines[key]    


        if key_map.has_key(tag):
            add_simple_field(self.entry, key_map[tag][0],
                             data, key_map[tag][1])

        return

    def end_record (self, entry, lines, *args, **argh):
        add_simple_field (entry, 'pages', ['%s-%s' % (
            self.firstpg[0], self.lastpg[0])])
        add_simple_field (entry, 'size', ['%s pp.' %(self.numberpg[0])])
        return    

class Isifile (Base.DataBase):
    '''Read a Isifile format database from an URL.'''
    id = 'Isifile'
    
    properties = {
        'change_id'   : 0,
        'change_type' : 0
        }

    def __init__ (self, url):
        Base.DataBase.__init__ (self, url)

        iter = iterator (url, 0)
        entry = iter.first ()
        self.preamble = iter.extraneous
        while entry:
            self.add (entry)
            entry = iter.next ()
        self.postamble = iter.extraneous    
        return

def writer (iter, output_stream, preamble=None, postamble = None):
    '''Write data given by an iterator, as well as an
    optional pre- and postamble, onto an output stream.'''

    remaining = {}
    text = []
    global field_map, output
    output = output_stream
    field_map = field_map or reverse_mapping(key_map)
    if preamble: output.writelines(preamble)
    output_write('FN', 'ISI Export Format')
    output_write('VR', '1.0')
    entry = iter.first()
    while entry:
        
        remaining = {}
        for fld in entry.keys():
            if field_map.has_key(fld):
                remaining[fld] = field_map[fld]
            else:
                m = sporadic.match(fld)
                if m:
                    remaining[fld] = string.upper(m.group(1))
                else:
                    remaining[fld] = '%% * ' + fld + ' * '
                    
        
        if not entry.has_key('isifile-pt'):
            output_write('PT','J')

        if entry.has_key ('author'):
            authors = []
            for author in entry['author']:
                initials = author.initials()
                initials = re.sub('\. *','',initials)
                authors.append( '%s, %s' % (author.last, initials))
            del remaining ['author']    
            output_write('AU', authors)    

        fld = 'title'
        if entry.has_key(fld):
            output_write('TI',str(entry[fld]))
            del remaining[fld]

        fld = 'journal'
        if entry.has_key(fld):
            output_write('SO',string.upper(str(entry[fld])))
            del remaining[fld]
        fld = 'pages'
        if entry.has_key (fld):
            for pair in string.split (str(entry[fld]), ' ; '):
                beginpg, endpg = string.split(pair, ' -- ')
                output_write('BP', beginpg)
                output_write('EP', endpg)
            del remaining[fld]
            

        fld = 'size'
        if entry.has_key(fld) :
            m = pagenum.match(str(entry[fld]))
            if m :
                output_write('PG', m.group(1))
            del remaining[fld]

        fld = 'month'
        if entry.has_key(fld):
            output_write('PD',string.upper(str(entry[fld])))
            del remaining[fld]

        fld = 'citedref'
        if entry.has_key(fld):
            output_write('CR',string.split(str(entry[fld]), ' ; '))
            del remaining[fld]

        fld = 'keywords'
        if entry.has_key(fld):
            val = str(entry[fld])
            m = keywds.match (val)
            if m:
                output_write('ID', string.upper(m.group(2)))
                val = m.group(1) + m.group(3)
            output_write ('DE', val)     
            del remaining[fld]
        for field in remaining.keys():
            output_write (remaining[field], entry [field])
        output.write('ER\n')     
        entry = iter.next()
        if entry: output.write('\n')
    if postamble: output.writelines(postamble)
    return entry

def opener (url, check):
        
        base = None
        if (not check) or (url.url [2] [-4:] == '.isi'):
                base = Isifile (url)
        return base


def iterator (url, check):
        ''' This methods returns an iterator that will parse the
        database on the fly (useful for merging or to parse broken
        databases '''

        if check and url.url [2] [-4:] != '.isi': return
        
        return IsifileIterator (open (Open.url_to_local (url), 'r'))

Autoload.register ('format', 'Isifile', {'open': opener,
                                         'write': writer,
                                         'iter': iterator})
