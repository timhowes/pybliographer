from Pyblio import Fields, Autoload
from Pyblio.Style import Utils
import sys

db   = bibopen (sys.argv [2])
keys = db.keys ()

url = Fields.URL (sys.argv [3])

Utils.generate (url, Autoload.get_by_name ('output', sys.argv [4]).data,
                db, keys, sys.stdout)

