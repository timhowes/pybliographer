from Pyblio import Config

Config.define ('bibtex/strict',
               """ A boolean indicating the strictness of the parsing """)

Config.set ('bibtex/strict', 0)

Config.define ('bibtex/macros', """ A dictionnary defining the BibTeX
macros (@String{} macros). Each entry of the dictionnary is a 2-uple :
the first field is the expansion of the macro, the second is a boolean
indicating if this macro definition has to be saved in the .bib files """)

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

Config.define ('bibtex/override', """ A boolean indicating if the
macro definitions provided here should override the ones given in a
file """)

Config.set ('bibtex/override', 0)

