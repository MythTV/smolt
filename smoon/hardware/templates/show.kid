<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Show Box</title>
</head>
<body>
	<form action="submit_ratings?uuid=${hostObject.UUID}" method="post">
        <h3>${hostObject.UUID}</h3>
		<p class='moof'><button type='submit'>Submit your ratings</button></p>
		<p>Rating: ${hostObject.rating}</p>
        <table id="show">
        	<tr><th>Rating:</th><td>${rating(value=hostObject.rating, field_id="host_rating")}</td></tr>
            <tr><th>UUID:</th><td>${hostObject.UUID}</td></tr>
            <tr><th>OS:</th><td>${hostObject.OS}</td></tr>
            <tr><th>platform:</th><td>${hostObject.platform}</td></tr>
            <tr><th>bogomips:</th><td>${hostObject.bogomips}</td></tr>
            <tr><th>CPU Speed:</th><td>${hostObject.CPUSpeed}</td></tr>
            <tr><th>systemMemory:</th><td>${hostObject.systemMemory}</td></tr>
            <tr><th>CPUVendor:</th><td>${hostObject.CPUVendor}</td></tr>
            <tr><th>numCPUs:</th><td>${hostObject.numCPUs}</td></tr>
            <tr><th>language:</th><td>${hostObject.language}</td></tr>
            <tr><th>defaultRunlevel:</th><td>${hostObject.defaultRunlevel}</td></tr>
            <tr><th>System Vendor:</th><td>${hostObject.vendor}</td></tr>
            <tr><th>System Model:</th><td>${hostObject.system}</td></tr>
            <tr><th>Kernel</th><td>${hostObject.kernelVersion}</td></tr>
            <tr><th>Formfactor</th><td>${hostObject.formfactor}</td></tr>
            <tr><th>SELinux Enabled</th><td>${hostObject.selinux_enabled}</td></tr>
            <tr><th>SELinux Enforce</th><td>${hostObject.selinux_enforce}</td></tr>
            <tr><th>Last Modified</th><td>${hostObject.lastModified}</td></tr>
        </table> 
        <h3>Devices</h3>
        <table id='show'>
            <tr>
                <th>Rating</th><th align='right'>Driver</th><th>Class</th><th>Bus</th><th>Vendor</th><th>Device</th><th>SubVendor</th><th>SubDevice</th>
            </tr>
            <tr py:for='device_node in devices.values()'>
            	<?python device = device_node[0] ?>
            	<td align='left'>${rating(value=device_node[1], field_id="device_%s" % device.id)}</td>
                <td align='right'>${device.Driver}</td>
                <td align='center'>${device.Class}</td>
                <td align='center'>${device.Bus}</td>
                <td align='center'>${ven.vendor(device.VendorId, bus=device.Bus)}</td>
                <td align='center'>${ven.device(device.VendorId, device.DeviceId, alt=device.Description, bus=device.Bus)}</td>
                <td align='center'>${ven.vendor(device.SubsysVendorId)}</td>
                <td align='center'>${ven.subdevice(device.VendorId, device.DeviceId, device.SubsysVendorId, device.SubsysDeviceId)}</td>
                <!--<td align='left'>${device.Description}</td>-->
            </tr>
        </table>
	</form>
</body>
</html>
