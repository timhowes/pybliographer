from Pyblio import Config

Config.define ('gnomeui/default', """ Graphical description of the
default field. """)

Config.define ('gnomeui/columns', """ A list of the fields displayed
on the main screen of the interface """)

Config.define ('gnomeui/tooltips', """ A boolean indicating if
tooltips are enabled """)

Config.define ('gnomeui/monospaced', """ A monospaced font, for native edition """)

Config.define ('gnomeui/native-as-default', """ Should we edit the
entries in their native format by default ? """)

Config.define ('gnomeui/searched', """ List of searchable fields """)

# --------------------------------------------------
from Pyblio.GnomeUI import Utils, Editor
import gtk

Config.set ('gnomeui/searched', ['Author', 'Title', 'Abstract', 'Date'])

Config.set ('gnomeui/monospaced',
            gtk.load_font ('-*-*-*-r-normal-*-*-*-*-*-c-*-iso8859-1'))

Config.set ('gnomeui/tooltips', 1)
Config.set ('gnomeui/native-as-default', 0)

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

Config.set ('gnomeui/columns', ('Author', 'Date', 'Title'))

