import api
import string

from pyPgSQL import PgSQL

def utf (txt):
    if txt is None: return None
    return txt.encode ('utf-8')

class Database (api.Database):

    update_info = string.replace ('''
    ''', "'", "''")

    tables = (
        # This sequence is used to provide unique primary keys
        '''CREATE SEQUENCE id''',

        # A Record table. There is no subclass as there are no
        # specific data for the subclasses.
        '''CREATE TABLE record (
             id   INT  PRIMARY KEY,
             type CHAR CONSTRAINT valid_type
                       CHECK (type in ('w', 'e', 'm', 'i'))
           )''',

        # A Role.
        '''CREATE TABLE role (
             id     TEXT PRIMARY KEY,
             parent TEXT REFERENCES role (id),
             info   TEXT
           )''',

        # This table holds links between Records.
        '''CREATE TABLE record_link (
             rec_a INT  REFERENCES record (id),
             role  TEXT REFERENCES role (id),
             rec_b INT  REFERENCES record (id),

             CONSTRAINT link_once UNIQUE (rec_a, role, rec_b)
           )''',

        # This table is used for the external references, as it is not
        # (yet) possible to use INHERITS to reference the base class
        # of several subclasses in a REFERENCES constraint.
        
        '''CREATE TABLE info (
             id INT PRIMARY KEY
           )''',

        # This is the base class for typed attributes
        '''CREATE TABLE type (
             id INT PRIMARY KEY
           )''',

        '''
        CREATE FUNCTION update_info ()
        RETURNS opaque AS '
        BEGIN
          IF TG_OP = ''DELETE'' THEN
               DELETE FROM info WHERE id = OLD.id;
               RETURN OLD;
          ELSIF TG_OP = ''INSERT'' THEN
               INSERT INTO info (id) VALUES (NEW.id);
               RETURN NEW;
          END IF;

          RETURN NEW;
        END;
        ' LANGUAGE 'plpgsql'
        ''',

        # The base class must not have rows of its own, only the
        # subclasses can.
        '''CREATE RULE no_type AS ON INSERT
                TO type
                DO INSTEAD NOTHING''',

        # A Person
        '''CREATE TABLE person_t (
             first  TEXT,
             middle TEXT,
             last   TEXT
           ) INHERITS (type) ''',
        
        '''CREATE TRIGGER on_person_change BEFORE INSERT OR DELETE
           ON person_t FOR EACH ROW
           EXECUTE PROCEDURE update_info()''',

        # A Text
        '''CREATE TABLE text_t (
             text TEXT, 
             lang TEXT
           ) INHERITS (type) ''',

        '''CREATE TRIGGER on_text_change BEFORE INSERT OR DELETE
           ON text_t FOR EACH ROW
           EXECUTE PROCEDURE update_info()''',


        # This table holds associations between records and typed
        # attributes.
        '''CREATE TABLE attribute (
             record INT  REFERENCES record (id),
             role   TEXT REFERENCES role (id),
             index  INT,
             data   INT,
             CONSTRAINT index_role UNIQUE (index, role)
        )''',

        )
    
    def __init__ (self, uri, create = 0):

        if create:
            # try to create the database (this cannot be done in a
            # transaction)
            db = PgSQL.connect (database = 'template1')
            db.autocommit = 1

            op = db.cursor ()

            # if the create fails, we already have a database. In that
            # case, do not continue, as we might corrupt something
            op.execute ("CREATE DATABASE %s WITH ENCODING = 'unicode'" % uri)

        self._db = PgSQL.connect (database = uri)
        self._op = self._db.cursor ()
        
        self._op.execute ("SET CLIENT_ENCODING TO 'unicode'")
        self._db.commit ()
        
        if create:
            for t in self.tables:
                self._op.execute (t)
            self._db.commit ()
        return

    def save (self):
        return


class Role (api.Role):

    def register (self, db):
        self.db = db

        db._op.execute ("INSERT INTO role (id, info) "
                        "VALUES (%s, %s)",
                        self.id, self.desc)
        db._db.commit ()
        return self
    
    def parent_set (self, super):
        ''' Set the parent Role, possibly to None '''
        
        self.db._op.execute ("UPDATE role SET parent = %s WHERE id = %s",
                             super.id, self.id)
        self.db._db.commit ()
        return

    
class Record (object):

    def register (self, db):
        db._op.execute ("SELECT nextval ('id')")
        self.id = db._op.fetchone () [0]
        self.db = db
        db._op.execute ("INSERT INTO record (id, type) VALUES (%s, %s)",
                        self.id, self._type)
        db._db.commit ()
        return self

    def attr_ins (self, attr, role, index):
        self.db._op.execute ("INSERT INTO attribute (index, role, "
                             "data, record) VALUES (%s, %s, %s, %s)",
                             index, role.id, attr.id, self.id)
        self.db._db.commit ()
        return
        
    def attr_del (self, role, index):
        self.db._op.execute ("DELETE FROM attribute WHERE "
                             "record = %s AND role = % AND index = %s",
                             self.id, role.id, index)
        db._db.commit ()
        return

    def link (self, record, role):
        self.db._op.execute ("INSERT INTO record_link (rec_a, role, "
                             "rec_b) VALUES (%s, %s, %s)",
                             self.id, role.id, record.id)
        db._db.commit ()
        return
        
    def unlink (self, record, role):
        self.db._op.execute ("DELETE FROM record_link WHERE "
                             "rec_a = %s AND role = %s AND rec_b = %s",
                             self.id, role.id, record.id)
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
        db._op.execute ("SELECT nextval ('id')")
        self.id = db._op.fetchone () [0]
        self.db = db
        return


class Person (Type, api.Person):

    def __init__ (self, first = None, middle = None, last = None):
        self._cache = [ None, None, None]

        api.Person.__init__ (self, first, middle, last)
        return
    
    def register (self, db):
        ''' Register the attribute in the database '''
        self._register (db)

        val = [ self.id ] + self._cache
        db._op.execute ("INSERT INTO person_t (id, first, middle, last) "
                        "values (%s, %s, %s, %s)", val)
        db._db.commit ()
        return self

    def _get_first (self):
        return self._cache [0]
    
    def _get_middle (self):
        return self._cache [1]

    def _get_last (self):
        return self._cache [2]

    def _set_first (self, val):
        self._cache [0] = val
        if not self.db: return

        self.db._op.execute ("UPDATE person_t SET first = %s "
                             "WHERE id = %s", utf (val),
                             self.id)
        self.db._db.commit ()
        return
    
    def _set_middle (self, val):
        self._cache [1] = val
        if not self.db: return

        self.db._op.execute ("UPDATE person_t SET middle = %s "
                             "WHERE id = %s", val, self.id)
        self.db._db.commit ()
        return

    def _set_last (self, val):
        self._cache [2] = val
        if not self.db: return
        
        self.db._op.execute ("UPDATE person_t SET last = %s "
                             "WHERE id = %s", val, self.id)
        self.db._db.commit ()
        return

    first = property (_get_first,
                      _set_first,
                      None,
                      'Middle Name of a Person')
    
    middle = property (_get_middle,
                       _set_middle,
                       None,
                       'Middle Name of a Person')
    
    last = property (_get_last,
                     _set_last,
                     None,
                     'Last Name of a Person')
    

class Text (Type, api.Text):

    def __init__ (self, text = None, lang = None):
        self._text = None
        self._lang = None

        api.Text.__init__ (self, text, lang)
        return
    
    def register (self, db):
        ''' Register the attribute in the database '''
        self._register (db)

        db._op.execute ("INSERT INTO text_t (id, text, lang) "
                        "values (%s, %s, %s)",
                        self.id,
                        utf (self._text),
                        utf (self._lang))
        db._db.commit ()
        return self

    def _get_text (self): return self._text
    
    def _get_lang (self): return self._lang

    def _set_text (self, val):
        self._text = val
        if not self.db: return

        self.db._op.execute ("UPDATE text_t SET text = %s "
                             "WHERE id = %s", utf (val),
                             self.id)
        self.db._db.commit ()
        return
    
    def _set_lang (self, val):
        self._lang = val
        if not self.db: return

        self.db._op.execute ("UPDATE text_t SET lang = %s "
                             "WHERE id = %s", val, self.id)
        self.db._db.commit ()
        return

    text = property (_get_text,
                     _set_text,
                     None,
                     'Textual content')
    
    lang = property (_get_lang,
                     _set_lang,
                     None,
                     'Language in which the text is written')
    
    
    
