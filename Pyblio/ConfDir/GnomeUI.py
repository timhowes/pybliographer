import gtk

from Pyblio import Config
from Pyblio.GnomeUI import Utils, Editor

Config.define ('gnomeui/default', """ Graphical description of the
default field. """)

Config.define ('gnomeui/monospaced', """ A monospaced font, for native edition """)

# --------------------------------------------------

Config.set ('gnomeui/monospaced',
            gtk.load_font ('-*-*-*-r-normal-*-*-*-*-*-c-*-iso8859-1'))

h = Config.get ('base/fields').data

h ['author'].width     = 150
h ['author'].widget    = Editor.AuthorGroup

h ['editor'].width     = 150
h ['editor'].widget    = Editor.AuthorGroup

h ['title'].width      = 200
h ['title'].widget     = Editor.Entry

h ['booktitle'].width  = 200
h ['booktitle'].widget = Editor.Entry

h ['date'].width    = 50
h ['date'].widget   = Editor.Date

h ['abstract'].widget  = Editor.Text
h ['crossref'].widget  = Editor.Reference

Config.set ('gnomeui/default',  (150, Editor.Entry))

