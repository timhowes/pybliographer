
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



class Record (object):

    ''' Set of attributes describing a bibliographic object '''

    def __init__ (self):
        self.attribute = {}
        return



class Work (Record):
    
    def __init__ (self):
        Record.__init__ (self)
        
        self.expression = []
        return


class Expression (Record):
    
    def __init__ (self):
        Record.__init__ (self)

        self.work = None
        self.manifestation = []
        return


class Manifestation (Record):
    
    def __init__ (self):
        Record.__init__ (self)

        self.expression = None
        self.item = []
        return


class Item (Record):

    def __init__ (self):
        Record.__init__ (self)
        
        self.manifestation = None
        return
    

class Role (object):

    ''' Detailed information about an attribute role. A role can be a
    specialization of another role. '''
    
    def __init__ (self, role_name, type):
        self.role  = role_name
        self.type  = type
        self.super = None
        self.sub = []
        return


class Attribute (object):

    ''' The base class of all the attributes of a record '''

    def __init__ (self, role_name):
        self.id = None
        self.db = None
        
        self.role = role
        return

    def __cmp__ (self, other):
        pass


class Actor (Attribute):
    ''' A Person or Corporate Entity '''
    pass


class Person (Actor):
    pass


class Corporate (Actor):
    pass


class Text (Attribute):

    ''' A non-constrained text attribute, with formatting and language
    properties. '''
    
    def __init__ (self, role_name, lang = None):
        Attribute.__init__ (self, role_name)
        
        self.lang = lang
        return


class Keyword (Attribute):

    ''' A keyword '''
    pass
