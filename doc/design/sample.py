from db import *

db = Database ('test', 1)

author_r = Role ('base:author', 'An Author', None).register (db)
title_r  = Role ('base:title', 'Title', None).register (db)

work  = Work ().register (db)
title = Text (text = u'Un titre accentué')

title.register (db)

work.attr_ins (title, title_r, 1)
