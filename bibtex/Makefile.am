# This file is part of pybliographer
# 
# Copyright (C) 1998-2003 Frederic GOBRY
# Email : gobry@idiap.ch
# 	   
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2 
# of the License, or (at your option) any later version.
#   
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# 
# $Id$


pybdir = $(libdir)/$(PACKAGE)

PARSER_PREFIX  = bibtex_parser_

LEX_OUTPUT_ROOT= lex.$(PARSER_PREFIX)
LEX            = @LEX@ -P$(PARSER_PREFIX)
YACC           = @YACC@ -d -t -p $(PARSER_PREFIX)

lib_LTLIBRARIES = libbibtex.la 

AM_CFLAGS = -DG_LOG_DOMAIN=\"BibTeX\"

INCLUDES = $(GLIB_CFLAGS) $(RECODEINC)

libbibtex_la_SOURCES = 	bibparse.y	\
			biblex.l	\
			stringutils.c	\
			bibtex.c	\
			accents.c	\
			struct.c	\
			entry.c		\
			author.c	\
			reverse.c	\
			source.c	\
			field.c

include_HEADERS = bibtex.h

EXTRA_DIST = 	bibparse.h 	\
		bibtex.h	\
		debugging.h 	\
		logging.h 	

libbibtex_la_LDFLAGS = -version-info 1:0:0 
libbibtex_la_LIBADD  = $(GLIB_LIBS) $(RECODELIB)

noinst_PROGRAMS    = testparser 
testparser_SOURCES = testparser.c
testparser_LDADD   = libbibtex.la
testparser_LDFLAGS = -static 

