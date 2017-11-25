# Copyright (C) 2016 Jaakko Luttinen

import versioneer

NAME         = 'sportsteam'
DESCRIPTION  = 'Django website for a sports team'
AUTHOR       = 'Jaakko Luttinen'
AUTHOR_EMAIL = 'jaakko.luttinen@iki.fi'
URL          = 'https://github.com/jluttine/django-sportsteam'
LICENSE      = 'AGPLv3'
VERSION      = versioneer.get_version()
COPYRIGHT    = '2011-2016, Jaakko Luttinen'


if __name__ == "__main__":

    import os
    import sys

    # Utility function to read the README file.
    # Used for the long_description.  It's nice, because now 1) we have a top level
    # README file and 2) it's easier to type in the README file than to put a raw
    # string in below ...
    def read(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

    from setuptools import setup, find_packages

    setup(
        install_requires = [
            'django>=1.9.0',
            'icalendar',
        ],
        extras_require = {
            'doc': [
                'sphinx',
            ],
            'dev': [
                'django_extensions',
                'ipython',
            ]
        },
        packages             = find_packages(),
        package_data         = {
            '': [
                "templates/*",
            ],
        },
        include_package_data = True,
        name                 = NAME,
        version              = VERSION,
        author               = AUTHOR,
        author_email         = AUTHOR_EMAIL,
        description          = DESCRIPTION,
        license              = LICENSE,
        url                  = URL,
        long_description     = read('README.rst'),
        classifiers          = [
            'Programming Language :: Python :: 3 :: Only',
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: GNU Affero General Public License v3',
            'Operating System :: OS Independent',
            'Framework :: Django',
        ],
    )
