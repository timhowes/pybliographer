import gettext
_ = gettext.gettext

from Pyblio import Config, Types
from Pyblio.Format.OvidLike import SimpleField, AuthorField, SourceField


Config.define ('ovid/deftype',
               _("Default type"),
               _("Default type for an Ovid entry"),
               Config.Element (lambda Config = Config:
                               Config.get ('base/entries').data.values ()))

Config.define ('ovid/mapping',
               _("Mapping"),
               _("""A mapping between the Ovid field name and the
               current field and type"""))


Config.set ('ovid/deftype',
            Config.get ('base/entries').data ['article'])

Config.set ('ovid/mapping', {
    'title'    : ('title',    SimpleField),
    'authors'  : ('author',   AuthorField),
    'abstract' : ('abstract', SimpleField),
    'source'   : (('journal', 'volume', 'number', 'pages', 'date'),
                  SourceField),
    })
