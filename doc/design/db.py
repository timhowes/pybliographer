import api

from pyPgSQL import PgSQL

class Database (api.Database):

    tables = (
        '''CREATE SEQUENCE record_id''',
        
        '''CREATE TABLE record (
             id   int  primary key,
             type char
           )''',

        '''CREATE TABLE role (
             id int primary key
           )''',

        '''CREATE TABLE record_link (
             id int primary key
           )''',

        '''CREATE TABLE type (
             id int primary key
           )''',

        '''CREATE TABLE person_t (
             first  text,
             middle text,
             last   text
           ) INHERITS (type) ''',
        
        '''CREATE TABLE text_t (
             text text,
             lang text
           ) INHERITS (type) ''',

        '''CREATE TABLE attribute (
             index  int,
             role   int REFERENCES role (id),
             data   int REFERENCES type (id),
             record int REFERENCES record (id)
        )''',
        )
    
    def __init__ (self, uri, create = 0):
        self._db = PgSQL.connect (database = uri)
        self._op = self._db.cursor ()

        if create:
            for t in self.tables:
                self._op.execute (t)
            self._db.commit ()
        return

    def save (self):
        self._db.commit ()
        return


class Record (object):

    def register (self, db):
        db._op.execute ("SELECT nextval ('record_id')")
        self.id = db._op.fetchone () [0]
        self.db = db
        db._op.execute ("INSERT INTO record (id, type) values (%s, %s)",
                        self.id, self._type)
        db._db.commit ()
        return


class Work (Record, api.Work):

    _type = 'w'

class Expression (Record, api.Expression):

    _type = 'e'

    
class Manifestation (Record, api.Manifestation):

    _type = 'm'

    
class Item (Record, api.Item):

    _type = 'i'


class Type (object):

    def _register (self, db):
        db._op.execute ("SELECT nextval ('record_id')")
        self.id = db._op.fetchone () [0]
        self.db = db
        return

class Person (Type, api.Person):

    def register (self, db):
        ''' Register the attribute in the database '''
        self._register (db)

        val = [self.id] + self.name 
        db._op.execute ("INSERT INTO person_t (id, last, middle, first) "
                        "values (%s, %s, %s, %s)", val)
        db._db.commit ()
        return self
    
    
db = Database ("test", create = 0)

Work ().register (db)

p = Person ()
p.name [p.FIRST] = 'Fred'
p.register (db)


