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

import string, os, sys

''' System for Configuration handling '''

class ConfigItem:

    def __init__ (self, name, description, hook = None, user = None):
        self.name        = name
        self.description = description

        # callback definition
        self.hook     = hook
        self.userdata = user

        self.data = None
        return

    def set (self, value):

        # eventually call the hook
        if self.hook:
            if not self.hook (self, value, self.userdata):
                raise ValueError, "value refused by hook"

        self.data = value
        return

    def get (self):
        return self.data
    

class Storage:

    def __init__ (self):
        self.items = {}
        self.sources = {}
        return


    def eventually_resolve (self, key):
        if self.items.has_key (key): return
        
        domain = string.split (key, '/') [0]
        
        if self.sources.has_key (domain):
            file = self.sources [domain]
            del self.sources [domain]

            execfile (file)

        return


    def domains (self):
        # get all domains from the keys
        doms = map (lambda key: string.split (key, '/') [0], keys ())
        
        # simplify the list
        hsht = {}
        def fill_hash (key, hsht = hsht): hsht [key] = 1
        map (fill_hash, doms + self.sources.keys ())

        return hsht.keys ()

    def keys_in_domain (domain):
        self.eventually_resolve (domain)

        # simplify the list
        def test_dom (key, dom = domain):
            f = string.split (key, '/')
            if f [0] == dom:
                return 1
            return 0
    
        return filter (test_dom, keys ())
        
    def keys (self):
        return self.items.keys ()

    
    def has_key (self, key):
        self.eventually_resolve (key)
        return self.items.has_key (key)


    def __getitem__ (self, key):
        self.eventually_resolve (key)
        return self.items [key]
        

    def __setitem__ (self, key, value):
        self.items [key] = value
        return

    def parse_dir (self, dir):
        files = map (lambda x, dir = dir: \
                     os.path.join (dir, x), os.listdir (dir))

        for filename in files:
            if filename [-3:] == '.py':
                domain = string.lower (os.path.split (filename [:-3]) [1])
                self.sources [domain] = filename
        return

        
ConfigItems = Storage ()


def define (key, description, hook = None, user = None):
    if ConfigItems.has_key (key):
        raise KeyError, "key `%s' already defined" % key

    ConfigItems [key] = ConfigItem (key, description, hook, user)
    return


def set (key, value):
    try:
        ConfigItems [key].set (value)
    except KeyError:
        sys.stderr.write ("pybliographer: warning: configuration key `%s' is undefined\n" % key)
    return


def get (key):
    return ConfigItems [key]


def keys ():
    return ConfigItems.keys ()


def has_key (key):
    return ConfigItems.has_key (key)


def domains ():
    return ConfigItems.domains ()


def keys_in_domain (domain):
    return ConfigItems.keys_in_domain ()


def parse_directory (dir):
    ConfigItems.parse_dir (dir)
    return

