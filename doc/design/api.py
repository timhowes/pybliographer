
class Database (object):
    
    ''' A complete pybliographer database. Every entry manipulated by
    the system is connected to such a database. '''
    
    def __init__ (self, uri, create = 0):
        pass

    def save (self):
        ''' Save the database  '''
        pass

    def query (self, query):
        ''' Perform a query on the database  '''
        pass
    


class Record (object):

    ''' Set of attributes describing a bibliographic object '''

    def __init__ (self):
        # these are defined once the object has been registered in the db.
        self.db = None
        self.id = None
        return

    def register (self, db):
        ''' Register the record in the database '''
        return self

    def attr_set (self, attr, role):
        ''' Connect an attribute to the Record, for a specific Role  '''
        pass
    
    def attr_del (self, attr, role):
        ''' Disconnect an attribute from a Record '''
        pass
    
    def link (self, record, role):
        ''' Link a Record to another Record, for a specific Role '''
        pass
    
    def unlink (self, record, role):
        ''' Unlink a Record from another Record, for a specific Role '''
        pass
    

class Work (Record):
    
    def __init__ (self):
        Record.__init__ (self)
        return


class Expression (Record):
    
    def __init__ (self):
        Record.__init__ (self)
        return


class Manifestation (Record):
    
    def __init__ (self):
        Record.__init__ (self)
        return


class Item (Record):

    def __init__ (self):
        Record.__init__ (self)
        return
    

class Role (object):

    ''' Detailed information about an attribute role. A role can be a
    specialization of another role. '''
    
    def __init__ (self, role, description, type):
        
        ''' A role is an intern string with the following syntax:

               <domain>:<role>

        The type indicates the classes that can be related by that role. '''
        
        self.role = role
        self.desc = description
        self.type = type

        # these are defined once the object has been registered in the db.
        self.db = None
        self.id = None
        return

    def register (self, db):
        ''' Register the role in the database '''
        pass

    def parent_set (self, super):
        ''' Set the parent Role, possibly to None '''
        pass

    

class Type (object):

    ''' The base class of all the attributes of a record '''

    def __init__ (self):
        # these are defined once the object has been registered in the db.
        self.db = None
        self.id = None
        return

    def __cmp__ (self, other):
        pass

    def register (self, db):
        ''' Register the attribute in the database '''
        return self


class Actor (Type):
    ''' A Person or Corporate Entity '''
    pass


class Person (Actor):

    LAST   = 0
    MIDDLE = 1
    FIRST  = 2
    
    def __init__ (self):
        Actor.__init__ (self)

        self.name = [ None, None, None ]
        return


class Corporate (Actor):
    def __init__ (self):
        Actor.__init__ (self)

        self.name = None
        return


class Text (Type):

    ''' A non-constrained text attribute, with formatting and language
    properties. '''
    
    def __init__ (self):
        Type.__init__ (self)
        
        self.lang = None
        self.text = None
        return


class Date (Type):

    YEAR  = 0
    MONTH = 1
    DAY   = 2
    
    def __init__ (self):
        Type.__init__ (self)

        self.date = [ None, None, None ]
        return


class Concept (Type):

    def __init__ (self):
        Type.__init__ (self)

        self.name = None
        return

    def parent_set (self, concept):
        ''' Set the parent Concept, possibly to None '''
        pass


class URI (Type):

    def __init__ (self):
        Type.__init__ (self)
        
        self.uri = None
        return

