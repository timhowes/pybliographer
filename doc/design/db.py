import api

from pyPgSQL import PgSQL

class Database (api.Database):

    tables = (
        '''CREATE SEQUENCE record_id''',
        
        '''CREATE TABLE work (
             id int primary key
           )''',

        '''CREATE TABLE expression (
             id int primary key
           )''',
        
        '''CREATE TABLE manifestation (
             id int primary key
           )''',
        
        '''CREATE TABLE item (
             id int primary key
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

    def _register (self, db):
        db._op.execute ("SELECT nextval ('record_id')")
        self.id = db._op.fetchone () [0]
        self.db = db
        return


class Work (api.Work, Record):

    def register (self, db):
        self._register (db)
        db._op.execute ("INSERT INTO work (id) values (%d)" % self.id)
        return


class Expression (api.Expression, Record):

    def register (self, db):
        self._register (db)
        db._op.execute ("INSERT INTO expression (id) values (%d)" % self.id)
        return

    
class Manifestation (api.Manifestation, Record):

    def register (self, db):
        self._register (db)
        db._op.execute ("INSERT INTO manifestation (id) values (%d)" % self.id)
        return

    
class Item (api.Item, Record):

    def register (self, db):
        self._register (db)
        db._op.execute ("INSERT INTO item (id) values (%d)" % self.id)
        return
    
db = Database ("test", create = 0)

Work ().register (db)

