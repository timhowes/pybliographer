# This file is part of pybliographer
# 
# Copyright (C) 1998-2004 Frederic GOBRY
# Email : gobry@pybliographer.org
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
# 

pybdir  = $(datadir)/$(PACKAGE)

bin_SCRIPTS = 	pybliographic	\
		pybliocheck	\
		pyblioconvert	\
		pybliocompact	\
		pybliotex	\
		pyblioformat	\
		pybliotext

pyb_DATA = 	pybliographic.py	\
		pybliocheck.py 		\
		pyblioconvert.py 	\
		pybliocompact.py 	\
		pybliotex.py		\
		pyblioformat.py		\
		pybliotext.py

noinst_SCRIPTS = pybscript

EXTRA_DIST = 	pybscript.in			\
	 	pybliographic.py 		\
		pybliocheck.py			\
		pyblioconvert.py		\
		pybliotex.py			\
		pyblioformat.py			\
		pybliocompact.py		\
		pybliotext.py

#pybliographic pybcheck pybconvert pybcompact pybtex pybformat pybtext:
$(bin_SCRIPTS):
	$(LN_S) pybscript $@

pybscript: pybscript.in
	sed \
		-e s!\@bin_dir\@!$(bindir)!               \
		-e s!\@libpyb\@!$(libdir)/$(PACKAGE)!     \
		-e s!\@datapyb\@!$(datadir)/$(PACKAGE)!   \
		-e s!\@package\@!$(PACKAGE)!              \
		-e s!\@version\@!$(VERSION)!              \
		-e s!\@locale_dir\@!$(localedir)!         \
		-e s!\@p_datadir\@!$(datadir)/$(PACKAGE)! \
		< $< > $@
	chmod 755 $@

pybscript: Makefile

DISTCLEANFILES = pybscript

CLEANFILES = $(bin_SCRIPTS)
