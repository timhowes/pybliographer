m4_dnl -*- html -*-
m4_dnl
m4_dnl --------------------------------------------------
m4_define(pyblio_last,  [[1.0.8]])m4_dnl
m4_dnl --------------------------------------------------
m4_dnl
m4_define(news_item,[[[[<dt><i>$1</i><dd>$2]]]])m4_dnl
m4_dnl
m4_define(pyblio_news, [[

news_item([[24/01/2001]], [[Johann Visagie has ported pybliographer to the
FreeBSD ports tree. Thanks a lot for making installation seamless for
FreeBSD people.]]),

news_item([[22/01/2001]], [[I've released pybliographer 1.0.8, which
finally fixes the search button problem. In this release you'll find a
few new translations and an updated version of the italian
documentation.]]),

news_item([[7/12/2000]],  [[pybliographer is now officially available
for Debian (Woody)&nbsp;! Please check your favorite mirror...]]),

news_item([[6/12/2000]],  [[Sourceforge is also up to date now.]]),

news_item([[5/12/2000]],  [[As there are problems to upload files to
SourceForge, the RPM files for pybliographer 1.0.7 are only available on the
Gnome mirrors...]]),

news_item([[30/11/2000]],  [[There  are   now  twelve  (12)  languages
supported by  pybliographer. The latest ones  are japanese, portuguese
(Brasil) and swedish.]]),

news_item([[21/11/2000]], [[Version  1.0.7 is out.  I added a  test so
that a  file won't be overwritten  if it has been  modified outside of
pybliographic.  In addition,  Dominique Burget  helped to  improve the
Ovid  parser. Finally,  the remaining  problems for  bibtex conversion
should be now fixed.]]),

news_item([[17/10/2000]],  [[We are  at 1.0.6.  A few  bug  fixes (for
Refer to BibTeX  conversion), the ability to compile  with Python 2.0,
and a new feature: user defined key generators. It will be possible to
generate emacs-like  keys for your new entries  (for more explanation,
have a look at the mailing-list...)]]),

news_item([[01/10/2000]],[[1.0.5 is  out. Now, the  searched words are
saved between sessions, it is possible  to display the key and type of
the   entries  in   the  index   window  (as   explained  in   the  <a
href="faq.html">FAQ</a>),  and formatted entries  follow the  order of
the  display when  no  specific  ordering is  specified.  And for  the
Italian  speaking people, a  brand new  version of  the documentation,
written by Yuri Bongiorno. ]]),

news_item([[31/08/2000]], [[Two new translations, in Danish by Kenneth
Christiansen and  in Ukrainian  by Yuri Syrota.  Well, I guess  I must
implement unicode support now ;^)]]),

news_item([[22/08/2000]], [[Kjartan Maraas  has worked out a norwegian
translation of pybliographer, whereas  in the same time Valek Filippov
brought to you a russian  version&nbsp;! These will be incorporated in
the next version.]]),

news_item([[27/07/2000]], [[1.0.4  is out. This  version improves some
formats (bibtex  strict mode now  recognizes its own files  as correct
;-), and  can parse  \ss{}. Refer accepts  %F fields thanks  to Martin
Wilck), and the  graphical interface (saving of columns  widths in the
index window, scrollbar in the  edition window for people having small
screens, better behavior of the selection after editing).]]),

news_item([[20/07/2000]], [[Now, this time it's for real, the
translations are included in the RPM files !]]),

news_item([[28/06/2000]], [[a new RPM package for pybliographer 1.0.3,
which this time includes the translations]]),

news_item([[26/06/2000]], [[it seems that after a week of upload at
0.2Kb/s, Konrad succeded in his attempt to provide us with the latest
RPMs for pybliographer 1.0.3&nbsp;! Thanks to him for his patience
;-)]]),

news_item([[13/06/2000]], [[let's go for  1.0.3! Now, it's possible to
read bibtex files  written on Windows, adding a new  field in an entry
doesn't  cancel previous modifications  on that  entry, and  some bugs
have been fixed in the formatting styles.]]),

news_item([[30/05/2000]], [[bugfix release  1.0.1 is out.  It corrects
problems with  empty bibtex databases and fixes  the broken pybconvert
script. The German and Italian translations are also updated]]),

news_item([[18/05/2000]], [[I plan to setup a FAQ on pybliographer. If
you think  that a particular  question should go  in it, let  me know!
I've also  added a <a  href="development.html">Development</a> section
on this site.]]),

news_item([[12/05/2000]], [[pybliographer  1.0.0 is out !  A few fixes
in  this   version  (concerning  the  save  order   for  entries  with
crossreferences).   Now,  let's start  on  the  new developement  tree
;-)]]),

news_item([[11/05/2000]], [[back from  holidays... The very last fixes
are being made to pybliographer before 1.0.0]]),

news_item([[20/04/2000]],    [[I've   created   a    mailing-list   at
SourceForge,  for general  discussions about  pybliographer.   You can
subscribe                                                            <a
href="http://lists.sourceforge.net/mailman/listinfo/pybliographer-general">here</a>.
]]),

news_item([[19/04/2000]],  [[there  are  now  <em>two</em>  unofficial
debian  packages for  pybliographer!  One has  been  provided by  Paul
Seelig,         and        is         available         from        <a
href="ftp://ntama.uni-mainz.de/pub/debian/unofficial/woody">here</a>,
and      another      by      Tobias     Bachmor,      located      <a
href="http://zemm.ira.uka.de/~bachmor/debian">here</a>. Thanks!]]),

news_item([[18/04/2000]],    [[we    are    now   at    0.9.11,    aka
1.0pre2.  Improved  bibtex  author  formatting and  fixed  compilation
problems with i18n support. I'll be on vacation two weeks, and plan to
release 1.0 when  I come back, depending on the  number of bug reports
I'll find in my mailbox ;-)]]),

news_item([[17/04/2000]], [[0.9.10 is out.  Consider this version as a
1.0pre1,  so please  report any  problem you  encounter with  it. I've
added bibtex customizations, and made  some minor bug fixes. It should
be  now  possible to  use  pybliographer  on endnote-generated  bibtex
files.]]),

news_item([[14/04/2000]],   [[Zoltán   Kóta   provided   a   hungarian
translation, which  will be  available in pybliographer  0.9.10. Don't
stop the translation effort! ]]),

news_item([[13/04/2000]],  [[RPMs of  pybliographer 0.9.9  are waiting
for you at the download section.]]),

news_item([[7/4/2000]],   [[gnome-python   1.0.53   is  out,   so   is
pybliographer  0.9.9.   This  version   is  only  a   minor  bug-fixes
release.]]),

news_item([[7/4/2000]], [[Holger Daszler has written a german po file,
which  will  be incorporated  in  the  next  release. If  your  native
language   is  not   Italian,  German   or  French,   please  consider
contributing a translation too !]]),

news_item([[4/4/2000]],  [[0.9.8  is out,  and  everybody is  strongly
advised  to  upgrade. This  version  is  still  based on  gnome-python
1.0.52, as 1.0.53 won't come  out immediately. In this new version, in
addition to  many bug fixes,  you will find a  graphical configuration
system,  ascending  and descending  sorting,  and  an XML-based  style
definition. Please try it and break it!]]),

news_item([[31/03/2000]], [[0.9.8  is almost ready, but  it requires a
not yet  released version of gnome-python...  If you want  to test it,
you have to  get the CVS version. It  provides graphical configuration
of many things  (like the structure of the  bibliography), plus an XML
parser for the description of the output styles.]]),

news_item([[23/03/2000]],  [[RPM files for  0.9.7.1 are  now available
(from    Konrad     Hinsen).    Go     get    them    on     the    <a
href="download.html">download page</a>.]]),

news_item([[15/03/2000]], [[issued 0.9.7.1 to fix the previous problem
plus an annoying bug in the creation of new entries...]]),

news_item([[15/03/2000]],   [[ooops,  for  those   having  compilation
problems    in    the   po/    directory,    juste   type    <tt>touch
Pyblio/Format/docbook.py</tt> in pybliographer-0.9.7, and your problem
should vanish.]]),

news_item([[14/03/2000]], [[version 0.9.7 is finally out!  As a lot of
changes  occured, this  version is  probably less  stable  that 0.9.6.
Nevertheless,  it  brings nice  improvements  (like multiple  document
interface, better  date handling, ...)  Documentation  will be updated
soon.              Oh,             watch            the             <a
href="download.html#requirements"><b>requirements</b></a>,  you really
need the latest gnome-python!]]),

news_item([[9/03/2000]], [[the basic graphical functionalities are now
working again (editing and sorting).  It will require the next version
of gnome-python, because of some bugs in the current one.]]),

news_item([[21/02/2000]],  [[the  core  is  ok.  Officially  supported
database formats  are now:  BibTeX (of course  !), Refer,  Medline and
Ovid. EndNote support  is cancelled for the moment,  as it is possible
to  export to  BibTeX  directly  (as I've  been  told). The  supported
formats provide now reading and writing. I'll add docbook again when I
feel like writing  the sgml parser. The interface  is still broken, as
MDI support  has some problems  under python... On another  topic, you
can       have       a      look       at       the      nice       <a
href="translations/it/index.html">italian   translation</a>   of   the
documentation, written by Yuri Bongiorno.]]),

news_item([[9/02/2000]], [[I've  started heavy cleanups  (motivated by
the early  spring weather  of Switzerland ;-))  that should lead  to a
much nicer code  and ease the writing of  some features (especially to
merge databases and read broken ones).]]),

news_item([[24/01/2000]],  [[Konrad Hinsen  kindly provided  RPM files
for      pybliographer      0.9.6.       Here      is      the      <a
href="pybliobase/pybliographer-0.9.6-1.i386.rpm">.i386.rpm</a> and the
<a  href="pybliobase/pybliographer-0.9.6-1.src.rpm">.src.rpm</a>.   On
the development side,  I expect to find some spare  time very soon, to
provide with  a new version. Primary  goal: fix the  file formats that
are supposed to work...]]),

news_item([[22/11/1999]],  [[version 0.9.6  is out,  with all  the new
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
...and I surely forget things...]]),

news_item([[16/11/1999]], [[version 0.9.6 will soon be ready.  It will
provide  lots  of nifty  improvements  (direct  citation insertion  in
<b>LyX</b>, internationalization,  ...). There are  also some projects
to create  new front-ends  for the  system: one for  KDE, and  one for
wxWindows.]])

]]
)m4_dnl
m4_dnl
m4_define(latest_news,m4_dnl
<dl>
$1
<p>$2
$3
$4
$5
$6
$7
$8
$9
$10
</dl>
)m4_dnl
m4_dnl
m4_define(all_the_news, [[<dl>all_the_subnews($@)</dl>]])m4_dnl
m4_define(all_the_subnews,m4_dnl
[[m4_ifelse($#, 0, , $#, 1, [[$1]],
[[$1
all_the_subnews(m4_shift($@))]])
]])m4_dnl
