Tutorial
========

This tutorial will provide an introduction and examples for writing
Icinga plugins using **Pycinga**.

Prerequisites
-------------

Before beginning, make sure that **Pycinga** is :doc:`installed <installation>`.
To verify this, the following should run without raising an exception::

    >>> import pycinga

Since Icinga plug-ins are simply executable applications, Icinga itself is not
required to develop plug-ins.

A Simple Plugin
----------------

All plugins must inherit from the :py:class:`~pycinga.plugin.Plugin` class.
Icinga plug-ins are expected to conform to a standard set of command line
arguments (in addition to any custom arguments that may be added), and the
Pycinga Plugin class already knows how to read and process these arguments.

After inheriting from the class, :py:func:`~pycinga.plugin.Plugin.check`
should be implemented, which should perform whatever check the plugin does,
and return a :py:class:`~pycinga.response.Response` object.

Here is a basic Icinga script::

    import pycinga
    from pycinga import Plugin, Response

    class MyCheck(Plugin):
        def check(self):
            return Response(pycinga.OK, "Everything is ok!")

    if __name__ == "__main__":
        # Instantiate the plugin, check it, and then exit
        MyCheck().check().exit()

Save this to a Python file and run it, and you should see the following
output:

::

    $ python my_check.py
    OK: Everything is ok!

And the exit status will be ``0``, meaning everything is good.

This is the most basic Icinga plug-in that can be created. Now, let's
create one that is more feature-complete.

Returning Proper Responses
--------------------------

In the first example, we simply returned ``pycinga.OK`` on every
check. Realistically, we would get a value and return ``OK``, ``WARNING``,
or ``CRITICAL`` depending on that value. According to the Icinga developer
guidelines, the warning and critical ranges must be able to be set via
the command line via ``-w`` and ``-c``, respectively. **Pycinga** plugins
do this for you automatically, as we shall see in this section.

Let's enhance our check to use a value, and return a proper response status
for that value::

    import pycinga
    from pycinga import Plugin

    class MyCheck(Plugin):
        def check(self):
            # Static for this example, but imagine in a real world plugin
            # that this would be calculated.
            value = 27

            # Return a response for that value
            return self.response_for_value(value)

This check now has some numeric value which we've set to a static ``27``
for the purpose of this example. The important piece is that the plugin
calls :py:func:`~pycinga.plugin.Plugin.response_for_value` to generate
a response based on that value. This method takes into account the warning
and critical ranges set by the plugin and the command line.

Since we didn't set any defaults for the warning and critical range,
we'll find that the check will be ``OK`` by default:

::

    $ python my_check.py
    OK:

By introducing some ranges, we can see that the plugin automatically
works. In this case, 27 is outside of the warning range, but still not
critical. The plugin properly returns ``WARN``:

::

    $ python my_check.py -w 10:20 -c 0:30
    WARN:

And again, if we modify the ranges slightly, we can get the plugin to
consider the value critical:

::

    $ python my_check.py -w 5:10 -c 0:20
    CRIT:

**Note on ranges:** If you're unfamiliar with Icinga ranges, it may not be
clear how exactly they're working. Ranges default to exclusive, meaning
a range of ``10:20`` means that a value is included in this range if the
value is ``< 10 OR > 20``. For more details on Icinga range format, it is
fully documented in the :py:class:`~pycinga.range.Range` documentation.

Adding Performance Data
-----------------------

Icinga plug-ins can also output metrics which are useful for 3rd party
applications and can also be read on the Icinga dashboard. **Pycinga**
provides an easy way to add performance data to responses. Extending our
example once again::

    import pycinga
    from pycinga import Plugin

    class MyCheck(Plugin):
        def check(self):
            # Static for this example, but imagine in a real world plugin
            # that this would be calculated.
            value = 27

            # Return a response for that value
            result = self.response_for_value(value)
            result.set_perf_data("some_key", value)
            result.set_perf_data("zero", 0)
            return result

The :py:func:`~pycinga.response.Response.set_perf_data` function can be used
to set performance data on the response. If we run the check now, we should
see output similar to the following:

::

    $ python my_check.py
    OK:|some_key=27;;;; zero=0;;;;

Note that the extra semicolons are in order to comply with the standard
performance data format and can contain additional information. See
:py:class:`~pycinga.perf_data.PerfData` for more information.

Custom Command-line Options and Arguments
-----------------------------------------

Often checks can require additional command line options. Since **Pycinga**
plugins parse the command line on their own, you should define additional
options on the plugin itself, rather than attempting to use your own command
line parser. **Pycinga** uses Python's built-in ``argparse`` library.

We'll extend our example to add an option to multiply the value by the
given option value:::

    import pycinga
    from pycinga import Plugin, make_option

    class MyCheck(Plugin):
        multiply_by = make_option("--multiply-by", type="int")

        def check(self):
            # Static for this example, but imagine in a real world plugin
            # that this would be calculated.
            value = 27

            # Multiply the value if we were given the flag
            if self.options.multiply_by:
                value = value * self.options.multiply_by

            return self.response_for_value(value, str(value))

We've added the option ``multiply_by``. If we run the check without the
option, we see the normal output:

::

    $ python my_check.py
    OK: 27

But by adding a number to multiply by, we'll get different output:

::

    $ python my_check.py --multiply-by 10
    OK: 270
