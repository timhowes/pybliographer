TEX =						\
	pyblio.sty				\
	manager.tex 				\
	processing.tex 				\
	td-afe.tex 				\
	td-atd.tex 				\
	td-c01.tex 				\
	td-cnf.tex 				\
	td-cnx.tex 				\
	td-dbm.tex 				\
	td-gui.tex 				\
	td-lst.tex 				\
	td-prc.tex 				\
	td-td1.tex 				\
	td-tec.tex 				\
	td-use.tex

REMOTE = frederic@canvas.gnome.org:/home/frederic/html

MAIN = td-td1

all: todo.pdf

todo.pdf: $(TEX)
	pdflatex $(MAIN)
	pdflatex $(MAIN)
	cp $(MAIN).pdf todo.pdf

remote: all
	rsync *.txt *.pdf *.py $(REMOTE)/design


glossary: tx-gloss-en.html

tx-gloss-en.html: data/gloen_*.xml txglosshtml.xsl
	xsltproc -o $@  txglosshtml.xsl txgloss.xml
	lynx --dump $@ > tx-gloss-en.txt

data/cl_%.html: data/cl_%.xml txclhtml
	xsltproc -o $@ txclhtml.xsl $<

tx-class.html: data/cl_*.xml txclhtm.xsl
	sh txmlcl.sh
	xsltproc -o $@ txclhtm.xsl txclass.xml


data/uc%.html: data/uc%.xml txusehtml.xsl
	xsltproc -o $@ txusehtml.xsl $<

tx-use.html: data/uc*.xml txusehtm.xsl
	sh txmluc.sh
	xsltproc -o $@ txusehtm.xsl txuses.xml


