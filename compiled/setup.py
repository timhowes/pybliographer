# -*- python -*-

import os
from distutils.core import setup, Extension


bibtex = [
    'accents.c',
    'author.c',
    'biblex.c',
    'bibparse.c',
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
