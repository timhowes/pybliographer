# This file is part of pybliographer
#  
# Original author of Ovid reader: Travis Oliphant <Oliphant.Travis@mayo.edu>
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

# Extension module for Ovid files

from Pyblio import Base, Autoload, Types, Fields

import sys, re, string

long_month = {"Jan":'January',   "Feb":'February', "Mar":'March',
              "Apr":'April',     "May":'May',      "Jun":'June',
              "Jul":'July',      "Aug":'August',   "Sep":'September',
              "Oct":'October',   "Nov":'November', "Dec":'December'}

source_obj = re.compile(r"""
    (.*).                  # Journal
    \s+([^(]*)             # volume,
    (?:\s+no[.]([^,]*),)*  # number
    (?:\s+pt[.]([^,]*),)*  # part
    \s+                    # separator
       (\d*)\s*            # day
       ([a-zA-Z\-.]*)[.]*  # month
       \s*(\d\d\d\d),      # year
    \s+pp[.]([^.]*)[.]     # pages
    \s([^,]*),*            # Publisher
    ([^.]*).               # Address
    """,re.VERBOSE)

pages_obj = re.compile(r".*(\s+pp[.]([0-9\-]+)[.\s]*)")
year_obj  = re.compile(r".*(\s*(\d\d\d\d),)")

# Records separated by two newlines + integer + newline
split_obj = re.compile(r"<\d+>$")

def parse_so(dict):
    so_match = source_obj.match (dict ["source"])
    
    dict ["journal"] = so_match.group(1)
    dict ["volume"]  = so_match.group(2)
    dict ["number"]  = so_match.group(3)
    dict ["part"]    = so_match.group(4)
    dict ["year"]    = so_match.group(7)
    dict ["month"]   = string.replace(so_match.group(6),'.','')
    
    if len (dict ["month"]) == 3:
        dict ["month"] = long_month [dict ["month"]]
        
    dict["pages"] = string.replace(so_match.group(8),'-','--')
    
    if so_match.group(10):
        dict["pubadd"] = string.lstrip(so_match.group(10))
        dict["publisher"] = string.replace(so_match.group(9),"Publisher: ","")
    else:
        dict["pubadd"] = so_match.group(9)
        dict["publisher"] = ""
    
    return dict

def parse2_so(dict):
    
    dict["journal"] = dict["source"]
    
    pp_match = pages_obj.match(dict["journal"])
    
    if pp_match:
        dict["pages"]   = string.replace(pp_match.group(2),'-','--')
        dict["journal"] = dict["journal"][:pp_match.start(1)] + \
                          dict["journal"][pp_match.end(1):]
    else:
        dict["pages"] = ""
        
    yr_match = year_obj.match(dict["journal"])
    
    if yr_match:
        dict["year"] = yr_match.group(2)
        dict["journal"] = dict["journal"][:yr_match.start(1)] + \
                          dict["journal"][yr_match.end(1):]
    else:
        dict["year"] = ""

    if not (yr_match or pp_match):
        raise "TypeError", "nothing found"
        return None
    
    dict ["volume"]    = ""
    dict ["number"]    = ""
    dict ["part"]      = ""
    dict ["month"]     = ""
    dict ["pubadd"]    = ""
    dict ["publisher"] = ""
    
    return dict

subs_pat   = re.compile(r"\s{2,}")
search_pat = re.compile(r"\n[A-Z]\w+(?:\s+\w+)*?\n[ ]{2,2}")

ovid2dict = {"Accession Number":"ui", "Author":"author", "Editor":"editor",
             "Source":"source", "Abstract":"abstract", "Title":"title",
             "Subject Headings":"keywords", "Corporate Author":"corp_auth",
             "Country of Publication":"cop"}

def get_entry (entry):
    
    thedict = {}
    
    entry = "\n" + entry

    # This is the list of entries actually parsed if present
    tofind = ["Accession Number", "Author", "Editor", "Title", "Source",
              "Abstract", "Subject Headings"]

    for field in tofind:
        indx = string.find(entry,"\n"+field+"\n")
        if indx >= 0:
            start_ind = indx + 2 + len(field)
            try:
                end_ind = start_ind + search_pat.search(entry[start_ind:]).start(0)
                thedict [ovid2dict [field]] = \
                        subs_pat.sub (" ",
                                      string.strip (entry [start_ind:end_ind]))
            except:
                thedict [ovid2dict [field]] = \
                        subs_pat.sub (" ",
                                      string.strip (entry [start_ind:]))

    if thedict.has_key("author"):
        temp = string.split(thedict["author"], '. ')
        temp[-1] = temp[-1][:-1]
        thedict["author"] = temp
        
    if thedict.has_key("editor"):
        temp = string.split(thedict["editor"], '; ')
        temp[-1] = temp[-1][:-1]
        thedict["editor"] = temp

    if thedict.has_key("keywords"):
        temp = string.split(thedict["keywords"],'. ')
        temp[-1] = temp[-1][:-1]
        thedict["keywords"] = temp
        
    return thedict

def make_key (dict):
    try:
        key = string.replace(string.lower(dict["author"][0]),"'","_")
        key = key[:string.find(key," ")]
        if len(dict["author"]) > 1:
            key = key + ":etal" + `len(dict["author"])`

    except:           # no authors take key from title
        thelist = string.split(dict["title"]," ")
        key = ""
        num = 0
        inum = 0; num_words = len(thelist)
        while num < 3:
            if inum >= num_words:
                break
            a_word=thelist[inum]
            if a_word not in ["the","The","a","A","An","an","of","Of"]:
                key = key + string.lower(a_word) + ":"
                num = num + 1
            inum = inum + 1
        try:                # Just in case key is still ""
            key = key[:-1]
        except:
            pass

    key = key + "_"
    return key



class Ovid (Base.DataBase):

    id = 'Ovid'

    properties = {
        'edit'        : 1,
        'add'         : 1,
        'remove'      : 1,
        }

    def __init__ (self, name):
        Base.DataBase.__init__ (self, name)

        # parse entries
        fid  = open (self.name, 'r')
        k    = 0
        data = ''
        
        # skip initial header
	while 1:
	    line = fid.readline ()
	    if line == '': break
	    
	    if split_obj.match (line):
	        break
	    
	while 1:
	    line = fid.readline ()
	    if line == '': break
	    
	    if split_obj.match (line):
	        
	        if data != '':
	            k = k + 1
	            try:
	                entry_dict = get_entry (data)
	            except:
	                raise IOError, "can't read entry %d" % (k)
	
	            allsource = 1
	            
	            try:
	                entry_dict = parse_so (entry_dict)
	            except:
	                try:
	                    entry_dict = parse2_so (entry_dict)
	                except:
	                    allsource = 0
	                    
	            self.__append_entry (entry_dict)
	            data = ''
	        continue
	
	    data = data + line
            
        fid.close ()
        return

    
    def __repr__ (self):
        return "<Ovid database (" + `len (self)` + \
               " entries)>"


    def __append_entry (self, dict):
        # determine type...
        type = 'article'
        
        procee = (string.find (dict["source"], 'roceedings') > 0) or \
                 (string.find (dict["title"], 'roceedings')  > 0)

        if procee:
            if dict.has_key("author"):
                type = 'inproceedings'
            else:
                type = 'proceedings'
        
        type = Types.getentry (type)

        # construct unique key
        basekey = make_key (dict)
        key = basekey
        k   = 1

        while self.has_key (Base.Key (self, key)):
            key = basekey + str (k)
            k = k + 1

        # convert fields
        entrydict = {}
        for f in dict.keys ():
            ftype = Types.gettype (type, f)
            
            if ftype == Types.TypeAuthor:
                # Author
                val = Fields.AuthorGroup ()
                for auth in dict [f]:
                    # Try some split method
                    fields = string.split (auth, ' ')
                    last = fields [0]
                    if len (fields) > 1:
                        first = string.join (fields [1:], ' ')
                        
                    val.append (Fields.Author ((None, first, last, None)))
                    
            elif ftype == Types.TypeDate:
                # Date
                try:
                    val = Fields.Date (int (dict [f]))
                except ValueError:
                    val = Fields.Text (dict [f])
            else:
                # Any other text
                val = Fields.Text (dict [f])


            entrydict [f] = val

        fullkey = Base.Key (self, key)
        self [fullkey] = Base.Entry (fullkey, key, type, entrydict)


def my_open (entity, check):
	
    method, address, file, p, q, f = entity
    base = None
	
    if (not check) or (method == 'file' and file [-5:] == '.ovid'):
        base = Ovid (file)
		
    return base

    
Autoload.register ('format', 'Ovid', {'open'  : my_open})


