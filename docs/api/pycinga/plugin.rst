:mod:`plugin` -- Plugin Class
============================================

.. automodule:: pycinga.plugin

   .. autoclass:: pycinga.plugin.Plugin([argv=sys.argv])

      .. attribute:: options

         Dictionary of parsed command line options and their values. As an
         example, to get the ``hostname`` passed in via the command line:::

             options.hostname

      .. attribute:: args

         Array of additional positional arguments passed in via the command
         line. For example, if you call the plugin with ``./plugin 1 2 3``,
         then ``options.args`` will return ``[1,2,3]``.

      .. automethod:: check
      .. automethod:: response_for_value
