from api import *

db = Database ('file:db.pbl')

work  = Work ().register (db)
title = Text ().register (db)

title.text = u'Au bonheur des ogres'

work.attribute ['core:title'].append (title)

auth = Person ().register (db)

auth.name [Person.LAST]  = u'Pennac'
auth.name [Person.FIRST] = u'Daniel'

work.attribute ['core:author'].append (auth)

db.save ()
