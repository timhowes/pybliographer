m4_dnl
m4_dnl Standard macros
m4_dnl
m4_changequote([[,]])m4_dnl
m4_changecom([[##]])m4_dnl
m4_dnl
m4_dnl --------------------------------------------------
m4_dnl
m4_dnl
m4_dnl --------------------------------------------------
m4_dnl
m4_define(html_header,[[<html>
<head>
<title> $1 </title>
<meta http-equiv="Content-Type" content="text/html; charset=latin-1">
<meta name="Author" content="Frédéric Gobry">
</head>
<body bgcolor="#ffffff">
<center><img src="pyblio.png" width="367" height="78" 
alt="p y b l i o g r a p h e r">
<p><b>This site is frozen. The current active site is <a
href="http://pybliographer.org/">pybliographer.org</a></b>

</center>

]])m4_dnl
m4_dnl
m4_dnl --------------------------------------------------
m4_dnl
m4_define(html_footer,m4_dnl
[[<hr><p align="center">

<table align=center><tbody valign="center">
<tr>
<td><a href="http://www.opensource.org/docs/definition.php"> <img
src="http://www.opensource.org/trademarks/opensource/web/opensource-75x65.png"
border="0" width="75" height="65" alt="[Open Source]"></a></td>

<td><a href="http://www.anybrowser.org/campaign/"> 
<img src="anybrowser.png" width="88"
 height="31" alt="[Best Seen with ANY Browser]" border="0"></a></td>

<td><A HREF="http://petition.eurolinux.org">   
<img src="http://www.aful.org/images/patent_button.png" alt="[No Patents]" 
width="88" heigth="36" border="0"></A></td>

</tr></tbody></table>

m4_dnl<p align="center">Thanks to the GNOME Project for hosting these pages</p>
<p align="center"><A href="http://sourceforge.net"> <IMG src="http://sourceforge.net/sflogo.php?group_id=4825&amp;type=5" width="210" height="62" border="0" alt="SourceForge.net Logo" /></A></p>
<p align="right">Send your comments to the
<a href="mailto:webmaster@pybliographer.org">Webmaster</a>
<br><small>Last update: html_date</small>
</body></html>]]) m4_dnl
m4_dnl
m4_dnl --------------------------------------------------
m4_dnl
m4_define(html_item_summary, [[m4_ifelse(html_current_item, $1, $3, $2)]])m4_dnl
m4_dnl
m4_define(html_summary,m4_dnl
[[<table><tbody>
<tr><td bgcolor="#eeeeff" align="left" valign="top">
m4_define([[html_current_item]], $1)m4_dnl
m4_include($2)m4_dnl
</td><td align="left">
$3
</td></tbody></table>]]) m4_dnl
m4_define(html_url, <a href="$1">$1</a>)m4_dnl
m4_define(html_mail, <a href="mailto:$1">&lt;$1&gt;</a>)m4_dnl
m4_dnl
m4_dnl -----
m4_dnl
m4_define(html_testfile, [[m4_syscmd(ls $1 >/dev/null 2>&1)m4_sysval]])m4_dnl
m4_define(html_filesize, [[m4_regexp(m4_esyscmd(ls -lh $1 2>/dev/null|awk '{print $ 5;}'),.*,\&)]])m4_dnl
m4_define(html_date, [[m4_esyscmd(date +%d/%m/%Y)]])m4_dnl
