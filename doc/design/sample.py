from db import *

db = Database ('test', 1)

a_r = Role ('base:author', 'Author', None).register (db)
t_r = Role ('base:title',  'Title',  None).register (db)

l_r = Role ('base:literal-author', 'Author', None).register (db)
l_r.parent = a_r

db.commit ()

work  = Work ().register (db)
title = Text (text = u'Un titre accentué').register (db)

work.attr_ins (title, t_r, 1)

db.commit ()

q = Text.search ('base:title', u'un')

for r in db.query (q):
    print r.attributes ()
    
