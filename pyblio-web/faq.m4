m4_dnl -*- html -*-

html_header(Pybliographer - FAQ)

m4_define(faq_item, [[<li><b>$1</b>
<br>$2]])m4_dnl

html_summary(faq, summary.m4, [[

<h1>Frequently Asked Questions</h1>

<ul> 

faq_item([[When adding a new entry, pybliographic outputs a lot of
messages ending with something like:
<br>
IOError: can't parse entry `@preamble{{']], [[You probably have a
broken version of GNU recode. Please check the <a
href="download.html#requirements">requirements</a> section, which
hopefully contains information for your linux distribution.]])

faq_item([[Pybliographic shows some text in lower case whereas it is
in upper case in the bibtex file.]], [[This is not a bug, it's a
feature&nbsp;! ;-) Pybliographer tries to mimic bibtex's behavior,
which recapitalizes some fields (like the title), so that you see what
you would get. You can configure which fields are subject to this
recapitalization in the Preference menu.]])


faq_item([[I don't see the new display system which allows clicking on
URLs...]], [[Your version of gnome-python is not compiled with support
for GtkHTML. You may need to compile it from the sources.]])

faq_item([[I've  upgraded  Gnome  to  version  1.4  and  Pybliographic
doesn't work anymore !]], [[If you are using Ximian Gnome, you need to
(temporarily) remove the monkeytalk package]])

faq_item([[Will    pybliographer   work   on    my   machine&nbsp;?]],
[[Pybliographer relies  on python (which  is available for  almost any
existing platform) and on some  compiled code. This code is written in
ANSI C,  but will compile  out of the  box only on Unix  machines. For
Windows, Macintosh,... you have  to compile it yourself. The graphical
interface  uses  gnome-python,  which   is  available  for  many  unix
architectures, but <b>not</b> on Windows or Macintosh.]])

faq_item([[Pybliographic  freezes  whenever  I  open a  database  !]],
[[Check that you have Gtk+ >= 1.2.7]])

faq_item([[When  starting pybliographic, I  get the  following message:
Fatal  Python  error:   can't  initialise  module  _gdkimlib]],  [[You
probably installed gnome-python from a RPM but your gnome installation
is not complete. Try installing gnome-python from the sources.]])

faq_item([[Pybliograph(ic|er)  complains  about  a missing  gettext.py
!]], [[Check that  you installed gnome-python with the  same prefix as
python.]])

faq_item([[The Close button of the search menu behaves as the Search
button]],[[Check that you have installed gnome-python 1.0.53 at least,
and that the <b>installation prefix</b> is the same as the one used
for python (usually /usr on Linux systems).]])

faq_item([[I cannot cite an entry in LyX, whereas all the paths are
correctly specified.]], [[On some systems, it is not possible to
read a pipe on a NFS device. You can specify another name for the
lyxserver pipe, so that it is located on a local disk.]])

faq_item([[How can I display the Key/Type of the entries in the index window?]],
[[You can edit the preferences and add special fields called <b>-Key-</b> and <b>-Type-</b>.
Don't forget the minus signs...]])

</ul>
]])

html_footer
