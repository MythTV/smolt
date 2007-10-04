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
                       img_post=".gif",
)}
</head>
<body>

<span py:def="wikilink(name, bus, vendor_id, device_id, subsys_vendor_id, subsys_device_id)">
<a href="${getWikiLink(bus, vendor_id, device_id, subsys_vendor_id, subsys_device_id)}">${name}</a>&nbsp;
</span>
<!--
	<div class='share' id='share' name='share'>
		<a href='share?sid=${host_object.id}'>Share my computer!</a>
	</div>
-->
        <h3>${host_object.uuid}</h3>

	<div id="legend">
	    <img src="/static/images/rating/r1.gif"/> Breaks System<br/>
	    <img src="/static/images/rating/r2.gif"/> Doesn't Work<br/>
	    <img src="/static/images/rating/r3.gif"/> Requires 3rd Party Drivers<br/>
	    <img src="/static/images/rating/r4.gif"/> Works, but required aditional configuration<br/>
	    <img src="/static/images/rating/r5.gif"/> Worked out of the box<br/>
	    <p><a href="show_all?UUID=${host_object.uuid}">Show all Information</a></p>
	</div>
        <table id="system_show">
       	    <tr><th>Rating:</th><td><div class="rating" id="Host${host_object.uuid}">${host_object.rating}</div></td></tr>
            <tr><th>UUID:</th><td>${host_object.uuid}</td></tr>
            <tr><th>Operating System:</th><td>${host_object.os}</td></tr>
            <tr><th>Platform:</th><td>${host_object.platform}</td></tr>
            <tr><th>System Vendor:</th><td>${host_object.vendor}</td></tr>
            <tr><th>System Model:</th><td>${host_object.system}</td></tr>
            <tr><th>Kernel</th><td>${host_object.kernel_version}</td></tr>
            <tr><th>Formfactor</th><td>${host_object.formfactor}</td></tr>
            <tr><th>Last Modified</th><td>${host_object.last_modified}</td></tr>
        </table> 
        <h3>Devices</h3>
        <table id="device_show">
            <tr>
                <th>Rating</th><th>Device</th><th>Class</th>
            </tr>
	    <?python 
device_list = devices.values()
device_list.sort(key=lambda x: x[0].cls)
	    ?>
            <tr py:for='device_node in device_list' py:if="device_node[0].vendor_id and device_node[0].device_id">
            	<?python device = device_node[0] 
		device_name = "%s %s (%s %s)" % ( ven.vendor(device.vendor_id, bus=device.bus),
			 ven.device(device.vendor_id, device.device_id, alt=device.description, bus=device.bus),
			 ven.vendor(device.subsys_device_id),
			 ven.subdevice(device.vendor_id, device.device_id, device.subsys_vendor_id, device.subsys_device_id))
?>
            	<td><div class="rating" id="Host${host_object.uuid}_Device${device.id}">${device_node[1]}</div></td>
		<td><span py:replace="wikilink(device_name, device.bus, device.vendor_id, device.device_id, device.subsys_vendor_id, device.subsys_device_id)">Wiki</span></td>
                <td align='center'>${device.cls}</td>
                <!--<td align='left'>${device.Description}</td>-->
            </tr>
        </table>
</body>
</html>
