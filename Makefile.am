# This file is part of pybliographer
# 
# Copyright (C) 1998-2000 Frederic GOBRY
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

pybdir  = $(datadir)/$(PACKAGE)
appdir  = $(datadir)/gnome/apps/Applications

SUBDIRS = 	Pyblio 		\
		intl		\
		bibtex 		\
		compiled 	\
		intl		\
		po		\
		.		\
		scripts		\
		tests		\
		Styles		\
		doc


appicondir = $(datadir)/pixmaps
appicon_DATA = pybliographic.png 

pixmapsdir = $(datadir)/pixmaps
pixmaps_DATA = pybliographic-logo.png


Mimedir = $(datadir)/mime-info
Mime_DATA = pybliographic.keys pybliographic.mime

app_DATA = pybliographic.desktop

bin_SCRIPTS = pybliographer

EXTRA_DIST = 	config.h.in			\
		pybrc.py 			\
	 	pybliographer.py 		\
		etc/installer.in		\
		compiled/Makefile.pre.in 	\
		compiled/Setup.in 		\
		compiled/recodemodule.c		\
		compiled/bibtexmodule.c		\
		pybliographic.keys.in		\
		pybliographic.mime		\
		pybliographic.desktop		\
		pybliographic.png		\
		pybliographic-logo.png

etc/installer: $(top_srcdir)/etc/installer.in $(top_builddir)/config.status
	cd $(top_builddir) \
		&& CONFIG_FILES=$@ CONFIG_HEADERS= $(SHELL) ./config.status

pybliographer: $(top_srcdir)/pybliographer.py etc/installer
	$(SHELL) etc/installer < $(top_srcdir)/pybliographer.py > pybliographer
	chmod 755 pybliographer

install-data-local:
	mv -f $(DESTDIR)$(pybdir)/pybrc.py $(DESTDIR)$(pybdir)/pybrc.old || true
	$(INSTALL_DATA) $(srcdir)/pybrc.py $(DESTDIR)$(pybdir)
	$(python) -c "import compileall ; compileall.compile_dir ('"$(DESTDIR)$(pybdir)"');"

pybliographic.keys: pybliographic.keys.in Makefile
	sed -e 's^\@icondir\@^$(appicondir)^g' \
	< $(srcdir)/pybliographic.keys.in > pybliographic.keys.tmp \
	&& mv pybliographic.keys.tmp pybliographic.keys 

# Simple target for bzipped distribution
bzdist: dist
	gunzip -c $(distdir).tar.gz | bzip2 > $(distdir).tar.bz2

