from z import *

db = Database ('test/db')

r = db.roles ()

m = Manifestation (db)

m.set ({r ['titre']: Text (u'Aldebaran - La catastrophe'),
        r ['scenariste']: Name ('Leo')})

m = Manifestation (db)

m.set ({r ['titre']: Text (u'La Source et la Sonde'),
        r ['scenariste']: [Name (u'<sn>Bourgeon</sn>'),
                           Name (u'Lacroix')]})

m = Manifestation (db)

m.set ({r ['titre']: Text (u'Six Saisons sur Ilo'),
        r ['scenariste']: [Name (u'<sn>Bourgeon</sn>'),
                           Name (u'Lacroix')]})

m = Manifestation (db)

m.set ({r ['titre']: Text (u'Dummy')})

print ">> before <<"

for m in db.content ().__iter__ ():
    print m.get ()

m.kill ()

print ">> after <<"

for m in db.content ().__iter__ ():
    print m.get ()

db.commit ()
