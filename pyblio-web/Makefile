M4    = m4 -P
M4INC = template.m4 defines.m4 news.m4 

#WEB   = /usr/local/www/www.gnome.org/pybliographer

WEB   = /home/groups/p/py/pybliographer/htdocs

LOGIN = gobry@ssh.sf.net
HOME  = $(LOGIN):~/html
 
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
	test -z "$(HTML) $(EXTRA)" || cp -rf design $(HTML) $(EXTRA) $(WEB)

clean:
	test -z "$(HTML)" || rm -f $(HTML)

remote:
	rsync *.m4 $(EXTRA) list-documents.sh Makefile $(HOME)
	ssh $(LOGIN) 'cd html && make install'

.SUFFIXES: .html .m4

%.html: %.m4 $(M4INC)
	$(M4) $(M4INC) $< > $@

screenshots.html: sample.html
