
class Database (object):
    
    ''' A complete pybliographer database. Every entry manipulated by
    the system is connected to such a database. '''
    
    def __init__ (self, uri):
        pass

    def save (self):
        pass

    def record_get (self, query = None):
        ''' Returns an iterator to loop over some records of the
        database '''
        pass

    def role_get (self, query = None):
        ''' Returns an iterator to loop over some roles of the
        database '''
        pass
    
    def attribute_get (self, query = None):
        ''' Returns an iterator to loop over some attributes of the
        database '''
        pass


    def __iter__ (self):
        ''' A default iterator that loops over all the entries in
        natural order '''
        return self.record_get ()




class Record (object):

    ''' Set of attributes describing a bibliographic object '''

    def __init__ (self):
        self.attribute = {}

        # these are defined once the object has been registered in the db.
        self.db = None
        self.id = None
        return

    def register (self, db):
        ''' Register the record in the database '''
        return self
    
    def unregister (self):
        ''' Unregister the record from the database '''
        return self


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
    
    def __init__ (self, role_name, type, shared):
        
        ''' A role_name is an intern string with the following syntax:

               <domain>:<role>

        The type is a subclass of Attribute. If shared is 1, then a
        unique attribute can be used in several records for the same role. '''
        
        self.role  = role_name
        self.type  = type
        self.super = None
        self.sub   = []

        # these are defined once the object has been registered in the db.
        self.db = None
        self.id = None
        return

    def register (self, db):
        ''' Register the role in the database '''
        pass

    def unregister (self):
        ''' Unregister the role from the database '''
        pass


class Attribute (object):

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

    def unregister (self):
        ''' Unregister the attribute from the database '''
        return self


class Actor (Attribute):
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


class Text (Attribute):

    ''' A non-constrained text attribute, with formatting and language
    properties. '''
    
    def __init__ (self, lang = None):
        Attribute.__init__ (self)
        
        self.lang = lang
        return


class Date (Attribute):

    YEAR  = 0
    MONTH = 1
    DAY   = 2
    
    def __init__ (self):
        Actor.__init__ (self)

        self.date = [ None, None, None ]
        return


class Concept (Attribute):

    pass


class URI (Attribute):

    pass
