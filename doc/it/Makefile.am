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

SGML = gui.sgml pyblio.sgml script.sgml
PNG  = edit.png main.png open.png search.png

EXTRA_DIST = \
	topic.dat $(SGML) $(PNG)

pybliographic_helpdir = $(datadir)/gnome/help/pybliographic/it

all: pyblio/book1.html

pyblio/book1.html: $(SGML)
	db2html pyblio.sgml || echo "** can't regenerate documentation"

install-data-local:
	$(mkinstalldirs) $(DESTDIR)$(pybliographic_helpdir)
	$(INSTALL_DATA)  $(srcdir)/topic.dat $(DESTDIR)$(pybliographic_helpdir)
	@echo "installing HTML files"
	@cp -rf $(srcdir)/pyblio/* $(DESTDIR)$(pybliographic_helpdir)
	@echo "installing PNG files"
	@for file in $(srcdir)/*.png ; do \
		$(INSTALL_DATA) $$file $(DESTDIR)$(pybliographic_helpdir) ; \
	done

dist-hook:
	cp -rf $(srcdir)/pyblio $(distdir)

doc-pack:
	mkdir documentation
	cp *.html *.png documentation
	tar zcvf doc-pack.tar.gz documentation
	rm -rf documentation