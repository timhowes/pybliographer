m4_dnl -*- html -*-

html_header(Pybliographer - FAQ)

m4_define(faq_item, [[<li><b>$1</b>
<br>$2]])m4_dnl

html_summary(faq, summary.m4, [[

<h1>Frequently Asked Questions</h1>

<ul>
faq_item([[Will    pybliographer   work   on    my   machine&nbsp;?]],
[[Pybliographer relies  on python (which  is available for  almost any
existing platform) and on some  compiled code. This code is written in
ANSI C,  but will compile  out of the  box only on Unix  machines. For
Windows, Macintosh,... you have  to compile it yourself. The graphical
interface  uses  gnome-python,  which   is  available  for  many  unix
architectures, but <b>not</b> on Windows or Macintosh.]])

faq_item([[Pybliographic  freezes  whenever  I  open a  database  !]],
[[Check that you have Gtk+ >= 1.2.7]])

faq_item([[The  installation  procedure  just  does  not  install  the
catalog for my favorite language, whereas there is support for it !]],
[[Try to  unset the environment variable  LINGUAS, remove config.cache
and reconfigure the package.]])

faq_item([[When  stating pybliographic, I  get the  following message:
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

</ul>
]])

html_footer
