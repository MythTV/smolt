
Smoon is the server part of smolt. 

This is a TurboGears (http://www.turbogears.org) project. It can be
started by running the start-hardware.py script.

to debug, run the debug-hardware script as:
python -i debug-hardware.py


------------------------
Deployment / Development
------------------------

You will need execute the following commands at the command line from the database directory :

 $ mysql -p -u root
 > CREATE DATABASE smoon;
 > CREATE USER 'smoon'@'smoon' IDENTIFIED BY 'smoon';
 > GRANT ALL ON smoon.* to 'smoon'@'localhost' ;
 > quit
 $ mysql -p -u smoon smoon < smolt.sql

Then go to the smoon directory and edit sample-dev.cfg to your liking.

Then launch smoon from the smoon directory :

 $ python start-hardware.py sample-dev.cfg

A smoon server is now running at http://127.0.0.1:8080/ .


------------
Localization
------------

To do it, follow this link:
http://docs.turbogears.org/1.0/GenshiInternationalizationWithBabel
