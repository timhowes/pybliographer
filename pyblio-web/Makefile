M4    = m4 -P
M4INC = template.m4 defines.m4 news.m4 
WEB   = /usr/local/www/www.gnome.org/pybliographer

#WEB   = /home/groups/pybliographer/htdocs

HTML =	index.html 		\
	download.html 		\
	screenshots.html 	\
	documentation.html 	\
	history.html 		\
	mailing.html 		\
	faq.html		\
	development.html

EXTRA = pyblio.png sample.html anybrowser.png


all: $(HTML)

*.html: summary.m4

install: all
	test -z "$(HTML) $(EXTRA)" || cp -f $(HTML) $(EXTRA) $(WEB)

clean:
	test -z "$(HTML)" || rm -f $(HTML)

remote:
	rsync *.m4 $(EXTRA) Makefile frederic@www.gnome.org:/home/frederic/html
	ssh frederic@www.gnome.org 'cd html && make install'

.SUFFIXES: .html .m4

%.html: %.m4 $(M4INC)
	$(M4) $(M4INC) $< > $@

screenshots.html: sample.html
