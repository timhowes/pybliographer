from z import *


db = Database ('test')

r = Role (db, 'auteur', None)
m = Manifestation (db)

m.set ({r: Text ('this is a test')})
m.set ({r: Text ('this is not test')})

c = db.content ()
res = c.query ('this')

for r in res.v:
    print r
    


