# This file is part of pybliographer
# 
# Copyright (C) 1998-2002 Frederic GOBRY
# Email : gobry@users.sf.net
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

from Pyblio.QueryEngine import Engine
from Pyblio.Autoload import register
from Pyblio import Exceptions

import time, string, urllib, urlparse


class Medline (Engine):

    def __init__ (self, url, param):
        self.query_url = param ['query']
        self.fetch_url = param ['fetch']

        self.host = urlparse.urlparse (url) [1]
        return

    def search (self, query):
        self.running = 1

        print query

        try:
            query_field, op, term = query ['query'] [0]
        except IndexError:
            raise Exceptions.SyntaxError ('please provide a search term')

        cmd = [ term ]

        for field in ('pub_type', 'language', 'subsets', 'ages', 'kind'):
            val = query [field]
            if not val: continue
            
            cmd.append (query [field])

        if query ['abstracts']:
            cmd.append ('hasabstract')
            
        if query ['printed']:
            cmd.append ('pubstatusaheadofprint')
            
        entrez = query ['entrez']
        
        if entrez:
            params ['datetype'] = 'edat'
            params ['reldate'] = entrez
        else:
            # check if we have a correct date range
            now = time.strftime ('%Y/%m/%d', time.gmtime ())
            
            dateq = {
                'edat' : { 'from' : None, 'to' : None },
                'dp'   : { 'from' : None, 'to' : None },
                }

            for f, o, v in query ['date']:
                dateq [f] [o] = v

            for k, v in dateq.items ():
                if v ['from'] is None:
                    continue
                
                if v ['to'] is None: v ['to'] = now

                cmd.append ('%s:%s[%s]' % (v ['from'],
                                           v ['to'], k))
                
        print cmd
            
        params = {
            'db' : 'pubmed',
            'term' : string.join (cmd, ' AND '),
            'field' : query_field,
            'dopt' : 'd',
            'retmax' : 100,
            'retstart' : 0,
            'usehistory' : 'n',
            'tool' : 'pybliographer'
            }

        query_url = urlparse.urlunparse (('http',
                                          self.host,
                                          self.query_url,
                                          None,
                                          urllib.urlencode (params),
                                          None))

        print query_url
    
        f = urllib.urlopen (query_url)
        uids = []

        while 1:
            line = f.readline ()
            if not line: break

            line = string.strip (line)
            if line [0:4] == '<Id>':
                line = string.replace (line,'<Id>','')
                line = string.replace (line,'</Id>','')
                uids.append (line)

        f.close ()
        
        print uids

        self.issue ('progress', 0.1)
        if not self.running: return 0

        params = urllib.urlencode ({
            'db'     : 'pubmed',
            'report' : 'medline',
            'mode'   : 'text',
            'id'     : string.join (uids, ',')
            })


        fetch_url = urlparse.urlunparse (('http',
                                          self.host,
                                          self.fetch_url,
                                          None, params,
                                          None))

        return fetch_url.encode ('ascii'), 'medline'

    
    def cancel (self):
        self.running = 0
        return

    
register ('query', 'Medline', Medline)
