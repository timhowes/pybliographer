# -*- python -*-

import os, stat

from distutils.core import setup, Extension


bibtex = [
    'accents.c',
    'author.c',
    'bibparse.c',
    'biblex.c',
    'bibtex.c',
    'bibtexmodule.c',
    'entry.c',
    'field.c',
    'reverse.c',
    'source.c',
    'stringutils.c',
    'struct.c'
    ]


# Obtain path for Glib

includes = []
include = os.popen ('pkg-config glib-2.0 --cflags').read ()

for inc in include.split (' '):
    inc = inc.strip ()
    if not inc: continue

    if inc [:2] == '-I':
        includes.append (inc [2:])

libs    = []
libdirs = []
library = os.popen ('pkg-config glib-2.0 --libs').read ()

for lib in library.split (' '):
    lib = lib.strip ()
    if not lib: continue

    if lib [:2] == '-l':
        libs.append (lib [2:])

    if lib [:2] == '-L':
        libdirs.append (lib [2:])


# Check the state of the generated lex and yacc files

def rebuild (src, deps):

    st = os.stat (src) [stat.ST_MTIME]

    for dep in deps:
        try:
            dt = os.stat (dep) [stat.ST_MTIME]
        except OSError:
            return True

        if st > dt: return True

    return False


def rename (src, dst):

    try: os.unlink (dst)
    except OSError: pass

    os.rename (src, dst)
    return


if rebuild ('bibparse.y', ['bibparse.c',
                           'bibparse.h']):
    print "rebuilding from bibparse.y"

    os.system ('bison -y -d -t -p bibtex_parser_ bibparse.y')

    rename ('y.tab.c', 'bibparse.c')
    rename ('y.tab.h', 'bibparse.h')


if rebuild ('biblex.l', ['biblex.c']):
    print "rebuilding from biblex.l"

    os.system ('flex -Pbibtex_parser_ biblex.l')

    rename ('lex.bibtex_parser_.c', 'biblex.c')

    

# Actual compilation

setup (name = "bibtex", version = "1.0",

       ext_modules = [

    Extension("_bibtexmodule", bibtex,
              include_dirs = includes,
              library_dirs = libdirs,
              libraries = libs),

    Extension("_recodemodule", ["recodemodule.c"],
              include_dirs = includes,
              libraries = ['recode'])
    ])
