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

# Extension module for Medline files

from Pyblio import Base, Fields, Types, Autoload

import re, string,sys

header = re.compile ('^(\w\w[\w ][\w ])- (.*)$')
contin = re.compile ('^      (.*)$')


def parse_one (fh):
    current = None
    data    = ''

    table = {}

    # Skip whitespace
    while 1:
        line = fh.readline ()
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
        
        line = fh.readline ()
        if line == '': break

        line = string.rstrip (line)
        if line == '': break
        
    if current:
        table [current] = data
        
    return table

one_to_one = {
    'TI' : 'title',
    'LA' : 'language',
    'MH' : 'keywords',
    'AD' : 'affiliation',
    'AB' : 'abstract',
    'AD' : 'authorAddress',
    'TA' : 'journal',
    'CY' : 'country',
    'PG' : 'pages',
    'IP' : 'number',
    'VI' : 'volume',
    }

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
    
    properties = {}

    def __init__ (self, name, type = 'refer'):
        Base.DataBase.__init__ (self, name)

        fh = open (name, 'r')

        while 1:
            table = parse_one (fh)
            if not table.keys ():
                break

            (key, type, table) = self.__normalize (table)
            self [key] = Base.Entry (key, type, table)

        return


    def __normalize (self, table):
        norm = {}
        key  = None
        type = Types.getentry ('article')
    
        if table.has_key ('UI'):
            key = Base.Key (self.key, 'medline-' + table ['UI'] [0])

        if table.has_key ('AU'):
            group = Fields.AuthorGroup ()
            
            for au in table ['AU']:
                author = Fields.Author (au)
                if author.first is not None:
                    author.first, author.last = author.last, author.first
                    
                group.append (author)
                
            norm ['author'] = group

        if table.has_key ('DP'):
            fields = string.split (table ['DP'][0], ' ')
            norm ['year'] = Fields.Date (fields [0])
            
        # The simple fields...
        for f in one_to_one.keys ():
            if table.has_key (f):
                norm [one_to_one [f]] = Fields.Text (string.join (table [f], " "))

        return key, type, norm

    def __repr__ (self):
        return "<Medline database (%d entries)>" % len (self)


# --------------------------------------------------
# Register a method to open BibTeX files
# --------------------------------------------------

def my_open (entity, check):
	
	method, address, file, p, q, f = entity
	base = None

	if (not check) or (method == 'file' and file [-4:] == '.med'):
		base = Medline (file)
		
	return base


Autoload.register ('format', 'Medline', {'open'  : my_open})
