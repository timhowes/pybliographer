AC_DEFUN(AM_CHECK_PYTHON, [
  
AC_PATH_PROG(Python, python, no)

if test "${Python}" = "no" ; then
  AC_MSG_ERROR([please install python first])
fi

dnl Python version
AC_MSG_CHECKING([python version is at least $1])

changequote(|,|)

cat > conftest.py <<EOF
import sys, string
base_version = string.split (sys.version) [0]
version = map (int, string.split (base_version, '.'))
if len (version) < 3: version.append (0)
fd = open ('conftest.out', 'w')
fd.write ('Python_Version=%s\n' % base_version)
fd.write ('Python_Major_Version=%d\n' % version [0])
fd.write ('Python_Minor_Version=%d\n' % version [1])
fd.write ('Python_Micro_Version=%d\n' % version [2])
fd.write ('Python_Prefix="%s"\n' % sys.exec_prefix)
fd.close ()

testversion = map (int, string.split ("$1", '.'))
if len (testversion) < 3: testversion.append (0)

for pair in map (None, version, testversion):
	if pair [0] > pair [1]: sys.exit (0)
	if pair [0] < pair [1]: sys.exit (1)

EOF

${Python} conftest.py  2>&5 1>&2

result=$?
rm -f conftest.py
if test -f conftest.out ; then
	. conftest.out
	rm -f conftest.out
else
	AC_MSG_RESULT(|no|)
	AC_MSG_ERROR(|unable to run the test program|)
fi

changequote([,])

if test $result = 0 ; then
	AC_MSG_RESULT([yes (${Python_Version})])
else
	AC_MSG_RESULT([no (${Python_Version})])
	AC_MSG_ERROR([please upgrade your python installation to version $1])
fi
])
