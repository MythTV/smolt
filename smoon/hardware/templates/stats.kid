<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title> Stats </title>
</head>
<body>
    <table id="stats" width="100%" border="0" cellpadding="3" cellspacing="3">
        <tr>
            <th valign="top" width="25%">Total Registered Hosts</th>
            <td><strong>${Host.select('1=1').count()}</strong></td>
        </tr>
        <tr>
            <th valign="top">Total Registered Devices</th>
            <td><strong>${Device.select('1=1').count()}</strong></td>
        </tr>
        <tr>
            <th valign="top">Total bogomips</th>
            <td><strong>${Stat["bogomipsTot"]}</strong></td>
        </tr>
        <tr>
            <th valign="top">Total processors</th>
            <td><strong>${Stat["cpusTot"]}</strong></td>
        </tr>
        <tr>
            <th valign="top">Total MHz</th>
            <td><strong>${Stat["cpuSpeedTot"]}</strong></td>
        </tr>

        <tr>
            <th valign="top">Archs</th>
            <td>
                <table id="stats">
                    <tr py:for='arch in Stat["archs"]'>
                        <td align="right">${arch[0]}</td>
                        <td align="center">${arch[1]}</td>
                        <td><strong>${'%.1f' % (float(arch[1]) / Stat["archstot"] * 100) } %</strong></td>
                        <td><img py:for='i in range(1, int( float(arch[1]) / Stat["archstot"] * 100 ))' src='/static/images/tile.png' /></td>
                    </tr>
                    <!--<tr>
                        <td colspan="4">
                            <img src="/cacti/smoltArch.png"/>
                        </td>
                    </tr>-->
                </table>
            </td>
        </tr>

        <tr>
            <th valign="top">Operating Systems</th>
            <td>
                <table id="stats">
                    <tr py:for='OS in Stat["OS"]'>
                        <td align="right">${OS[0]}</td>
                        <td align="center">${OS[1]}</td>
                        <td nowrap="true"><strong>${'%.1f' % (float(OS[1]) / Stat["OStot"] * 100) } %</strong></td>
                        <td nowrap="true"><img py:for='i in range(1, int( float(OS[1]) / Stat["OStot"] * 100 ))' src='/static/images/tile.png' /></td>
                    </tr>
                </table>
            </td>
        </tr>

        <tr>
            <th valign="top">Default Runlevel</th>
            <td>
                <table id="stats">
                    <tr py:for='rl in Stat["runlevel"]'>
                        <td align="right">${rl[0]}</td>
                        <td align="center">${rl[1]}</td>
                        <td><strong>${'%.1f' % (float(rl[1]) / Stat["runleveltot"] * 100) } %</strong></td>
                        <td><img py:for='i in range(1, int( float(rl[1]) / Stat["runleveltot"] * 100 ))' src='/static/images/tile.png' /></td>
                    </tr>
                </table>
            </td>
        </tr>

        <tr>
            <th valign="top">Language (Top 15)</th>
            <td>
                <table id="stats">
                    <tr py:for='lang in Stat["language"]'>
                        <td align="right">${lang[0]}</td>
                        <td align="center">${lang[1]}</td>
                        <td><strong>${'%.1f' % (float(lang[1]) / Stat["languagetot"] * 100) } %</strong></td>
                        <td><img py:for='i in range(1, int( float(lang[1]) / Stat["languagetot"] * 100 ))' src='/static/images/tile.png' /></td>
                    </tr>
                </table>
            </td>
        </tr>

        <tr>
            <th valign="top">Vendor (Top 15)</th>
            <td>
                <table id="stats">
                    <tr py:for='vendor in Stat["vendors"]'>
                        <td align="right">${vendor[0]}</td>
                        <td align="center">${vendor[1]}</td>
                        <td><strong>${'%.1f' % (float(vendor[1]) / Stat["languagetot"] * 100) } %</strong></td>
                        <td><img py:for='i in range(1, int( float(vendor[1]) / Stat["languagetot"] * 100 ))' src='/static/images/tile.png' /></td>
                    </tr>
                </table>
            </td>
        </tr>



<!--        <tr>
            <th valign="top">CPU Vendor</th>
            <td>
                <table id="stats">
                    <tr py:for='cpuVen in Stat["cpuVendor"]'>
                        <td align="right">${Stat["cpuVendor"][cpuVen]}</td>
                        <td align="center">${cpuVen}</td>
                        <td><strong>${'%.1f' % (float(Stat["cpuVendor"][cpuVen]) / Stat["cpuVendortot"] * 100) } %</strong></td>
                        <td><img py:for='i in range(1, int( float(Stat["cpuVendor"][cpuVen]) / Stat["cpuVendortot"] * 100 ))' src='/static/images/tile.png' /></td>
                    </tr>
                </table>
            </td>
        </tr>-->



       <tr>
            <th valign="top">System Memory</th>
            <td>
                <table id="stats">
                    <tr py:for='mem in Stat["sysMem"]'>
                        <td align="right">${mem[0]}</td>
                        <td align="center">${mem[1]}</td>
                        <td><strong>${'%.1f' % (float(mem[1]) / Host.select('1=1').count() * 100) } %</strong></td>
                        <td><img py:for='i in range(1, int( float(mem[1]) / Host.select("1=1").count() * 100 ))' src='/static/images/tile.png' /></td>
                    </tr>
                </table>
            </td>
        </tr>

       <tr>
            <th valign="top">Swap Memory</th>
            <td>
                <table id="stats">
                    <tr py:for='mem in Stat["swapMem"]'>
                        <td align="right">${mem[0]}</td>
                        <td align="center">${mem[1]}</td>
                        <td><strong>${'%.1f' % (float(mem[1]) / Host.select('1=1').count() * 100) } %</strong></td>
                        <td><img py:for='i in range(1, int( float(mem[1]) / Host.select("1=1").count() * 100 ))' src='/static/images/tile.png' /></td>
                    </tr>
                </table>
            </td>
        </tr>

        <tr>
            <th valign="top">CPU Speed</th>
            <td>
                <table id="stats">
                    <tr py:for='cpuSpeed in Stat["cpuSpeed"]'>
                        <td align="right">${cpuSpeed[0]}</td>
                        <td align="center">${cpuSpeed[1]}</td>
                        <td><strong>${'%.1f' % (float(cpuSpeed[1]) / Host.select('1=1').count() * 100) } %</strong></td>
                        <td><img py:for='i in range(1, int( float(cpuSpeed[1]) / Host.select("1=1").count() * 100 ))' src='/static/images/tile.png' /></td>
                    </tr>
                </table>
            </td>
        </tr>

        <tr>
            <th valign="top">bogomips</th>
            <td>
                <table id="stats">
                    <tr py:for='bogomips in Stat["bogomips"]'>
                        <td align="right">${bogomips[0]}</td>
                        <td align="center">${bogomips[1]}</td>
                        <td><strong>${'%.1f' % (float(bogomips[1]) / Host.select('1=1').count() * 100) } %</strong></td>
                        <td><img py:for='i in range(1, int( float(bogomips[1]) / Host.select("1=1").count() * 100 ))' src='/static/images/tile.png' /></td>
                    </tr>
                </table>
            </td>
        </tr>

        <tr>
            <th valign="top">Top 20 Devices</th>
            <td>
                <table id="stats">
                    <!--<tr py:for='dev in Stat["devices"]'>
                        <td align="right">${dev[0]}</td>
                        <td align="center">${dev[1]}</td>
                        <td nowrap="true"><strong>${'%.1f' % (float(dev[1]) / Stat["devicestot"] * 100) } %</strong></td>
                        <td nowrap="true"><img py:for='i in range(1, int( float(dev[1]) / Stat["devicestot"] * 100 ))' src='/static/images/tile.png' /></td>
                    </tr>-->
                    <!--<tr>
                        <td align="right">Other</td>
                        <td align="center"></td>
                        <td nowrap="true"><strong>${'%.1f' % (float(Stat["devices20sum"]) / Stat["devicestot"] * 100) } %</strong></td>
                        <td><img py:for='i in range(1, int( float(Stat["devices20sum"]) / Stat["devicestot"] * 100 ))' src='/static/images/tile.png' /></td>
                    </tr>-->
                </table>
            </td>
        </tr>
 
    </table>
</body>
</html>
