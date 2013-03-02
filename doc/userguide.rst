User guide
==========

Some installation:

.. code-block:: console

   git clone https://github.com/jluttine/django-sportsteam.git
   cd django-sportsteam
   python manage.py syncdb
   mkdir sportsteam/static
   python manage.py collectstatic

The database is pre-populated from ``initial_data.json``.  Run the
development server:

.. code-block:: console

   ./runserver.sh

.. automodule:: teamstats.views
   :members:

