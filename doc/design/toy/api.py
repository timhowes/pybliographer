class Database:
    
    ''' A complete pybliographer database. Every entry manipulated by
    the system is connected to such a database. '''
    
    def __init__ (self, uri, create = 0):
        pass
    
    def commit (self):
        ''' Commit the set of local changes to the database '''
        pass
    
    def roles (self):
        ''' Return a dict of available roles '''
        pass

    def save (self):
        ''' Save the database  '''
        pass

    def content (self):
        ''' Return the Set containing all the manifestations. '''
        pass

    def index (self, role):
        ''' Return an Index to browse a given role. '''
        pass

    def complete (self):
        ''' Return a list of values that match a specific part of a
        role. '''
        pass
    


class Role:

    ''' Detailed information about an attribute role. A role can be a
    specialization of another role. A role object can be used as a key
    in a hash table.'''

    def __init__ (self, db, name, type, parent = None):
        pass

    def kill (self):
        ''' Kill the role from the DB '''
        pass

    def get (self):
        """ Get the intl'ed info about the role """
        pass

    def set (self, info):
        """ Set the intl'ed info about the role """
        pass

    def __cmp__ (self, other):
        return cmp (self.name, other.name)
    
    def __hash__ (self):
        return hash (self.name)
    
    def __repr__ (self):
        return 'Role (%s)' % `self.name`
    

class Set:

    ''' Set of Manifestations, resulting from a query or from user
    manipulations'''

    def kill (self):
        ''' Kill the set from the DB '''
        pass

    def __iter__ (self):
        pass

    def query (self, word, role = None):
        ''' Return a subset of the current Set, according to the filter. '''
        pass


class Folder (Set):

    def __init__ (self, db, name, parent = None):
        pass
    
    def add (self, manifs):
        pass

    def rem (self, manifs):
        pass
    

class Text:

    def __init__ (self, v):
        pass

    def words (self):
        pass
    
class Manifestation:

    '''  Holder for bibliographic information '''

    def __init__ (self, db):
        ''' Create a new manifestation '''
        pass

    def kill (self):
        ''' Kill the manif from the database '''
        pass

    def get (self):
        ''' Retrieve all the info about a manifestation '''
        pass

    def set (self, info):
        ''' Update info on a manifestation '''
        pass
    
    def __repr__ (self):
        return 'Manifestation (%s)' % `self.get ()`





