

cat > txclass.xml <<EOFFF 
<?xml version="1.0" encoding="iso8859-1" ?>

<!-- GENERATED FILE -- DO NOT EDIT -->
<listclasses>


EOFFF


for i in `echo data/cl_*.xml |sort -u ` ; do
    if [ "$i" != "data/cl_000.xml" ]; then
	
	j=${i#"data/cl_"}
	echo ${j%".xml"}
	echo ${j%".xml"} | sed -e 's%.*%  <cl file="&" />%' >> txclass.xml
    fi


done

cat >> txclass.xml <<EOF

</listclasses>

EOF
