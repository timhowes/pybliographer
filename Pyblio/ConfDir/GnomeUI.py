from Pyblio import Config

Config.define ("gnomeui/fields", """ Graphical description of fields.
It's a hash table, with the entry name (lower case) as key, and a
instance of GnomeUI.FieldsInfo.UIDescription as value. """)

Config.define ("gnomeui/default", """ Graphical description of the
default field. It's an instance of GnomeUI.FieldsInfo.UIDescription """)

Config.define ("gnomeui/columns", """ A list of the fields displayed
on the main screen of the interface """)


Config.define ("gnomeui/tooltips", """ A boolean indicating if
tooltips are enabled """)

Config.define ("gnomeui/threads", """ A boolean indicating if the
good version of threads are available """)


Config.set ("gnomeui/tooltips", 1)
Config.set ("gnomeui/threads",  1)

