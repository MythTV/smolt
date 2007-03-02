<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Show Box</title>
</head>
<body>
        <h3>${hostObject.UUID}</h3>
        <table id="show">
            <tr><th>UUID:</th><td>${hostObject.UUID}</td></tr>
            <tr><th>OS:</th><td>${hostObject.OS}</td></tr>
            <tr><th>platform:</th><td>${hostObject.platform}</td></tr>
            <tr><th>bogomips:</th><td>${hostObject.bogomips}</td></tr>
            <tr><th>systemMemory:</th><td>${hostObject.systemMemory}</td></tr>
            <tr><th>CPUVendor:</th><td>${hostObject.CPUVendor}</td></tr>
            <tr><th>numCPUs:</th><td>${hostObject.numCPUs}</td></tr>
            <tr><th>language:</th><td>${hostObject.language}</td></tr>
            <tr><th>defaultRunlevel:</th><td>${hostObject.defaultRunlevel}</td></tr>
            <tr><th>System Vendor:</th><td>${hostObject.vendor}</td></tr>
            <tr><th>System Model:</th><td>${hostObject.system}</td></tr>
        </table> 
        <h3>Devices</h3>
        <table id='show'>
            <tr>
                <th align='right'>Driver</th><th>Class</th><th>Bus</th><th>Vendor</th><th>Device</th><th>SubVendor</th><th>SubDevice</th><th align='left'>Description</th>
            </tr>
            <tr py:for='device in devices'>
                <td align='right'>${device.Driver}</td>
                <td align='center'>${device.Class}</td>
                <td align='center'>${device.Bus}</td>
                <td align='center'>${hex(device.VendorId)}</td>
                <td align='center'>${device.DeviceId}</td>
                <td align='center'>${device.SubsysDeviceId}</td>
                <td align='center'>${device.SubsysVendorId}</td>
                <td align='left'>${device.Description}</td>
            </tr>
        </table>
</body>
</html>
