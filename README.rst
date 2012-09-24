Django site - Sports team
=========================

Web site for sports teams with Django.

See the documentation in ``docs/`` folder or at
http://django-sportsteam.readthedocs.org/.

Deploying
---------

For development, you can use ``runserver.sh``.  However, development
server doesn't serve some files properly (e.g., video file streaming
doesn't work).  How to deploy?  See
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/modwsgi/.

You should have Apache and ``mod_wsgi`` installed. On Ubuntu::

   sudo aptitude install apache2 libapache2-mod-wsgi

In ``/etc/apache2/httpd.conf``, add, for instance::

   Alias /media/ /path/to/django-sportsteam/sportsteam/media/
   Alias /static/ /path/to/django-sportsteam/sportsteam/sitestatic/

   <Directory /path/to/django-sportsteam/sportsteam/sitestatic>
   Order deny,allow
   Allow from all
   </Directory>

   <Directory /path/to/django-sportsteam/sportsteam/media>
   Order deny,allow
   Allow from all
   </Directory>

   WSGIScriptAlias / /path/to/django-sportsteam/sportsteam/wsgi.py
   WSGIPythonPath /path/to/django-sportsteam

   <Directory /path/to/django-sportsteam/sportsteam>
   <Files wsgi.py>
   Order allow,deny
   Allow from all
   </Files>
   </Directory>


Check that your ``django-sportsteam`` folder, sub-folders and all
parent folders have read-access for apache.


License and copyright
---------------------

An example video ``sportsteam/media/videos/example.mp4`` is licensed
under CC-BY.  The video by JKJFHD44 was downloaded from
http://www.youtube.com/watch?v=kM6eFMkzQIw.

For everything else applies the copyright and license conditions as
described below.

Copyright (C) 2011,2012 Jaakko Luttinen jaakko.luttinen@iki.fi

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with this program.  If not, see
<http://www.gnu.org/licenses/>.

