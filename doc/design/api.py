
class Database (object):
    
    ''' A complete pybliographer database. Every entry manipulated by
    the system is connected to such a database. '''
    
    def __init__ (self, uri):
        pass

    def save (self):
        pass

    def iter (self, filter = None, sort = None,
              count = None, start = None):

        ''' Returns an iterator to loop over some entries of the
        database '''
        pass

    def __iter__ (self):
        ''' A default iterator that loops over all the entries in
        natural order '''
        return self.iter ()


class Work (object):
    pass


class Expression (object):
    def __init__ (self, work):
        pass


class Manifestation (object):
    def __init__ (self, expression):
        pass


class Item (object):

    def __init__ (self, manifestation):
        pass


class Role (object):

    ''' Detailed information about a role '''
    
    def __init__ (self):
        pass


class Type (object):
    ''' The base class of all the data stored in a record '''

    def __init__ (self, role, id = None):
        self.role = role
        self.id   = id
        return

    def __cmp__ (self, other):
        pass

class Actor (Type):
    pass

class Person (Actor):
    pass

class Corporate (Actor):
    pass

