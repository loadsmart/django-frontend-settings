Frontend Settings
=================

Abstract
--------

This project provides an API that expose settings and feature flags for the frontend.

It uses `django-drf` to create an endpoint to expose flags and settings configured in `django-waffle` and `django-constance`



Usage
-----

Requirements
Python (3.10, 3.11, 3.12)
Django (4.1, 4.2)
Django REST Framework (3.13+)

Installation
~~~~~~~~~~~~
Install using pip:

.. code::

    pip install django-frontend-settings

Add 'frontend-settings' to your INSTALLED_APPS setting.

.. code:: python

    INSTALLED_APPS = [
        ...
        'frontend_settings',
    ]

Expose the view in your urls:

.. code:: python

    from django.urls import path
    from frontend_settings.views import settings as frontend_settings_view

    path("frontend-settings/", frontend_settings_view, name="frontend-settings"),


Then your flags from waffle and setting from constance should be returned on a get in this route:


.. code::

    $ curl 'http://localhost:8000/frontend-settings/'
    {"data":{"flags":{"MY_FEATURE_FLAG":true},"settings":{}}}


In that case I had `FRONTEND_MY_FEATURE_FLAG` flag in waffle.
The default prefix for flags is `FRONTEND_`, if you like to change it you can do by changing the following config on settings.py:

.. code:: python

    FRONTEND_SETTINGS = {
        "WAFFLE_FLAG_PREFIX": "FRONTEND_", # Prefix used to filter out the flag that should be exposed in the endpoint
        "CONSTANCE_KEY_PREFIX": "FRONTEND_", # Prefix used to filter out the settings in constance
    }
