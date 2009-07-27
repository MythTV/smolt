from i18n import _

PRIVACY_POLICY =  _(\
"""<span></span>
Smolt will only send hardware and basic operating system information to the
Fedora smolt server (smoon).  The only tie from the database to a submitters
machine is the UUID.  As long as the submitter does not give out this UUID
the submission is anonymous.  If at any point in time a user wants to delete
his/her profile from the database they need only run<br>
<br>
&nbsp;&nbsp;&nbsp;<tt>smoltDeleteProfile</tt><br>
<br>
The information sent to the smolt database server should be considered public
in that anyone can view the statistics, data and share machine profiles.  In 
many ways smolt is designed to get hardware vendors and other 3rd parties'
attention.  As such, not only will this information be shared with 3rd parties,
we will be using smolt as leverage to gain better support for open source
drivers and better support in general.<br>
<br>
IP Logging:  In Fedora's smolt install all web traffic goes through a proxy
server first.  This is the only place IP addresses are being logged and they
are kept on that server for a period of 4 weeks at which time log rotation
removes these logs.  The Fedora Project does not aggregate IP addresses in
the smolt database.  These logs are private and will not be available to the
general public.<br>
<br>
Users unhappy with this policy should simply not use smolt.  Users with
questions about this policy should contact the Fedora Infrastructure Team at
<a href="mailto:%(mail)s">%(mail)s</a>.  Also remember that users can delete their
profiles at any time using<br>
<br>
&nbsp;&nbsp;&nbsp;<tt>smoltDeleteProfile</tt><br>
<br>
Thanks for participating and for your interest in our privacy policy.
""") % {'mail':'admin%sfedoraproject.org' % '@'}
