<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
	<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Show Box</title>
${ratingwidget.display(update="rating", 
                       href="/rate_object", 
                       num="5",
                       img_on="/static/images/stars/rating_on.gif",
                       img_off="/static/images/stars/rating_off.gif",
                       img_over="/static/images/stars/rating_over.gif",
                       imgon_pre="/static/images/rating/r",
                       imgoff_pre="/static/images/rating/ro",
                       imgbusy_pre="/static/images/rating/rb",
                       img_post=".gif",
)}
</head>
<body>

<span py:def="wikilink(name, device)">
<a py:if="device.vendor_id and device.device_id" href="${getDeviceWikiLink(device)}">${name}</a>
<span py:if="not (device.vendor_id and device.device_id)" py:replace="name"></span>
</span>
<!--
	<div class='share' id='share' name='share'>
		<a href='share?sid=${host_object.id}'>Share my computer!</a>
	</div>
-->
        <h3>${host_object.uuid}</h3>

	<div id="legend">
            <img src="/static/images/rating/r0.gif"/> I don't use this/I don't know<br/>
	    <img src="/static/images/rating/r1.gif"/> Breaks System<br/>
	    <img src="/static/images/rating/r2.gif"/> Doesn't Work<br/>
	    <img src="/static/images/rating/r3.gif"/> Requires 3rd Party Drivers<br/>
	    <img src="/static/images/rating/r4.gif"/> Works, but required aditional configuration<br/>
	    <img src="/static/images/rating/r5.gif"/> Worked out of the box<br/>
	    <p><a href="/client/show?UUID=${host_object.uuid}">Show basic Information</a></p>
	</div>
        <table id="system_show">
       	    <tr><th>Rating:</th><td><div class="rating" id="Host${host_object.uuid}">${host_object.rating}</div></td></tr>
            <tr><th>UUID:</th><td>${host_object.uuid}</td></tr>
            <tr><th>Operating System:</th><td><a href="${getOSWikiLink(host_object)}">${host_object.os}</a></td></tr>
            <tr><th>Platform:</th><td>${host_object.platform}</td></tr>
            <tr><th>Bogomips:</th><td>${host_object.bogomips}</td></tr>
            <tr><th>CPU Speed:</th><td>${host_object.cpu_speed}</td></tr>
            <tr><th>System Memory:</th><td>${host_object.system_memory}</td></tr>
            <tr><th>CPUVendor:</th><td>${host_object.cpu_vendor}</td></tr>
            <tr><th>Number of CPUs:</th><td>${host_object.num_cpus}</td></tr>
            <tr><th>Language:</th><td>${host_object.language}</td></tr>
            <tr><th>Default Runlevel:</th><td>${host_object.default_runlevel}</td></tr>
            <tr><th>System Vendor:</th><td>${host_object.vendor}</td></tr>
            <tr><th>System Model:</th><td><a href="${host_link}">${host_object.system}</a></td></tr>
            <tr><th>Kernel</th><td>${host_object.kernel_version}</td></tr>
            <tr><th>Formfactor</th><td>${host_object.formfactor}</td></tr>
            <tr><th>SELinux Enabled</th><td>${host_object.selinux_enabled}</td></tr>
            <tr><th>SELinux Enforce</th><td>${host_object.selinux_enforce}</td></tr>
            <tr><th>Last Modified</th><td>${host_object.last_modified}</td></tr>
        </table> 
        <h3>Devices</h3>
        <table id="device_show">
            <tr>
                <th>Rating</th><th>Vendor</th><th>Device</th><th>SubVendor</th><th>SubDevice</th><th>Driver</th><th>Class</th><th>Bus</th>
            </tr>
            <tr py:for='device_node in devices'>
            	<?python device = device_node[0] ?>
            	<td align='left'><div class="rating" id="Host${host_object.uuid}_Device${device.id}">${device_node[1]}</div></td>
                <td align='center'>${ven.vendor(device.vendor_id, bus=device.bus)}</td>
		<td align='center'><span py:replace="wikilink(ven.device(device.vendor_id, device.device_id, alt=device.description, bus=device.bus), device)">Devicename</span></td>
                <td align='center'>${ven.vendor(device.subsys_device_id)}</td>
                <td align='center'>${ven.subdevice(device.vendor_id, device.device_id, device.subsys_vendor_id, device.subsys_device_id)}</td>
                <td align='center'>${device.driver}</td>
                <td align='center'>${device.cls}</td>
                <td align='center'>${device.bus}</td>
                <!--<td align='left'>${device.Description}</td>-->
            </tr>
        </table>
</body>
</html>
