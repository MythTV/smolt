<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Welcome to TurboGears</title>
</head>
<body>

        <span py:replace="hostObject.UUID">UUID</span><br/>
        <span py:replace="hostObject.lsbRelease">lsbRelease</span><br/>
        <span py:replace="hostObject.OS">OS</span><br/>
        <span py:replace="hostObject.platform">platform</span><br/>
        <span py:replace="hostObject.bogomips">bogomips</span><br/>
        <span py:replace="hostObject.systemMemory">systemMemory</span><br/>
        <span py:replace="hostObject.CPUVendor">CPUVendor</span><br/>
        <span py:replace="hostObject.numCPUs">numCPUs</span><br/>
        <span py:replace="hostObject.CPUSpeed">CPUSpeed</span><br/>
        <span py:replace="hostObject.language">language</span><br/>
        <span py:replace="hostObject.defaultRunlevel">defaultRunlevel</span><br/>

</body>
</html>
