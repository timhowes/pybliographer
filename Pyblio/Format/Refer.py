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

# Extension module for Refer files

from Pyblio import Base, Types, Fields, Config, Autoload

import re, string, sys

tag_re = re.compile ('%(.) (.*)')


class ReferBase (Base.DataBase):

    id = 'Refer'
    
    properties = {
        #'edit'        : 1,
        #'add'         : 1,
        #'remove'      : 1,
        }
	

    def __init__ (self, name, type = 'refer'):
        Base.DataBase.__init__ (self, name)

        type_table    = Config.get ("%s/table" % type).data
        endnote_types = Config.get ("endnote/types").data
        
        # parse entries
        fid  = open (self.name, 'r')

        data = ''
        fields = {}
        type   = None
        key    = 0

        finished = 0
        ln = 0
        while not finished:
	    line = fid.readline ()
            ln = ln + 1
            
	    if line == '': finished = 1

            line = string.strip (line)
            
            if line == '' and len (fields.keys ()) > 0:
                # ----- create the whole entry -----
                # determine the real type
                type = None
                if fields.has_key (' type '):
                    if endnote_types.has_key (fields [' type ']):
                        type = endnote_types [fields [' type ']]
                        
                    del fields [' type ']

                while 1:
                    if fields.has_key ('journal'):
                        type = 'article'
                        break
                    if fields.has_key ('booktitle'):
                        type = 'inbook'
                        break
                    if fields.has_key ('volume') or fields.has_key ('number'):
                        type = 'inproceedings'
                        break
                    if fields.has_key ('author') and fields.has_key ('title'):
                        type = 'unpublished'
                        break
                    
                    type = 'misc'
                    break
                
                # get the real instances of every component
                name  = "key-%d" % key ; key = key + 1
                real  = Base.Key (self, name)
                entry = Types.getentry (type)

                for f in fields.keys ():
                    type = Types.gettype (entry, f)

                    if type == Types.TypeAuthor:
                        group = Fields.AuthorGroup ()
                        
                        for auth in fields [f]:
                            group.append (Fields.Author (auth))
                            
                        fields [f] = group
                    elif type == Types.TypeDate:
                        if len (fields [f]) > 1:
                            sys.stderr.write ("%s:%d: warning: field `%s' is defined" +
                                              " more than once\n" % (self.name, ln, f))
                            continue
                        fields [f] = Fields.Date (fields [f] [0])
                    else:
                        if len (fields [f]) > 1:
                            sys.stderr.write ("%s:%d: warning: field `%s' is defined" +
                                              " more than once" % (self.name, ln, f))
                            continue
                        fields [f] = Fields.Text (fields [f] [0])
                        
                self [real] = Base.Entry (real, entry, fields)
                
                # start a new entry
                fields = {}
                type = None
                data = ''
                continue
            
            t = tag_re.match (line)
            # we matched a new field start
            if t:
                if not type is None:
                    
                    if fields.has_key (type):
                        fields [type].append (string.strip (data))
                    else:
                        fields [type] = [string.strip (data)]
                    
                type = t.group (1)
                if not type_table.has_key (type):
                    print "%s:%d: warning: key `%s' has been skipped" % (self.name, ln, type)
                    type = None
                    data = ''
                else:
                    # store the current field
                    type = type_table [type]
                    data = t.group (2)
                    
                continue

            # in the general case, append the new text
            data = data + ' ' + line
            

def refer_open (entity, check):
	
    method, address, file, p, q, f = entity
    base = None
	
    if (not check) or (method == 'file' and file [-6:] == '.refer'):
        base = ReferBase (file, 'refer')
		
    return base

def en_open (entity, check):
	
    method, address, file, p, q, f = entity
    base = None
	
    if (not check) or (method == 'file' and file [-4:] == '.end'):
        base = ReferBase (file, 'endnote')
		
    return base
    
Autoload.register ('format', 'Refer',   {'open'  : refer_open})
Autoload.register ('format', 'EndNote', {'open'  : en_open})

