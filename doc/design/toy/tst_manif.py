from z import *

db = Database ('test/db')

r = db.roles ()

m = Manifestation (db)

m.set ({r ['titre']: Text ('Aldebaran - La catastrophe'),
        r ['scenariste']: Name ('Leo')})

print m.get ()

m = Manifestation (db)

m.set ({r ['titre']: Text ('La Source et la Sonde'),
        r ['scenariste']: [Name ('<sn>Bourgeon</sn>'), Name ('Lacroix')]})

print m.get ()

