from distutils.core import setup, Extension
from distutils.cmd import Command
from distutils.command.config import config as basecfg

class config (basecfg):
    
    def run (self):

        # generate the Pyblio/version.py file
        print dir (self)


includes = ['/usr/include/glib-2.0',
            '/usr/lib/glib-2.0/include',
            'bibtex']

setup (name = "Pybliographer",
       version = "1.1.90",
       description = "Bibliographic management software",
       author = "Pybliographer Team",
       url = "http://pybliographer.org/",

       cmdclass = {'config' : config},
       
       packages = ['Pyblio',
                   'Pyblio.Format',
                   'Pyblio.GnomeUI',
                   'Pyblio.Output',
                   'Pyblio.Style'],

       data_files = [('Pyblio/ConfDir',
                      ['Pyblio/ConfDir/Base.py',
                       'Pyblio/ConfDir/BibTeX.py',
                       'Pyblio/ConfDir/BibTeX+.py',
                       'Pyblio/ConfDir/Gnome.py',
                       'Pyblio/ConfDir/GnomeUI.py',
                       'Pyblio/ConfDir/Medline.py',
                       'Pyblio/ConfDir/Ovid.py',
                       'Pyblio/ConfDir/Refer.py']),
                     ('Styles',
                      ['Styles/Abbrev.xml',
                       'Styles/Alpha.xml',
                       'Styles/apa4e.xml',
                       'Styles/bibstyle.dtd'])],
       
       ext_modules = [
    Extension("_bibtexmodule", ["compiled/bibtexmodule.c"],
              include_dirs = includes,
              library_dirs = ['bibtex/.libs'],
              libraries = ['glib-2.0', 'bibtex']),
    
    Extension("_recodemodule", ["compiled/recodemodule.c"],
              include_dirs = includes,
              libraries = ['recode'])
    ]
       )
