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
