from db import *

db = Database ('test', 1)

c_r = Role ('base:cites', 'Cites', None).register (db)

a_r = Role ('base:author', 'Author', None).register (db)
t_r = Role ('base:title',  'Title',  None).register (db)

l_r = Role ('base:literal-author', 'Author', None).register (db)
l_r.parent = a_r

db.commit ()

w_1   = Work ().register (db)
title = Text (text = u'Un titre accentué').register (db)

w_1.attr_ins (title, t_r, 1)

w_2  = Work ().register (db)
title = Text (text = u'Un autre titre').register (db)

w_2.attr_ins (title, t_r, 1)

# work 1 cites work 2
w_1.link (w_2, c_r)

db.commit ()

q = (Text.search ('base:title', u'un') |
     Text.search ('base:title', u'deux'))

for r in db.query (q):
    print r.attributes ()
    for l in r.related ():
        print l
    
