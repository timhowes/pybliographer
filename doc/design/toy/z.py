import string

from ZODB import FileStorage, DB
from Persistence import Persistent

import api

class Database (api.Database):
    
    ''' A complete pybliographer database. Every entry manipulated by
    the system is connected to such a database. '''
    
    def __init__ (self, uri, create = 0):
        storage = FileStorage.FileStorage (uri)
        db = DB (storage)
        cnx = db.open ()
        
        self.root = cnx.root ()
        
        for k in ('role', 'index'):
            if not self.root.has_key (k):
                self.root [k] = {}
        for k in ('manif', 'set'):
            if not self.root.has_key (k):
                self.root [k] = []
        return

    def commit (self):
        ''' Commit the set of local changes to the database '''
        get_transaction ().commit ()
        return
    
    def roles (self):
        ''' Return a dict of available roles '''
        return self.root ['role']


    def save (self):
        ''' Save the database  '''
        pass

    def content (self):
        ''' Return the Set containing all the manifestations. '''
        s = Set (self)
        s.value = self.root ['manif']
        return s
    
    def index (self, role):
        ''' Return an Index to browse a given role. '''
        pass

    def complete (self):
        ''' Return a list of values that match a specific part of a
        role. '''
        pass
    


class Role (Persistent, api.Role):

    ''' Detailed information about an attribute role. A role can be a
    specialization of another role. A role object can be used as a key
    in a hash table.'''

    def __init__ (self, db, name, type, parent = None):
        ''' Create a new role and insert it in the DB '''
        
        self.name = name
        self.type = type
        self.parent = parent
        self.desc = {}

        self.db = db
        
        db.root ['role'] [name] = self
        db.root._p_changed = 1
        return

    def kill (self):
        ''' Kill the role from the DB '''
        del self.db.root ['role'] [self.name]
        self.db.root._p_changed = 1
        return

    def get (self):
        """ Get the intl'ed info about the role """
        pass

    def set (self, info):
        """ Set the intl'ed info about the role """
        pass

    

class Set (Persistent, api.Set):

    ''' Set of Manifestations, resulting from a query or from user
    manipulations'''

    def __init__ (self, db, query = None, order = None, value = None):
        self.q = query
        self.o = order
        
        self.v = value or []

        self.db = db
        db.root ['set'].append (self)
        db.root._p_changed = 1
        return
    
    def kill (self):
        ''' Kill the set from the DB '''
        self.db.root ['set'].remove (self)
        self.db.root._p_changed = 1
        return

    def __iter__ (self):
        return iter (self.v)


    def query (self, word, role = None):
        ''' Return a subset of the current Set, according to the filter. '''

        idx = self.db.root ['index']
        try:
            w = idx [word]

            if role is None:
                res = []
                for v in w.values ():
                    res = res + v
                return Set (self.db, value = res)

            return Set (self.db, value = w [role])
        
        except KeyError:
            return Set (self.db)


class Folder (Set, api.Folder):

    def __init__ (self, db, name, query = None):
        pass
    
    
    def add (self, manifs):
        pass

    def rem (self, manifs):
        pass
    

class Indexed:

    ''' Virtual class of objects whose textual content is fully
    indexed.'''

    def idx_del (self, role, txts):
        idx = self.db.root ['index']

        for txt in txts:
            for w in txt.words ():
                try:
                    idx [w] [role].remove (self)
                except KeyError, ValueError:
                    pass
        
        self.db.root._p_changed = 1
        return

    def idx_add (self, role, txts):
        idx = self.db.root ['index']

        for txt in txts:
            for w in txt.words ():
                if not idx.has_key (w):
                    idx [w] = {}
                if not idx [w].has_key (role):
                    idx [w][role] = []

                if not self in idx [w][role]:
                    idx [w][role].append (self)
        
        self.db.root._p_changed = 1
        return
            
    
            
class Text (api.Text):

    def words (self):
        return string.split (self.v)


class Name (api.Name):

    def words (self):
        return string.split (self.v)
    

class Manifestation (Persistent, Indexed, api.Manifestation):

    '''  Holder for bibliographic information '''

    def __init__ (self, db):
        ''' Create a new manifestation '''

        db.root ['manif'].append (self)
        db.root._p_changed = 1

        self.db = db
        self.info = {}
        return
    

    def kill (self):
        ''' Kill the manif from the database '''
        db.root ['manif'].remove (self)
        db.root._p_changed = 1
        return


    def get (self):
        ''' Retrieve all the info about a manifestation '''
        return self.info


    def set (self, info):
        ''' Set all the info on a manifestation '''
        for k, v in info.items ():
            if not v:
                try:
                    self.idx_del (k, self.info [k])
                    del self.info [k]
                except KeyError:
                    pass
            else:
                if type (v) is not type ([]): v = [v]
                self.info [k] = v
                self.idx_add (k, v)
                
        self._p_changed = 1
        return
    





