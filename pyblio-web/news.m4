m4_dnl -*- html -*-
m4_dnl
m4_dnl --------------------------------------------------
m4_define(pyblio_last,  [[1.0.3]])m4_dnl
m4_dnl --------------------------------------------------
m4_dnl
m4_define(pyblio_news, [[

[[<b>13/06/2000</b>: let's go for 1.0.3! Now, it's possible to read
bibtex files written on Windows, adding a new field in an entry
doesn't cancel previous modifications on that entry, and some bugs
have been fixed in the formatting styles.]],

[[  <b>30/05/2000</b>:  bugfix  release  1.0.1  is  out.  It  corrects
problems with  empty bibtex databases and fixes  the broken pybconvert
script. The German and Italian translations are also updated]],

[[ <b>18/05/2000</b>: I  plan to setup a FAQ  on pybliographer. If you
think that  a particular question should  go in it, let  me know! I've
also  added a  <a  href="development.html">Development</a> section  on
this site.]],

[[ <b>12/05/2000</b>: pybliographer 1.0.0 is out ! A few fixes in this
version (concerning the save order for entries with crossreferences).
Now, let's start on the new developement tree ;-)]],

[[ <b>11/05/2000</b>: back from holidays... The very last fixes are
being made to pybliographer before 1.0.0]],

[[ <b>20/04/2000</b>: I've created  a mailing-list at SourceForge, for
general  discussions   about  pybliographer.  You   can  subscribe  <a
href="http://lists.sourceforge.net/mailman/listinfo/pybliographer-general">here</a>.
]],

[[  <b>19/04/2000</b>: there  are now  <em>two</em>  unofficial debian
packages for pybliographer! One has  been provided by Paul Seelig, and
is                  available                  from                 <a
href="ftp://ntama.uni-mainz.de/pub/debian/unofficial/woody">here</a>,
and      another      by      Tobias     Bachmor,      located      <a
href="http://zemm.ira.uka.de/~bachmor/debian">here</a>. Thanks!]],

[[  <b>18/04/2000</b>: we  are now  at 0.9.11,  aka  1.0pre2. Improved
bibtex  author formatting  and  fixed compilation  problems with  i18n
support. I'll be on vacation two weeks, and plan to release 1.0 when I
come back,  depending on  the number  of bug reports  I'll find  in my
mailbox ;-)]],

[[  <b>17/04/2000</b>:  0.9.10 is  out.  Consider  this  version as  a
1.0pre1,  so please  report any  problem you  encounter with  it. I've
added bibtex customizations, and made  some minor bug fixes. It should
be  now  possible to  use  pybliographer  on endnote-generated  bibtex
files.]],

[[ <b>14/04/2000</b>: Zoltán Kóta provided a hungarian translation,
which will be available in pybliographer 0.9.10. Don't stop the
translation effort! ]],

[[ <b>13/04/2000</b>: RPMs of pybliographer 0.9.9 are waiting for
you at the download section.]],

[[ <b>7/4/2000</b>: gnome-python 1.0.53 is out, so is pybliographer
0.9.9. This version is only a minor bug-fixes release.]],

[[  <b>7/4/2000</b>: Holger Daszler  has written  a german  po file,
which  will  be incorporated  in  the  next  release. If  your  native
language   is  not   Italian,  German   or  French,   please  consider
contributing a translation too !]],

[[ <b>4/4/2000</b>: 0.9.8 is out, and everybody is strongly advised
to upgrade. This version is still based on gnome-python 1.0.52, as
1.0.53 won't come out immediately. In this new version, in addition to
many bug fixes, you will find a graphical configuration system,
ascending and descending sorting, and an XML-based style
definition. Please try it and break it!]],

[[ <b>31/03/2000</b>: 0.9.8 is almost ready, but it requires a
not yet released version of gnome-python... If you want to test it,
you have to get the CVS version. It provides graphical configuration
of many things (like the structure of the bibliography), plus an XML
parser for the description of the output styles.]],

[[ <b>23/03/2000</b>: RPM files for 0.9.7.1 are now available (from
Konrad Hinsen). Go get them on the <a href="download.html">download
page</a>.]],

[[ <b>15/03/2000</b>: issued 0.9.7.1 to fix the previous problem
plus an annoying bug in the creation of new entries...]],

[[ <b>15/03/2000</b>:  ooops, for those  having compilation problems
in      the     po/      directory,      juste     type      <tt>touch
Pyblio/Format/docbook.py</tt> in pybliographer-0.9.7, and your problem
should vanish.]],

[[ <b>14/03/2000</b>:  version 0.9.7  is finally out!   As a  lot of
changes  occured, this  version is  probably less  stable  that 0.9.6.
Nevertheless,  it  brings nice  improvements  (like multiple  document
interface, better  date handling, ...)  Documentation  will be updated
soon.              Oh,             watch            the             <a
href="download.html#requirements"><b>requirements</b></a>,  you really
need the latest gnome-python!]],

[[  <b>9/03/2000</b>: the  basic graphical  functionalities  are now
working again (editing and sorting).  It will require the next version
of gnome-python, because of some bugs in the current one.]],

[[ <b>21/02/2000</b>: the core  is ok. Officially supported database
formats   are  now:  BibTeX   (of  course   !),  Refer,   Medline  and
Ovid. EndNote support  is cancelled for the moment,  as it is possible
to  export to  BibTeX  directly  (as I've  been  told). The  supported
formats provide now reading and writing. I'll add docbook again when I
feel like writing  the sgml parser. The interface  is still broken, as
MDI support  has some problems  under python... On another  topic, you
can       have       a      look       at       the      nice       <a
href="translations/it/index.html">italian   translation</a>   of   the
documentation, written by Yuri Bongiorno.]],

[[ <b>9/02/2000</b>: I've started heavy cleanups (motivated by the
early spring weather of Switzerland ;-)) that should lead to a much
nicer code and ease the writing of some features (especially to merge
databases and read broken ones).]],

[[ <b>24/01/2000</b>:  Konrad Hinsen  kindly provided RPM  files for
pybliographer        0.9.6.        Here        is        the        <a
href="pybliobase/pybliographer-0.9.6-1.i386.rpm">.i386.rpm</a> and the
<a   href="pybliobase/pybliographer-0.9.6-1.src.rpm">.src.rpm</a>.  On
the development side,  I expect to find some spare  time very soon, to
provide with  a new version. Primary  goal: fix the  file formats that
are supposed to work...]],

[[  <b>22/11/1999</b>:  version  0.9.6  is  out, with  all  the  new
features I announced previously, plus  a nice <b>speedup of the BibTeX
parser</b>, especially  for entries holding long  abstracts. Thanks to
those who haven't believed me me  when I told them that everything was
fine ;-) In fact, the parser can go 10 times faster for a modification
of 5 lines of code... So, to summarize, this version adds:
<ul>
<li> internationalization (french for the moment, volonteers are welcome !)
<li> Medline support
<li> LyX support
<li> speed improvement
<li> documentation distribution
</ul>
...and I surely forget things...]],

[[  <b>16/11/1999</b>: version  0.9.6 will  soon be  ready.  It will
provide  lots  of nifty  improvements  (direct  citation insertion  in
<b>LyX</b>, internationalization,  ...). There are  also some projects
to create  new front-ends  for the  system: one for  KDE, and  one for
wxWindows.]]

]]
)m4_dnl
m4_dnl
m4_define(latest_news,m4_dnl
<li> $1
<li> $2
<li> $3
<li> $4
<li> $5
<li> $6
<li> $7
<li> $8
<li> $9
<li> $10
)m4_dnl
m4_dnl
m4_define(all_the_news, [[m4_ifelse($#, 0, , $#, 1, [[<li> $1]],
[[<li> $1
all_the_news(m4_shift($@))]])
]])m4_dnl