m4_dnl -*- html -*-

html_header(Pybliographer - Development)

html_summary(devel, summary.m4, [[

<h1>Development</h1>

<p>The 1.1.x series of pybliographer will start soon. The following
ideas will probably find a place in it (depending if enough people are
interested to contribute):

<ul>
<li> <b>XSL support</b>.  This should enable the creation of real
bibliographic styles, comparable to the bibtex bst mechanism. It will
also ease the conversion to some other formats, like <a
href="http://www.docbook.org">DocBook</a>.

<li> <b>Bibliography generation</b>.  Once the previous point is
achieved, it will be possible to generate bibliographies by parsing
documents written with certain word processors (like <a
href="http://www.abisource.com">AbiWord</a>), in a similar way as
Reference Manager, (thanks to Paul U Cameron for this suggestion).

<li> <b>Web queries</b>. Some scientific search engines provide a way
to get the result of a query in a known bibliographic format, which
could be directly fed into pybliographer.

<li> <b>Database interaction</b>. On the same model, being able to
store large bibliographies on a SQL server would improve
pybliographer's performances a lot.  The use of <a
href="http://www.gnome.org/gnome-db">gnome-db</a> as an intermediate
software layer could provide database-vendor independancy.
</ul>

<p>Of course, people interested in  any of these topics are invited to
join the <a href="mailing.html">mailing-list</a>  and see how they can
contribute&nbsp;!  

]])

html_footer
