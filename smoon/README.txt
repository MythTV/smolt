hardware

This is a TurboGears (http://www.turbogears.org) project. It can be
started by running the start-hardware.py script.

to debug, run the debug-hardware script as:
python -i debug-hardware.py


------------------------
Deployment / Development
------------------------

This project uses SQLAlchemy-Migrate.  Since it was originally deployed
without it, you cannot just upgrade your DB and have everything in working
condition.  Instead, you have to initialize your DB to match the last working version
before we migrated to Migrate.

Assuming your user is 'smoon', password is 'smoon', and DB is 'smoon', runing on mysql
you will need to execute the following commands at the command line from /smoon

NOTE: In Fedora, Migrate is named sqlalchemy-migrate.  It might be called 'migrate' in
other distributions.

 $ mysql -u smoon -p smoon < smoon.ddl.sql
 $ sqlalchemy-migrate manage manage.py --repository=db --url=mysql://smoon:smoon@localhost/smoon
 $ python manage.py version_control
 $ python manage.py upgrade

NOTE: THE FOLLOWING DOESN'T WORK YET! DON'T DO IT.

If you don't have the mythtv extensions setup, you may receive some warnings when running
the upgrade.  These warnings are harmless.  If you want to installed the mythtv extensions
after upgrading, run the following.

 $ sqlalchemy-migrate manage manage.myth.py --repository=db_myth --url=mysql://smoon:smoon@localhost/smoon
 $ python manage.myth.py upgrade


------------
Localization
------------

To do it, follow this link:
http://docs.turbogears.org/1.0/GenshiInternationalizationWithBabel
