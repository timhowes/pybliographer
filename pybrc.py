# Site configuration

from Pyblio.Types  import *
from Pyblio.Fields import *

from Pyblio import Autoload, Config

from Pyblio.TextUI import *

# ==================================================

import string, os

# define autoloaded formats

Autoload.preregister ('format', 'BibTeX',  'Pyblio.Format.BibTeX',  '.*\.bib')
Autoload.preregister ('format', 'Ovid',    'Pyblio.Format.Ovid',    '.*\.ovid')
Autoload.preregister ('format', 'Medline', 'Pyblio.Format.Medline', '.*\.med')
Autoload.preregister ('format', 'Refer',   'Pyblio.Format.Refer',   '.*\.refer')


# define styles and outputs

Autoload.preregister ('style', 'Alpha',  'Pyblio.Style.alpha')
Autoload.preregister ('style', 'Abbrv',  'Pyblio.Style.alpha')
Autoload.preregister ('style', 'Custom', 'Pyblio.Style.custom')

Autoload.preregister ('output', 'Text',  'Pyblio.Output.text')
Autoload.preregister ('output', 'Raw',   'Pyblio.Output.raw')
Autoload.preregister ('output', 'HTML',  'Pyblio.Output.html')
Autoload.preregister ('output', 'LaTeX', 'Pyblio.Output.LaTeX')


# Parse the configuration directory

rootconfig = os.path.join ('Pyblio', 'ConfDir')

if not os.path.isdir (rootconfig):
    rootconfig = os.path.join (pyb_prefix, 'Pyblio', 'ConfDir')
    
if os.path.isdir (rootconfig):
    Config.parse_directory (rootconfig)


# ==================================================


# ==================================================


    
