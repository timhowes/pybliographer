gladedir = $(datadir)/$(PACKAGE)/Pyblio/GnomeUI/glade
appicondir = $(datadir)/pixmaps

glade_DATA = 					\
	fields1.glade				\
	pyblio.ui 				\
	search.glade 				\
	sort.glade 				\
	format.ui				\
	medline.glade 				\
	config1.glade				\
	openurl.glade

EXTRA_DIST = $(glade_DATA) pyblio.ui.in

pyblio.ui: pyblio.ui.in Makefile
	sed -e 's^\@icondir\@^$(appicondir)^g' 		\
	< $(srcdir)/pyblio.ui.in > pyblio.ui.tmp 	\
	&& mv pyblio.ui.tmp pyblio.ui
