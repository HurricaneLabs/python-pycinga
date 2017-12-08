:mod:`pycinga` -- Python Library for Writing Icinga Plugins
============================================================

.. automodule:: pycinga
   :synopsis: Python library for writing Icinga plugins.

   .. autodata:: version
   .. data:: PerfData

     Alias for :class:`pycinga.perf_data.PerfData`

   .. data:: Plugin

     Alias for :class:`pycinga.plugin.Plugin`

   .. data:: Range

     Alias for :class:`pycinga.range.Range`

   .. data:: Response

     Alias for :class:`pycinga.response.Response`

   .. data:: Status

     Alias for :class:`pycinga.status.Status`

   .. data:: OK

     A :class:`~pycinga.status.Status` object representing the OK
     response status.

   .. data:: WARNING

     A :class:`~pycinga.status.Status` object representing the WARNING
     response status.

   .. data:: CRITICAL

     A :class:`~pycinga.status.Status` object representing the CRITICAL
     response status.

   .. data:: UNKNOWN

     A :class:`~pycinga.status.Status` object representing the UNKNOWN
     response status.

Sub-modules:

.. toctree::
   :maxdepth: 2

   perf_data
   plugin
   response
   range
   status
