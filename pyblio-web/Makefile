M4   = template.m4 defines.m4 news.m4 
WEB  = /usr/local/www/www.gnome.org/pybliographer

HTML  = index.html download.html screenshots.html documentation.html history.html mailing.html
EXTRA = pyblio.png


all: $(HTML)

*.html: summary.m4

install: all
	test -z "$(HTML) $(EXTRA)" || cp -f $(HTML) $(EXTRA) $(WEB)

clean:
	test -z "$(HTML)" || rm -f $(HTML)

gnome:
	rcp -r *.m4 $(EXTRA) Makefile frederic@www.gnome.org:/home/frederic/html

.SUFFIXES: .html .m4

%.html: %.m4 $(M4)
	m4 $(M4) $< > $@

screenshots.html: sample.html