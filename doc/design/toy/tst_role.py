from z import *

db = Database ('test/db')

Role (db, 'titre', None)

a = Role (db, 'auteur', None)

Role (db, 'dessinateur', None, a)
Role (db, 'scenariste', None, a)

db.commit ()

def rshow (roles):
    k = roles.keys ()
    k.sort ()

    for name in k:
        print "%s: %s" % (name, roles [name])
    return

r = Role (db, 'gronf', None)

rshow (db.roles ())

r.kill ()

r = db.roles ()

rshow (db.roles ())

