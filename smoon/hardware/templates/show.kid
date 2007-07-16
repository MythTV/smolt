<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Show Box</title>
</head>
<body>
	<form action="submit_ratings?uuid=${hostObject.uuid}" method="post">
        <h3>${hostObject.uuid}</h3>
		<p class='moof'><button type='submit'>Submit your ratings</button></p>
		<p>Rating: ${hostObject.rating}</p>
        <table id="show">
        	<tr><th>Rating:</th><td>${rating(value=hostObject.rating, field_id="host_rating")}</td></tr>
            <tr><th>UUID:</th><td>${hostObject.uuid}</td></tr>
            <tr><th>OS:</th><td>${hostObject.os}</td></tr>
            <tr><th>platform:</th><td>${hostObject.platform}</td></tr>
            <tr><th>bogomips:</th><td>${hostObject.bogomips}</td></tr>
            <tr><th>CPU Speed:</th><td>${hostObject.cpu_speed}</td></tr>
            <tr><th>systemMemory:</th><td>${hostObject.system_memory}</td></tr>
            <tr><th>CPUVendor:</th><td>${hostObject.cpu_vendor}</td></tr>
            <tr><th>numCPUs:</th><td>${hostObject.num_cpus}</td></tr>
            <tr><th>language:</th><td>${hostObject.language}</td></tr>
            <tr><th>defaultRunlevel:</th><td>${hostObject.default_runlevel}</td></tr>
            <tr><th>System Vendor:</th><td>${hostObject.vendor}</td></tr>
            <tr><th>System Model:</th><td>${hostObject.system}</td></tr>
            <tr><th>Kernel</th><td>${hostObject.kernel_version}</td></tr>
            <tr><th>Formfactor</th><td>${hostObject.formfactor}</td></tr>
            <tr><th>SELinux Enabled</th><td>${hostObject.selinux_enabled}</td></tr>
            <tr><th>SELinux Enforce</th><td>${hostObject.selinux_enforce}</td></tr>
            <tr><th>Last Modified</th><td>${hostObject.last_modified}</td></tr>
        </table> 
        <h3>Devices</h3>
        <table id='show'>
            <tr>
                <th>Rating</th><th align='right'>Driver</th><th>Class</th><th>Bus</th><th>Vendor</th><th>Device</th><th>SubVendor</th><th>SubDevice</th>
            </tr>
            <tr py:for='device_node in devices.values()'>
            	<?python device = device_node[0] ?>
            	<td align='left'>${rating(value=device_node[1], field_id="device_%s" % device.id)}</td>
                <td align='right'>${device.driver}</td>
                <td align='center'>${device.klass}</td>
                <td align='center'>${device.bus}</td>
                <td align='center'>${ven.vendor(device.vendor_id, bus=device.bus)}</td>
                <td align='center'>${ven.device(device.vendor_id, device.device_id, alt=device.description, bus=device.bus)}</td>
                <td align='center'>${ven.vendor(device.subsys_device_id)}</td>
                <td align='center'>${ven.subdevice(device.vendor_id, device.device_id, device.subsys_vendor_id, device.subsys_vendor_id)}</td>
                <!--<td align='left'>${device.Description}</td>-->
            </tr>
        </table>
	</form>
</body>
</html>
