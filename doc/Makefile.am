# This file is part of pybliographer
# 
# Copyright (C) 1998 Frederic GOBRY
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

SUBDIRS = . C it

DOCUMENTED_FILES = \
	Autoload.py	\
	Base.py		\
	Config.py	\
	Connector.py	\
	Core.py		\
	Exceptions.py	\
	Fields.py	\
	Formatter.py	\
	Help.py		\
	Iterator.py	\
	Key.py		\
	LyX.py		\
	Open.py		\
	Search.py	\
	Selection.py	\
	Sort.py		\
	Text.py		\
	TextUI.py	\
	Types.py	\
	Utils.py	\
	recode.py

noinst_DATA = reference.sgml

reference.sgml: reference.xml docbook.xsl
	4xslt reference.xml docbook.xsl > reference.sgml || \
	echo "*** can't regenerate reference" ;

reference.xml: $(DOCUMENTED_FILES:%=../Pyblio/%)
	$(srcdir)/xmldoc --root=../Pyblio $(DOCUMENTED_FILES) > reference.xml

EXTRA_DIST = reference.xml reference.sgml docbook.xsl xmldoc
