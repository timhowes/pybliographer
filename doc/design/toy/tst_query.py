from z import *

db = Database ('test/db')

r = db.roles ()

s = db.content ()

a = s.query (u'lacroix')

print len (a)

for m in a.__iter__ ():
    print m.get ()

print len (s.query (u'lacroix', r ['scenariste']))
print len (s.query (u'lacroix', r ['titre']))

