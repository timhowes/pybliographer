import gettext, string

_ = gettext.gettext

from Pyblio import Config, Fields

Config.define ('bibtex+',
               _("Advanced BibTeX"),
               _("Advanced BibTeX configuration"))

def _get_text_ent ():
    return map (lambda x: x.name,
                filter (lambda x: x.type is Fields.Text,
                        Config.get ('base/fields').data.values ()))

Config.define ('bibtex+/braces',
               _("Use Braces"),
               _(""" A boolean specifying if pybliographic should use
               braces (instead of quotes) to limit entries """),
               Config.Boolean ())

Config.define ('bibtex+/capitalize',
               _("Capitalize"),
               _(""" A flag indicating if pybliographer should handle
               automatic capitalization in the bibtex output """),
               Config.Dict (Config.Element (_get_text_ent),
                            Config.Boolean ()))

Config.define ('bibtex+/override',
               _("Override Macros"),
               _(""" A boolean indicating if the macro definitions
               provided here should override the ones given in a file
               """),
               Config.Boolean ())


Config.set ('bibtex+/braces', 1)

Config.set ('bibtex+/capitalize', {
    'title'     : 1,
    'booktitle' : 1,
    })
               
Config.set ('bibtex+/override', 0)
