#!/bin/sh

set -e

test -d test && rm -rf test
mkdir test

PY="tst_role.py tst_manif.py tst_query.py"

for py in ${PY} ; do
    echo "-- $py --"
    python $py
done
