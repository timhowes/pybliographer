import gettext
_ = gettext.gettext

from Pyblio import Config

Config.define ('gnome',
               _("Gnome"),
               _("Gnome interface configuration"))

Config.define ('gnome/columns',
               _("Columns"),
               _("Fields displayed on the main screen of the interface"),
               Config.List (Config.String ()))

Config.define ('gnome/tooltips',
               _("Tooltips"),
               _("Enable tooltips ?"),
               Config.Boolean ())

Config.define ('gnome/native-as-default',
               _("Native Edit"),
               _("Edit the entries in their native format by default ?"),
               Config.Boolean (_("Use native edit by default ?")))

Config.define ('gnome/searched',
               _("Searchable"),
               _("Searchable fields"),
               Config.List (Config.String ()))

Config.define ('gnome/history',
               _("History Size"),
               _("Size of the history file"),
               Config.Integer (min = 1, desc = _("Number of items")))

# --------------------------------------------------

Config.set ('gnome/searched', ['Author', 'Title', 'Abstract', 'Date'])

Config.set ('gnome/tooltips', 1)

Config.set ('gnome/native-as-default', 0)

Config.set ('gnome/columns', ('Author', 'Date', 'Title'))

Config.set ('gnome/history', 10)
