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

DISTCHECK_CONFIGURE_FLAGS = --disable-update-desktop-database

pybdir  = $(datadir)/$(PACKAGE)
appdir  = $(datadir)/applications

SUBDIRS = 	Pyblio 		\
		scripts		\
		tests		\
		Styles		\
		po		\
		help


appicondir = $(datadir)/pixmaps
appicon_DATA = pybliographic.png 

pixmapsdir = $(datadir)/pixmaps
pixmaps_DATA = pybliographic-logo.png pybliographic-viewer.png


Mimedir = $(datadir)/mime-info
Mime_DATA = pybliographic.keys pybliographic.mime

app_DATA = pybliographic.desktop

bin_SCRIPTS = pybliographer

pyb_DATA = pybrc.py

desktopdir = $(datadir)/applications
desktop_in_files = pybliographic.desktop.in
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)

@INTLTOOL_DESKTOP_RULE@

INTLTOOL = 			\
	intltool-extract.in 	\
	intltool-merge.in 	\
	intltool-update.in

EXTRA_DIST = \
	 	pybliographer.in 		\
		pybliographic.keys.in		\
		pybliographic.mime		\
		pybliographic.png		\
		pybliographic-logo.png		\
		pybliographic-viewer.png	\
		gnome-doc-utils.make \
		$(desktop_in_files) $(INTLTOOL) $(pyb_DATA)

CLEANFILES = pybliographer $(desktop_DATA)

DISTCLEANFILES = 		\
	intltool-extract 	\
	intltool-merge 		\
	intltool-update		\
	pybliographic.keys

pybliographer: pybliographer.in
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

pybliographer: Makefile

pybliographic.keys: pybliographic.keys.in
	sed -e 's!\@icondir\@!$(appicondir)!g' < $< > $@

pybliographic.keys: Makefile

update_desktop_database = update-desktop-database $(DESTDIR)$(appdir) \
	|| echo "**** Warning: cannot update mime cache (recommended for Gnome >= 2.8)"

install-data-hook: update-desktop-database
uninstall-hook: update-desktop-database
update-desktop-database:
if ENABLE_UPDATE_DESKTOP_DATABASE
	$(update_desktop_database)
endif
