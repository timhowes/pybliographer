#!/bin/sh

cat<<EOF
<ul>
<li>A large TODO file, in <a href="design/todo.pdf">PDF</a>
EOF

for file in *.txt ; do
  echo "<li> <a href=\"design/$file\">$file</a>"
done

cat<<EOF
</ul>

EOF
