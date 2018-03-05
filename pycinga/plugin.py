"""
This module provides the Plugin class, which is the basic
class which encapsulates a single plugin. This is the class
which should be subclassed when creating new plugins.
"""

from argparse import ArgumentError, ArgumentParser
from copy import copy

from six import with_metaclass

from .range import Range, RangeValueError
from .response import Response
from .status import Status

# Status constants which contain both the status text and the
# exit status associated with them.
OK = Status("OK", 0)
WARNING = Status("WARN", 1)
CRITICAL = Status("CRIT", 2)
UNKNOWN = Status("UNKNOWN", 3)


def check_pycinga_range(value):
    """
    This parses and returns the Icinga range value.
    """
    try:
        return Range(value)
    except RangeValueError as e:
        raise ArgumentError("options %s: %s" % (value, e.message))


class PluginMeta(type):
    """
    We use a metaclass to create the plugins in order to gather and
    set up things such as command line arguments.
    """

    def __new__(cls, name, bases, attrs={}):
        attrs = attrs if attrs else {}

        # Set the parents on the plugin by finding all the parsers and
        # setting them.
        parents = []
        attrs_copy = copy(attrs)

        for key, val in attrs_copy.items():
            if isinstance(val, ArgumentParser):
                # We set the destination of the Action to always be the
                # attribute key...
                val.dest = key

                # Append it to the list of options and delete it from
                # the original attributes list
                parents.append(val)
                del attrs[key]

        # Need to iterate through the bases in order to extract the
        # list of parent options, so we can inherit those.
        for base in bases:
            if hasattr(base, "_parents"):
                parents.extend(getattr(base, "_parents"))

        # Store the parent list and create the option parser
        attrs["_parents"] = parents
        attrs["_option_parser"] = ArgumentParser(parents=parents)

        # Create the class
        return super(PluginMeta, cls).__new__(cls, name, bases, attrs)


class Plugin(with_metaclass(PluginMeta, object)):
    """
    Encapsulates a single plugin. This is able to parse the command line
    arguments, understands the range syntax, provides help output, and
    more.
    """

    parser = ArgumentParser(add_help=False)
    parser.add_argument("-H", "--hostname", type=str)
    parser.add_argument("-w", "--warning", type=check_pycinga_range)
    parser.add_argument("-c", "--critical", type=check_pycinga_range)
    parser.add_argument("-t", "--timeout", type=int, default=0)
    parser.add_argument("-v", "--verbosity", action="count")

    # TODO: Still missing version

    responses = []
    _options = None

    @property
    def options(self):
        if self._options is None:
            self._options = self._option_parser.parse_args(self.args)
        return self._options

    def __init__(self, args=None):
        """
        Instantiates a plugin, setting up the options and arguments state.
        Initialization by itself shouldn't do much, since the plugin should run
        when :py:func:`check` is called.

        This init method will parse the arguments given in ``args`` and will
        set the results on the ``options`` attribute. If no ``args`` are given,
        the command line arguments given to the whole Python application will
        be used.

        All plugins parse standard command line arguments that are required
        by the Icinga developer guidelines:

          - ``hostname`` - Set via ``-H`` or ``--hostname``, this should be the
            host that this check targets, if applicable.
          - ``warning`` - Set via ``-w`` or ``--warning``, this should be a valid
            range in which the value of the plugin is considered to be a warning.
          - ``critical`` - Set via ``-c`` or ``--critical``, this should be a
            valid range in which the value is considered to be critical.
          - ``timeout`` - Set via ``-t`` or ``--timeout``, this is an int value
            for the timeout of this check.
          - ``verbosity`` - Set via ``-v``, where additional ``v`` means more
            verbosity. Example: ``-vvv`` will set ``options.verbosity`` to 3.

        Subclasses can define additional options by creating ``Action`` instances
        and assigning them to class attributes. The easiest way to make an
        ``Action`` is to use Python's built-in ``argparse`` methods. The following
        is an example plugin which adds a simple string argument:::

            class MyPlugin(Plugin):
                parser = ArgumentParser()
                parser.add_argument("--your-name", dest="your_name", type="string")

        Instantiating the above plugin will result in the value of the new
        argument being available in ``options.your_name``.
        """
        # Parse the given arguments to set the options
        self.args = args

    def check(self):
        """
        This method is what should be called to run this plugin and return
        a proper :py:class:`~pycinga.response.Response` object. Subclasses
        are expected to implement this.
        """
        raise NotImplementedError("This method must be implemented by the plugin.")

    def response_for_value(self, value, message=None):
        """
        This method is meant to be used by plugin implementers to return a
        valid :py:class:`~pycinga.response.Response` object for the given value.
        The status of this response is determined based on the warning and
        critical ranges given via the command line, which the plugin automatically
        parses.

        An optional ``message`` argument may be provided to set the message
        for the Response object. Note that this can easily be added later as well
        by simply setting the message attribute on the response object returned.

        Creating a response using this method from :py:func:`check` makes it
        trivial to calculate the value, grab a response, set some performance
        metrics, and return it.
        """
        status = OK
        if getattr(self.options, "critical", None) and self.options.critical.in_range(value):
            status = CRITICAL
        elif getattr(self.options, "warning", None) and self.options.warning.in_range(value):
            status = WARNING

        return Response(status, message=message)

    def add_response(self, response):
        """
        Add a Response object to be collated by all_responses
        """
        self.responses.append(response)

    def all_responses(self, default=None):
        """
        Collate all Response objects added with add_response.  Return
        a Response object with worst Status of the group and a message
        consisting of the groups messages grouped and prefixed by their
        status.

        e.g. Response(worstStatus, "A, C WARN: K, L OK: X, Y, Z")

        If no responses have been added, return the Response passed
        in as default, or if default is None return pycinga.OK
        """
        if not self.responses:
            if default:
                return default
            else:
                return Response(OK)

        self.responses.sort(reverse=True, key=lambda k: k.status)

        worst = self.responses[0]
        status = worst.status
        message = worst.message

        laststatus = status

        for resp in self.responses[1:]:
            if laststatus is not resp.status:
                message += " " + resp.status.name + ": " + resp.message
                laststatus = resp.status
            else:
                message += ", " + resp.message

        return Response(status, message)
