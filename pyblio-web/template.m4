dnl
dnl Standard macros
dnl
changequote([[,]])dnl
changecom([[##]])dnl
dnl
dnl --------------------------------------------------
dnl
dnl
dnl --------------------------------------------------
dnl
define(html_header,dnl
[[<html>
<head>
<title> $1 </title>
<meta http-equiv="Content-Type" content="text/html; charset=latin-1">
<meta name="Author" content="Frédéric Gobry">
</head>
<body bgcolor="#ffffff">
<center><img src="pyblio.png" width="367" height="78" 
alt="p y b l i o g r a p h e r"></center>
]])dnl
dnl
dnl --------------------------------------------------
dnl
define(html_footer,dnl
[[<hr><p align="center">
<a href="http://www.anybrowser.org/campaign/"> 
<img src="anybrowser.png" width="88"
 height="31" alt="Best Seen with ANY Browser" border="0"></a>
<p align="center">Thanks to the GNOME Project for hosting these pages</p>
<p align="right">Send your comments to 
<a href="mailto:frederic.gobry@epfl.ch">Frédéric Gobry</a>
<br> html_date
</body></html>]]) dnl
dnl
dnl --------------------------------------------------
dnl
define(html_item_summary, [[ifelse(html_current_item, $1, $3, $2)]])
dnl
define(html_summary, 
[[<table><tbody>
<tr><td bgcolor="#eeeeff" align="left" valign="top">
define([[html_current_item]], $1)
include($2)
</td><td align="left">
$3
</td></tbody></table>]]) dnl
define(html_url, <a href="$1">$1</a>)dnl
define(html_mail, <a href="mailto:$1">&lt;$1&gt;</a>)dnl
dnl
dnl -----
dnl
define(html_testfile, [[syscmd(ls $1 >/dev/null 2>&1)sysval]])dnl
define(html_filesize, [[regexp(esyscmd(ls -lh $1 2> /dev/null | awk '{print $ 5;}'),.*,\&)]])dnl
define(html_date, [[esyscmd(date)]])dnl