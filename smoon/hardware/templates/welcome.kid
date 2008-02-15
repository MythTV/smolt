<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Smolt</title>
</head>
<body>
<h2>Lookup</h2>
    <form method='GET' action='/show'>
        Enter your profile UUID: <input type='text' name='uuid' size='32'/>
    </form>
<p></p>
<h2>Statistics</h2>
<p>
For detailed statistics about the devices in the database see <a href='/static/stats/stats.html'>/stats</a> or <a href='/static/stats/devices.html'>/devices</a>
</p>

<h2> Arch Chart </h2>
    ${archFlot.display()}
<!--<h2>Growth</h2>
<p><img src="/cacti/smoltArch.png"/></p> -->

<h2>More info</h2>
<p>Browse and search the <a href="/wiki/">Wiki</a> for detailed information about specific devices.
Usage and other general answers can also be found at the <a href="/wiki/">Wiki</a>.</p>
</body>
</html>
