
class Database (object):
    
    ''' A complete pybliographer database. Every entry manipulated by
    the system is connected to such a database. '''
    
    def __init__ (self, uri, create = 0):
        pass

    def commit (self):
        ''' Commit the set of local changes to the database '''
        pass
    
    def save (self):
        ''' Save the database  '''
        pass

    def query (self, query = None, order = None):
        ''' Perform a query on the database and returns an iterator on
        the results '''
        pass
    
    def roles (self):
        pass


class Searchable (object):

    ''' Base class of an elementary search unit. An instanciated
    subclass of Searchable is returned by the 'search' method of all
    the available types. This instance must be passed as the 'query'
    argument of the Database.query method. '''
    
    def __init__ (self, role):
        self.role = role
        return

    def __and__ (self, other):
        return self
    
    def __or__ (self, other):
        return self
    

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

    def attr_ins (self, attr, role, index):
        ''' Connect an attribute to the Record, for a specific Role,
        at a given index '''
        pass
    
    def attr_del (self, role, index):
        ''' Disconnect an attribute from a Record '''
        pass
    
    def link (self, record, role):
        ''' Link a Record to another Record, for a specific Role '''
        pass
    
    def unlink (self, record, role):
        ''' Unlink a Record from another Record, for a specific Role '''
        pass

    def attributes (self):
        ''' Return a list of all the attributes of a Record '''
        return []
    
    def related (self, role = None):
        ''' Return a ResultSet of all the related records '''
        pass

    
class Work (Record):

    tag = 'w'
    
    def __init__ (self):
        Record.__init__ (self)
        return

    def __repr__ (self):
        return 'Work (id = %d)' % self.id


class Expression (Record):
    
    tag = 'e'

    def __init__ (self):
        Record.__init__ (self)
        return

    def __repr__ (self):
        return 'Expression (id = %d)' % self.id

class Manifestation (Record):
    
    tag = 'm'

    def __init__ (self):
        Record.__init__ (self)
        return

    def __repr__ (self):
        return 'Manifestation (id = %d)' % self.id

class Item (Record):

    tag = 'i'

    def __init__ (self):
        Record.__init__ (self)
        return
    
    def __repr__ (self):
        return 'Item (id = %d)' % self.id


class Role (object):

    ''' Detailed information about an attribute role. A role can be a
    specialization of another role. '''

    __slots__ = ('parent')
    
    def __init__ (self, role, description, type):
        
        ''' A role is an intern string with the following syntax:

               <domain>:<role>

        The type indicates the classes that can be related by that role. '''
        
        self.id   = role
        self.desc = description
        self.type = type

        # these are defined once the object has been registered in the db.
        self.db = None
        return

    def register (self, db):
        ''' Register the role in the database '''
        pass


class Type (object):

    ''' The base class of all the attributes of a record '''

    def __init__ (self):
        # these are defined once the object has been registered in the db.
        self.db = None
        self.id = None
        return

    def register (self, db):
        ''' Register the attribute in the database '''
        return self


    def search (role):
        ''' Return a search object for the current type and the
        specified role '''

        pass

    search = staticmethod (search)


class Person (Type):

    tag = 'p'
    
    __slots__ = ('first', 'middle', 'last')
    
    def __init__ (self, first = None, middle = None, last = None):
        Actor.__init__ (self)

        if first:  self.first  = first
        if middle: self.middle = middle
        if last:   self.last   = last
        return

    def __repr__ (self):
        return 'Person (%s, %s, %s)' % (`self.first`,
                                        `self.middle`,
                                        `self.last`)



class Text (Type):

    tag = 't'
    
    ''' A non-constrained text attribute, with formatting and language
    properties. '''

    __slots__ = ('text', 'lang')
    
    def __init__ (self, text = None, lang = None):
        Type.__init__ (self)
        
        if text: self.text = text
        if lang: self.lang = lang
        return

    def __repr__ (self):
        return 'Text (%s, lang = %s)' % (`self.text`,
                                         `self.lang`)


class Date (Type):

    tag = 'd'

    YEAR  = 0
    MONTH = 1
    DAY   = 2
    
    def __init__ (self):
        Type.__init__ (self)

        self.date = [ None, None, None ]
        return


class Concept (Type):

    tag = 'c'

    def __init__ (self):
        Type.__init__ (self)

        self.name = None
        return

    def parent_set (self, concept):
        ''' Set the parent Concept, possibly to None '''
        pass


class URI (Type):

    tag = 'u'

    def __init__ (self):
        Type.__init__ (self)
        
        self.uri = None
        return

