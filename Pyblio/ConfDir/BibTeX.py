import gettext
_ = gettext.gettext

from Pyblio import Config

# ==================================================

Config.define ('bibtex',
               _("BibTeX"),
               _("BibTeX parser configuration"))

Config.define ('bibtex/strict',
               _("Strict Parsing"),
               _("""Turn warnings into errors"""),
               Config.Boolean ())

Config.define ('bibtex/macros',
               _("Macros"),
               _("BibTeX @String{} macros"),
               Config.Dict (Config.String (),
                            Config.Tuple ((Config.String (), Config.Boolean ()))))

Config.define ('bibtex/datefield',
               _("Date Fields"),
               _("""Links from `real' date field to the two bibtex
               fields that compose it"""))

Config.define ('bibtex/months',
               _("Month values"),
               _(""" A hash table linking month names to their
               values """))

# ==================================================

Config.set ('bibtex/strict', 0)


Config.set ('bibtex/macros',
            {'jan' : ("January", 0),
             'feb' : ("February", 0),
             'mar' : ("March", 0),
             'apr' : ("April", 0),
             'may' : ("May", 0),
             'jun' : ("June", 0),
             'jul' : ("July", 0),
             'aug' : ("August", 0),
             'sep' : ("September", 0),
             'oct' : ("October", 0),
             'nov' : ("November", 0),
             'dec' : ("December", 0),
             })


Config.set ('bibtex/datefield', {
    'date'  : ('year', 'month'),
    })

Config.set ('bibtex/months', {
    'jan' : 1,
    'feb' : 2,
    'mar' : 3,
    'apr' : 4,
    'may' : 5,
    'jun' : 6,
    'jul' : 7,
    'aug' : 8,
    'sep' : 9,
    'oct' : 10,
    'nov' : 11,
    'dec' : 12,
    })
    
