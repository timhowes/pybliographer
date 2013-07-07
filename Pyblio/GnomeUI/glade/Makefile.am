gladedir = $(datadir)/$(PACKAGE)/Pyblio/GnomeUI/glade
appicondir = $(datadir)/pixmaps

glade_DATA = 					\
	fields1.ui				\
	pyblio.ui 				\
	search.glade 				\
	sort.ui 				\
	format.ui				\
	medline.glade 				\
	config1.ui				\
	openurl.glade

EXTRA_DIST = $(glade_DATA) pyblio.ui.in

pyblio.ui: pyblio.ui.in Makefile
	sed -e 's^\@icondir\@^$(appicondir)^g' 		\
	< $(srcdir)/pyblio.ui.in > pyblio.ui.tmp 	\
	&& mv pyblio.ui.tmp pyblio.ui
