<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Smolt</title>
</head>
<body>

<h1> Smolt </h1>

Most people probably want to go to <a href='/stats'>/stats</a> or <a href='/devices'>/devices</a>

<h2>Lookup</h2>
    <form method='GET' action='/show'>
        UUID: <input type='text' name='UUID' size='32'/>
    </form>
<h2>Growth</h2>
    <img src="/cacti/smoltArch.png"/>

<h2>More info</h2>
    Usage and other general answers can be found at <a href='https://hosted.fedoraproject.org/projects/smolt'>https://hosted.fedoraproject.org/projects/smolt</a>

</body>
</html>
