import sys, string, re
base_version = string.split (sys.version) [0]
base_version = re.match ('[\d\.]+', base_version).group (0)

version = map (int, string.split (base_version, '.'))
if len (version) < 3: version.append (0)
fd = open ('conftest.out', 'w')
fd.write ('Python_Version=%s\n' % base_version)
fd.write ('Python_Major_Version=%d\n' % version [0])
fd.write ('Python_Minor_Version=%d\n' % version [1])
fd.write ('Python_Micro_Version=%d\n' % version [2])
fd.write ('Python_Prefix="%s"\n' % sys.exec_prefix)
fd.close ()

testversion = map (int, string.split (sys.argv [1], '.'))
if len (testversion) < 3: testversion.append (0)

for pair in map (None, version, testversion):
	if pair [0] > pair [1]: sys.exit (0)
	if pair [0] < pair [1]: sys.exit (1)
