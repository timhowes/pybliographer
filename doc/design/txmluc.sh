if [ -x txmuses.xml ]; then
    echo NICHTS ZU TUN ?
else
    echo ODER DOCH ?
fi

cat > txuses.xml <<EOFFF 
<?xml version="1.0" encoding="iso8859-1" ?>

<!-- GENERATED FILE -- DO NOT EDIT -->

<listusecases>


EOFFF


for i in `echo data/uc*.xml |sort -u ` ; do
    if [ "$i" != "data/uc000.xml" ]; then
	
	j=${i#"data/uc"}
	echo ${j%".xml"}
	echo ${j%".xml"} | sed -e 's%.*%  <uc filename="&" />%' >> txuses.xml
    fi


done

cat >> txuses.xml <<EOF

</listusecases>

EOF
