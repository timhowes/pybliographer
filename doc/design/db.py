import api
import string

from pyPgSQL import PgSQL

def utf (txt):
    if txt is None: return None
    return txt.encode ('utf-8')

def uni (txt):
    if txt is None: return None
    return txt.decode ('utf-8')



class Database (api.Database):

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
             type   TEXT NOT NULL,
             info   TEXT NOT NULL
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

        # This function keeps in sync the Info table with the
        # different subclasses of Type.
        '''
        CREATE FUNCTION update_info ()
        RETURNS opaque AS '
        BEGIN
          IF TG_OP = ''DELETE'' THEN
               DELETE FROM info WHERE id = OLD.id;
               RETURN OLD;
          ELSIF TG_OP = ''INSERT'' THEN
               -- check that the role can bind the two sides
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
             data   INT  REFERENCES info (id),
             index  INT  NOT NULL,
             CONSTRAINT index_role UNIQUE (record, role, index)
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

            Role ('record:above', 'Above', 'ew|me|im').register (self)
            Role ('record:below', 'Below', 'we|em|mi').register (self)
        return

    def save (self):
        return

    def commit (self):
        self._db.commit ()
        return

    def roles (self):
        # get all the roles in a single pass
        self._op.execute ("SELECT id, parent, info, type FROM role")

        assoc = {}

        result = self._op.fetchall ()
        
        for role in result:
            r = Role (role [0], role [2], role [3])
            r.db = self

            assoc [role [0]] = r

        for role in result:
            if not role [1]: continue
            
            assoc [role [0]]._parent = assoc [role [1]]

        return assoc

    def query (self, query = None, order = None):

        tables = {}
        args   = []
        
        if query is None:
            tables ['record'] = 1
            where = ''
        else:
            where = query.where (tables, args)

            if len (tables):
                for k in tables.keys ():
                    where += ' AND attribute.data = %s.id' % k
                tables ['attribute'] = 1
                
                where += ' AND attribute.record = record.id'
                
            tables ['record'] = 1
            where = 'WHERE ' + where
            
        f = string.join (tables.keys (), ', ')

        q = "SELECT record.id, record.type FROM %s %s" % (f, where)

        print "Query: %s  %s" % (q, args)
        return ResultSet (self, q, args)



class Role (api.Role):

    def __init__ (self, role, description, type):
        api.Role.__init__ (self, role, description, type)
        self._parent = None
        return
    

    def register (self, db):
        self._db = db

        self._parent = None
        
        db._op.execute ("INSERT INTO role (id, info, type) "
                        "VALUES (%s, %s, %s)",
                        self.id, self.desc, self.type)
        return self
    
    def _set_parent (self, super):
        ''' Set the parent Role, possibly to None '''
        
        self._db._op.execute ("UPDATE role SET parent = %s WHERE id = %s",
                              super.id, self.id)
        return

    def _get_parent (self):
        return self._parent

    parent = property (_get_parent,
                       _set_parent,
                       None,
                       'Parent Role')
    
    
class Record (object):

    def register (self, db):
        db._op.execute ("SELECT nextval ('id')")
        self.id = db._op.fetchone () [0]
        self.db = db
        db._op.execute ("INSERT INTO record (id, type) VALUES (%s, %s)",
                        self.id, self.tag)
        return self

    def attr_ins (self, attr, role, index):
        self.db._op.execute ("INSERT INTO attribute (index, role, "
                             "data, record) VALUES (%s, %s, %s, %s)",
                             index, role.id, attr.id, self.id)
        return
        
    def attr_del (self, role, index):
        self.db._op.execute ("DELETE FROM attribute WHERE "
                             "record = %s AND role = % AND index = %s",
                             self.id, role.id, index)
        return

    def link (self, record, role):
        self.db._op.execute ("INSERT INTO record_link (rec_a, role, "
                             "rec_b) VALUES (%s, %s, %s)",
                             self.id, role.id, record.id)
        return
        
    def unlink (self, record, role):
        self.db._op.execute ("DELETE FROM record_link WHERE "
                             "rec_a = %s AND role = %s AND rec_b = %s",
                             self.id, role.id, record.id)
        return
        
    
    def _fill (self, db, id):
        ''' Initialize a Record that has been retrieved from a query '''
        self.id = id
        self.db = db
        return


    def related (self, role = None):
        ''' Return a ResultSet of all the related records '''
        
        q = ("SELECT l.role, l.rec_b, r.type FROM record_link l, record r "
             "WHERE r.id = l.rec_b AND l.rec_a = %s")
        args = [ self.id ]
        
        if role:
            q += " AND l.role = %s"
            args.append (role)
            
        
        return RelatedResultSet (self.db, q, args)


    def attributes (self):
        ret = []
        
        op = self.db._db.cursor ()

        # fetch all the text attributes
        op.execute ("SELECT a.role, a.index, t.* FROM text_t t, attribute a"
                    " WHERE t.id = a.data AND a.record = %s", self.id)

        for r in op.fetchall ():
            o = Text (uni (r [3]),
                      uni (r [4]))
            
            o._fill (self.db, r [2])
            
            ret.append ((r [0], r [1], o))

        # fetch all the person attributes
        op.execute ("SELECT a.role, a.index, t.* FROM person_t t, attribute a"
                    " WHERE t.id = a.data AND a.record = %s", self.id)

        for r in op.fetchall ():

            o = Person (uni (r [3]),
                        uni (r [4]),
                        uni (r [5]))
            
            o._fill (self.db, r [2])
            
            ret.append ((r [0], r [1], o))

        return ret


class Work (Record, api.Work):
    pass


class Expression (Record, api.Expression):
    pass


class Manifestation (Record, api.Manifestation):
    pass

    
class Item (Record, api.Item):
    pass


class ResultSet (object):

    ''' This result set can handle queries that return records '''
    
    _assoc = {
        Work.tag:          Work,
        Expression.tag:    Expression,
        Manifestation.tag: Manifestation,
        Item.tag:          Item,
        }
    
    def __init__ (self, db, q, args):
        self._db = db
        self._op = db._db.cursor ()

        self._op.execute (q, args)
        return

    def __iter__ (self):
        return self

    def next (self):
        row = self._op.fetchone ()
        if row is None:
            raise StopIteration ()

        r = self._assoc [row [1]] ()
        r._fill (self._db, row [0])
        return r
    
        
class RelatedResultSet (object):

    ''' This result set can handle queries that return records '''
    
    _assoc = {
        Work.tag:          Work,
        Expression.tag:    Expression,
        Manifestation.tag: Manifestation,
        Item.tag:          Item,
        }
    
    def __init__ (self, db, q, args):
        self._db = db
        self._op = db._db.cursor ()

        self._op.execute (q, args)
        return

    def __iter__ (self):
        return self

    def next (self):
        row = self._op.fetchone ()
        if row is None:
            raise StopIteration ()

        r = self._assoc [row [2]] ()
        r._fill (self._db, row [1])
        return (row [0], r)
    
        
class Type (object):

    def _register (self, db):
        db._op.execute ("SELECT nextval ('id')")
        self.id = db._op.fetchone () [0]
        self.db = db
        return

    def _fill (self, db, id):
        self.id = id
        self.db = db
        return


class Boolean (object):

    def __and__ (self, other):
        return QueryAnd (self, other)
    
    def __or__ (self, other):
        return QueryOr (self, other)


class QueryOr (Boolean):

    def __init__ (self, a, b):
        self.a = a
        self.b = b
        return

    def where (self, tables, args):
        return "(%s OR %s)" % (self.a.where (tables, args),
                               self.b.where (tables, args))


class QueryAnd (Boolean):

    def __init__ (self, a, b):
        self.a = a
        self.b = b
        return

    def where (self, tables, args):
        return "(%s AND %s)" % (self.a.where (tables, args),
                                self.b.where (tables, args))


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
        return
    
    def _set_middle (self, val):
        self._cache [1] = val
        if not self.db: return

        self.db._op.execute ("UPDATE person_t SET middle = %s "
                             "WHERE id = %s", val, self.id)
        return

    def _set_last (self, val):
        self._cache [2] = val
        if not self.db: return
        
        self.db._op.execute ("UPDATE person_t SET last = %s "
                             "WHERE id = %s", val, self.id)
        return

    first  = property (_get_first, _set_first, None,
                       'Middle Name of a Person')
    
    middle = property (_get_middle, _set_middle, None,
                       'Middle Name of a Person')
    
    last   = property (_get_last, _set_last, None,
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
        return self

    def _get_text (self): return self._text
    
    def _get_lang (self): return self._lang

    def _set_text (self, val):
        self._text = val
        if not self.db: return

        self.db._op.execute ("UPDATE text_t SET text = %s "
                             "WHERE id = %s", utf (val),
                             self.id)
        return
    
    def _set_lang (self, val):
        self._lang = val
        if not self.db: return

        self.db._op.execute ("UPDATE text_t SET lang = %s "
                             "WHERE id = %s", val, self.id)
        return

    text = property (_get_text, _set_text, None,
                     'Textual content')
    
    lang = property (_get_lang, _set_lang, None,
                     'Language in which the text is written')


    def search (role, text, lang = None):
        return TextQuery (role, text, lang)
    
    search = staticmethod (search)
    

class TextQuery (Boolean, api.Searchable):

    def __init__ (self, role, text, lang):
        api.Searchable.__init__ (self, role)

        self.text = text
        self.lang = lang
        return
    
    def where (self, tables, args):
        q = [ 'attribute.role = %s' ]
        args.append (self.role)
        
        if self.text:
            q.append ("text_t.text ILIKE %s")
            args.append ('%' + utf (self.text) + '%')
            
        if self.lang:
            q.append ("text_t.lang = %s")
            args.append (utf (self.text))
            
        if len (q) > 1:
            tables ['text_t'] = 1
        
        return "(%s)" % string.join (q, ' AND ')
    
