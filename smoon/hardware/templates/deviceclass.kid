<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title> Stats </title>
</head>
<body>
    <table id="stats" width="100%" border="0" cellpadding="3" cellspacing="3">
        <tr>
            <th valign="top" width="25%">Total Count</th>
            <td><strong>${count}</strong></td>
        </tr>
        <tr>
            <th valign="top" width="25%">% hosts detected ${type}</th>
            <td><strong>${'%.1f' % (float(count) / totalHosts * 100)} %</strong></td>
        </tr>
    </table>

    <table id='stats' width="100%" border="0" cellpadding="3" cellspacing="3">
        <tr py:for='vendor in vendors'>
            <td>${pciVendors.vendor(vendor[0])}</td>
            <td>${vendor[1]}</td>
            <td nowrap="true"><strong>${'%.1f' % (float(vendor[1]) / totalHosts * 100) } %</strong></td>
            <td nowrap="true"><img py:for='i in range(1, int( float(vendor[1]) / totalHosts * 100 ))' src='/static/images/tile.png' /></td>

        </tr>
    </table>
    <table id="stats" width="100%" border="0" cellpadding="3" cellspacing="3">
        <tr><th>Device</th><td>bus</td><td>Driver</td><td>Vendor</td><td>Sub Vendor</td><td>Sub Device</td><td>Date Added</td><td>% tot hosts</td><td></td></tr>
        <tr py:for='type in types'>
            <th align="right">${pciVendors.device(type[3], type[4], alt=type[1])}</th>
            <td align="center">${type[1]}</td>
            <td align="center">${type[2]}</td>
            <td align="center">${pciVendors.vendor(type[3])}</td>
<!--            <td align="center">${pciVendors.device(type[3], type[4], alt=type[7])}</td>-->
            <td align="center">${pciVendors.vendor(type[5])}</td>
            <td align="center">${pciVendors.subdevice(type[3], type[4], type[5], type[6])}</td>
            <td align="center">${type[7]}</td>
            <td nowrap="true"><strong>${'%.1f' % (float(type[8]) / totalHosts * 100) } %</strong></td>
            <td nowrap="true"><img py:for='i in range(1, int( float(type[8]) / totalHosts * 100 ))' src='/static/images/tile.png' /></td>
        </tr>
    </table>

</body>
</html>
