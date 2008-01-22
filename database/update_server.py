from urlgrabber import grabber

for x in xrange(240):
    print "doing iteration %s" % x
    grabber.urlgrab('http://localhost:8080/upgrade/upgrade')
