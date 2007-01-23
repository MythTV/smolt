<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title> Stats </title>
</head>
<body>
    <table>
        <tr><td>Total Registered Hosts</td><td>${Host.select('1=1').count()}</td></tr>
        <tr><td>Total Registered Devices</td><td>${Device.select('1=1').count()}</td></tr>
        <tr><td>Arch's</td>
             <td>
                <table>
                    <tr py:for='arch in Stat["archs"]'>
                        <td>${arch[0]}</td><td>${arch[1]} </td><td><b py:for='i in range(1, int( float(arch[1]) / Stat["archstot"] * 50 ))'>|</b></td><td>${'%.1f' % (float(arch[1]) / Stat["archstot"] * 100) } %</td>
                    </tr>
                </table>
            </td>
        </tr>

        <tr><td>Operating Systems</td><td>
                <div py:for='OS in Stat["OS"]'>
                    ${OS[0]}: ${OS[1]}<br/>
                </div>
            </td></tr>
        <tr><td>Default Runlevel</td><td>
                <div py:for='rl in Stat["runlevel"]'>
                    (${rl[0]}): ${rl[1]}<br/>
                </div>
            </td></tr>
        <tr><td>Top 20 Devices</td><td>
                <div py:for='dev in Stat["devices"]'>
                    ${dev[0]}: ${dev[1]}<br/>
                </div>
            </td></tr>


    </table>
</body>
</html>
