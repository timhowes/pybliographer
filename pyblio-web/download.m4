m4_dnl -*- html -*-

html_header(Pybliographer - Downloads)

html_summary(download, summary.m4, [[

<h1>Download</h1>

<a name="requirements"> 
<h2> Requirements </h2>

Please, check that your system meets the following requirements.

<p>For the text-only version, you need:

<ul>
<li><b><a href="http://www.python.org">python</a></b> version <b>1.5.2</b>.

<li><b><a href="http://www.gtk.org">Glib</a></b> version <b>1.2.x</b>

<li><b><a href="http://www.iro.umontreal.ca/contrib/recode">GNU
Recode</a></b> version <b>3.5</b>

</ul>

<p>For the Gnome interface, you will have to add:

<ul>
<li><b><a href="http://www.gnome.org">Gnome Environment</a></b>
version <b>1.0.50</b> or better.

<li><b><a
href="http://www.gnome.org/applist/view.phtml?name=gnome-python">Gnome-Python</a></b>
version <b>1.0.53</b> at least.

</ul>


<h2>Download pybliographer, version pyblio_last</h2>

Here is a list of <a href="http://www.gnome.org/ftpmirrors.shtml">FTP
mirrors</a> where you can find pybliographer.

<p>The latest release (<b>pyblio_last</b>) is available in the following
formats:

<ul>
m4_ifelse(html_testfile(local_stable/sources/pybliographer-pyblio_last.tar.gz), 0,
<li><a href="pyblio_stable/sources/pybliographer-pyblio_last.tar.gz">gzipped</a> 
(.tar.gz, html_filesize(local_stable/sources/pybliographer-pyblio_last.tar.gz))
)

m4_ifelse(html_testfile(local_stable/sources/pybliographer-pyblio_last.tar.bz2), 0,
<li><a href="pyblio_stable/sources/pybliographer-pyblio_last.tar.bz2">bzipped</a> 
(.tar.bz2, html_filesize(local_stable/sources/pybliographer-pyblio_last.tar.bz2))
)

m4_ifelse(html_testfile(local_stable/rpm/pybliographer-pyblio_last-1.i386.rpm), 0,
<li><a href="pyblio_stable/rpm/pybliographer-pyblio_last-1.i386.rpm">RPM</a>
(.i386.rpm, html_filesize(local_stable/rpm/pybliographer-pyblio_last-1.i386.rpm))
)

m4_ifelse(html_testfile(local_stable/rpm/pybliographer-pyblio_last-1.src.rpm), 0,
<li>or <a href="pyblio_stable/rpm/pybliographer-pyblio_last-1.src.rpm">source RPM</a>
(.src.rpm, html_filesize(local_stable/rpm/pybliographer-pyblio_last-1.src.rpm))
)
</ul>

The official site for latest RPM files is <a
href="ftp://dirac.cnrs-orleans.fr/pub/pybliographer/">here</a>.  These
RPM files are kindly provided by <a
href="mailto:hinsen@cnrs-orleans.fr">Konrad Hinsen</a>.

<p>Historical  versions   of  pybliographer  are   available  from  <a
href="pyblio_unstable">here</a>. Don't use them, really.

]])

html_footer
