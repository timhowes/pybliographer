AC_DEFUN([AM_CHECK_PYTHON], [
  
AC_PATH_PROG(Python, python, no)

if test "${Python}" = "no" ; then
  AC_MSG_ERROR([please install python first])
fi

dnl Python version
AC_MSG_CHECKING([python version is at least $1])

${Python} ${srcdir}/setup-check.py $1  2>&5 1>&2

result=$?
rm -f conftest.py
if test -f conftest.out ; then
	. ./conftest.out
	rm -f conftest.out
else
	AC_MSG_RESULT([no])
	AC_MSG_ERROR([unable to run the test program])
fi

if test $result = 0 ; then
	AC_MSG_RESULT([yes (${Python_Version})])
else
	AC_MSG_RESULT([no (${Python_Version})])
	AC_MSG_ERROR([please upgrade your python installation to version $1])
fi
])
