import sys
from Pyblio import Selection, Sort

how = sys.argv [1]

if how == '': how = None

a = bibopen (sys.argv [2], how)

f = open (sys.argv [3], 'w')

# write out in the key order
sel = Selection.Selection (sort = Sort.Sort ([Sort.KeySort ()]))
it  = sel.iterator (a.iterator ())

bibwrite (it, out = f, how = a.id)
