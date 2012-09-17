User guide
==========

Some installation:

.. code-block:: console

   git clone https://github.com/jluttine/django-sportsteam.git
   cd django-sportsteam
   python manage.py syncdb
   python manage.py collectstatic

Pre-populate the database with some toy data:

.. code-block:: console

   ./load_data.sh

Run the development server:

.. code-block:: console

   ./runserver.sh
