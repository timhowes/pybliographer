#!/bin/sh

run () 
{
	eval $*
	if test $? != 0 ; then	
		echo "error: while processing $*"
		exit 1
	fi
}

tst_start ()
{
    run ln -fs ${srcdir}/../Styles/Alpha.xml ${srcdir}/../Pyblio ${srcdir}/../pybrc.py ../compiled .
}

tst_stop ()
{
    run rm -f Pyblio pybrc.py compiled Alpha.xml
}

