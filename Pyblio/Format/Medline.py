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

# Extension module for Medline files

from Pyblio import Base, Fields, Types, Autoload, Open, Iterator, Utils, Config

import re, string,sys

header = re.compile ('^(\w\w[\w ][\w ])- (.*)$')
contin = re.compile ('^      (.*)$')

one_to_one = Config.get ('medline/mapping').data


class MedlineIterator (Iterator.Iterator):

    def __init__ (self, file):
        self.file = file
        return
    
    
    def first (self):
        # rewind the file
        self.file.seek (0)

        return self.next ()

    def next (self):
        current = None
        data    = ''
        
        table = {}

        # Skip whitespace
        while 1:
            line = self.file.readline ()
            if line == '': return table
            
            line = string.rstrip (line)
            if line != '': break

        while 1:
            head = header.match (line)
            if head:
                if current:
                    if table.has_key (current):
                        table [current].append (data)
                    else:
                        table [current] = [data]
                        
                current = string.strip (head.group (1))
                data    = head.group (2)
            else:
                cont = contin.match (line)
                if cont:
                    data = data + ' ' + cont.group (1)
        
            line = self.file.readline ()
            if line == '': break

            line = string.rstrip (line)
            if line == '': break

        # don't forget the last item
        if current:
            if table.has_key (current):
                table [current].append (data)
            else:
                table [current] = [data]

        # create the entry with the actual fields
        norm = {}
        type = Types.get_entry ('article')
    
        if table.has_key ('UI'):
            norm [one_to_one ['UI']] = Fields.Text (table ['UI'] [0])
            del table ['UI']

        if table.has_key ('AU'):
            group = Fields.AuthorGroup ()
            
            for au in table ['AU']:
                author = Fields.Author (au)
                if author.first is not None:
                    author.first, author.last = author.last, author.first

                    # use the letters of the first name as a sequence of
                    # initials
                    author.first = string.join (author.first, '. ') + '.'
                    
                group.append (author)
                
            norm [one_to_one ['AU']] = group
            del table ['AU']

        if table.has_key ('DP'):
            fields = string.split (table ['DP'][0], ' ')
            norm [one_to_one ['DP']] = Fields.Date (fields [0])
            del table ['DP']
            
        # The simple fields...
        for f in table.keys ():
            if one_to_one.has_key (f):
                norm [one_to_one [f]] = Fields.Text (string.join (table [f], " ; "))
            else:
                norm ['medline-' + string.lower (f)] = \
                     Fields.Text (string.join (table [f], " ; "))
        
        return Base.Entry (None, type, norm)


# UI identifiant unique
# AU auteurs *
# TI titre 
# LA langue *
# MH mots clés *
# PT *  type : JOURNAL ARTICLE, REVIEW, REVIEW, TUTORIAL,CLINICAL TRIAL,
#              RANDOMIZED CONTROLLED TRIAL, LETTER, EDITORIAL, MULTICENTER STUDY,
#              NEWS, HISTORICAL ARTICLE
# DA date de ?? en yyyymmdd 
# DP date de ?? en yyyy mois +/-j
# IS 
# TA titre de la revue
# PG  
# SB 
# CY pays d'édition ?
# IP  
# VI 
# JC  
# AA semble être toujours Author ou AUTHOR
# EM date de?? en yyyymm
# AB  
# AD 
# PMID
# SO  référence complète
# RN semble indexer des substances chimiques
# TT titre dans la langue d'origine
# 4099 URL vers l'article
# 4100 URL vers abstract de l'article ??
    

class Medline (Base.DataBase):
    
    id = 'Medline'
    
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


def writer (iter, output):

    entry = iter.first ()
    while entry:

        ekeys = {}
        for k in entry.keys (): ekeys [k] = 1
        
        med = one_to_one ['UI']

        if entry.has_key (med):
            del ekeys [med]
            ui = str (entry [med])
        else:
            print "warning: entry has no medline reference"
            ui = 0
            
        output.write ('%-4.4s- %s\n' % ('UI', ui))

        med = one_to_one ['AU']
        
        if entry.has_key (med):
            del ekeys [med]
            for auth in entry [med]:
                first = auth.first or ''
                compact = []
                for seq in string.split (first, ' '):
                    compact.append (seq [0])

                first = string.join (compact, '')
                text = '%s %s' % (auth.last or '', first)
                
                output.write ('%-4.4s- %s\n' % ('AU', text))

        med = one_to_one ['DP']
        if entry.has_key (med):
            del ekeys [med]
            output.write ('%-4.4s- %s\n' % ('DP', str (entry [med])))

        # write the remaining know fields
        for key in one_to_one.keys ():
            field = one_to_one [key]

            if not ekeys.has_key (field): continue
            del ekeys [field]
            
            output.write ('%-4.4s- %s\n' % (key, Utils.format (str (entry [field]),
                                                              75, 0, 6)))
        # write the unknown fields
        remaining = ekeys.keys ()
        remaining.sort ()
        for field in remaining:
            if field [0:8] == 'medline-':
                key = string.upper (field [8:])
                output.write ('%-4.4s- %s\n' % (key, Utils.format (str (entry [field]),
                                                                   75, 0, 6)))
            
        
        entry = iter.next ()
        if entry: output.write ('\n')

        
def opener (url, check):
	
	base = None

	if (not check) or (url.url [2] [-4:] == '.med'):
		base = Medline (url)
		
	return base


def iterator (url, check):
	''' This methods returns an iterator that will parse the
	database on the fly (useful for merging or to parse broken
	databases '''

        if check and url.url [2] [-4:] != '.med': return
        
        return MedlineIterator (open (Open.url_to_local (url), 'r'))


Autoload.register ('format', 'Medline', {'open'  : opener,
                                         'write' : writer,
                                         'iter'  : iterator})
