TEX = 						\
	appendix.tex 				\
	bibdata.tex 				\
	external.tex 				\
	features.tex 				\
	gui.tex 				\
	intro.tex 				\
	manager.tex 				\
	processing.tex 				\
	scripting.tex 				\
	techne.tex 				\
	todolist.tex 				\
	todo.tex

REMOTE = frederic@canvas.gnome.org:/home/frederic/html

all: todo.pdf

todo.pdf: $(TEX)
	pdflatex todo.tex
	pdflatex todo.tex

remote: all
	rsync *.txt *.pdf $(REMOTE)/design
