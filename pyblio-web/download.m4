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
Recode</a></b> version <b>3.5 exactly</b> (not 3.6, not any of the
development versions called 3.5d,...) For your convenience, an
untested RPM version is available <a href="recode-3.5-1.i386.rpm">here</a>, thanks to The
Matt.

</ul>

<p>For the Gnome interface, you will have to add:

<ul>
<li><b><a href="http://www.gnome.org">Gnome Environment</a></b>
version <b>1.0.50</b> or better.

<li><b><a
href="http://www.daa.com.au/~james/pygtk">Gnome-Python</a></b> version
<b>1.0.53</b> at least.

</ul>


<h2>Download pybliographer, version pyblio_last</h2>

<p>The latest release (<b>pyblio_last</b>) is available more or less
 simultaneously in the following formats and for the following systems:

m4_define(rpm_bin, 1)
m4_define(rpm_src, 1)

<hr>
<dl>
  <dt><i>Debian</i><dd> from any <a href="http://packages.debian.org/unstable/text/pybliographer.html">Debian</a> mirror.</dd>

  <dt><i>FreeBSD</i><dd>from any <a href="http://www.freebsd.org/cgi/cvsweb.cgi/ports/misc/pybliographer/">FreeBSD</a> mirror.

  <dt><i>RPM</i><dd>

    <ul>

      <li>from <a
      href="http://sourceforge.net/project/showfiles.php?group_id=4825">SourceForge</a>,
      as source and binary RPMs.

      <li>from any <a
      href="ftp://ftp.gnome.org/pub/GNOME/MIRRORS.html">Gnome
      mirror</a>, in the <b>stable/sources/pyblio</b> directory, as a <a href="pyblio_stable/pybliographer-pyblio_last-rpm_src.src.rpm">source RPM</a>
   </ul>
  </dd>

  <dt><i>Source</i><dd>
  
  <ul>

    <li>from <a href="http://sourceforge.net/project/showfiles.php?group_id=4825">SourceForge</a>

    <li>from any <a href="ftp://ftp.gnome.org/pub/GNOME/MIRRORS.html">Gnome mirror</a>, as a

<a href="pyblio_stable/pybliographer-pyblio_last.tar.gz">tar/gz</a> 
or a

<a href="pyblio_stable/pybliographer-pyblio_last.tar.bz2">tar/bz2</a> 

archive
  </ul>
  </dd>
</dl>

<hr>

<p>The RPM source files are kindly provided by Konrad Hinsen. Binary RPMs
are built by Zoltan Kota and Matt Thompson.

<p>Pybliographer is available on <a
href="http://www.debian.org">Debian</a>, thanks to Paul Seelig, Tobias
Bachmor and Pedro Guerreiro.

<p> Johann Visagie is the author of the <a href="http://www.freebsd.org">FreeBSD</a> port.

<p>Historical  versions   of  pybliographer  are   available  from  <a
href="pyblio_unstable">here</a>. Don't use them, really.</p>

]])

html_footer
