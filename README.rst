Pycinga |Docs| |Build Status| |codecov.io|
==========================================

Pycinga is a simple Python library meant to make writing
`Icinga <http://www.icinga.com/>`_ plugins much easier. Icinga
plugins have `quite a few guidelines <https://www.monitoring-plugins.org/doc/guidelines.html>`_
to adhere to, and Pycinga provides helpers to make this
easy.

Install
-------

To install, simply use ``pip`` or ``easy_install``::

    pip install pycinga

Documentation
-------------

Documentation for the latest version can always be found at
`http://pycinga.readthedocs.io/en/latest <http://pycinga.readthedocs.io/en/latest>`_.

Features
--------

The core features supported by Pycinga:

- Parsing command line arguments such that the standard expected
  arguments (such as ``-H``, ``-w``, ``-c``) are accepted.
- Returning proper POSIX exit code based on status.
- Parsing Icinga range formats (such as "@10:20", "~:50", "10", etc.)
- Outputting status and message.
- Outputting performance data.

Example
-------

What all these features result in is a concise, simple, and
guidelines-compliant Python-based Icinga plugin::

    from pycinga import Plugin

    class UserCheck(Plugin):
        """
        Icinga plugin to check how many users are logged into this
        machine.
        """

        def check(self):
            # Get the number of logged in users, for now we hardcode
            users = 27

            # Build a response and exit. This `response_for_value` automatically
            # creates a response with the proper status given the value and the
            # warning/critical ranges passed in via the command line.
            response = self.response_for_value(users, "%d users" % users)
            response.set_perf_data("users", users)
            response.set_perf_data("another metric", 27, "MB")
            return response

    if __name__ == '__main__':
        # Build the plugin instance and run it. This will also parse
        # command line arguments by default.
        UserCheck().check().exit()

While the above example subclasses ``Plugin``, you're of course welcome
to simply call `Plugin`s methods directly and build a ``Response``
yourself.


.. |Docs| image:: https://readthedocs.org/projects/pycinga/badge/?version=latest
    :target: http://pycinga.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. |Build Status| image:: https://travis-ci.org/HurricaneLabs/python-pycinga.svg?branch=master
    :target: https://travis-ci.org/HurricaneLabs/python-pycinga
.. |codecov.io| image:: https://codecov.io/gh/HurricaneLabs/python-pycinga/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/HurricaneLabs/python-pycinga
