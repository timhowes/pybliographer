#!/bin/sh

cat<<EOF
<ul>
EOF

for file in *.pdf *.txt ; do
  echo "<li> <a href=\"design/$file\">$file</a>"
done

cat<<EOF
</ul>

EOF
