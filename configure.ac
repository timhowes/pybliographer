dnl -*- m4 -*-
dnl This file is part of pybliographer
dnl
dnl Copyright (C) 1998-2003 Frederic GOBRY
dnl Email : gobry@idiap.ch
dnl          
dnl This program is free software; you can redistribute it and/or
dnl modify it under the terms of the GNU General Public License
dnl as published by the Free Software Foundation; either version 2 
dnl of the License, or (at your option) any later version.
dnl   
dnl This program is distributed in the hope that it will be useful,
dnl but WITHOUT ANY WARRANTY; without even the implied warranty of
dnl MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
dnl GNU General Public License for more details. 
dnl
dnl You should have received a copy of the GNU General Public License
dnl along with this program; if not, write to the Free Software
dnl Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
dnl
dnl $Id$
dnl
dnl Process this file with autoconf to produce a configure script.

AC_PREREQ(2.57)

AC_INIT(pybliographer, 1.1.90)
AM_INIT_AUTOMAKE

AC_CONFIG_SRCDIR(pybliographer.py)

AM_ACLOCAL_INCLUDE(macros)

AM_CHECK_PYTHON(2.2)

dnl NLS is now hand-managed for python.

AC_CONFIG_FILES(	
	Makefile 
	macros/Makefile
	po/Makefile
	etc/installer
	scripts/Makefile
	tests/Makefile
	glade/Makefile
	Pyblio/Makefile
	Pyblio/GnomeUI/Makefile
	Pyblio/Format/Makefile
	Pyblio/Output/Makefile
	Pyblio/ConfDir/Makefile
	Pyblio/Style/Makefile
	doc/Makefile
	doc/C/Makefile
	doc/it/Makefile
	Styles/Makefile
)


AC_OUTPUT

echo "pybliographer is now configured. Type make to build it"
