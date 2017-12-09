"""
This module provides the Status class, which encapsulates
a status code for Icinga.
"""


class Status(object):
    """
    Encapsulates an Icinga status, which holds a name and
    an exit code.
    """

    def __init__(self, name, exit_code):
        """
        Creates a new status object for Icinga with the given name and
        exit code.

        **Note**: In general, this should never be called since the standard
        statuses are exported from ``pycinga``.
        """

        if not isinstance(exit_code, int):
            raise ValueError("exit_code must be an int, not %s" % type(exit_code))
        if not isinstance(name, str):
            raise ValueError("name must be a str, not %s" % type(exit_code))

        self.name = name
        self.exit_code = exit_code

    def __repr__(self):
        return "Status(name=%s, exit_code=%d)" % (repr(self.name), self.exit_code)

    def __lt__(self, other):
        return (self.exit_code < other.exit_code)

    def __eq__(self, other):
        return (self.exit_code == other.exit_code)

    def __ne__(self, other):
        return (self.exit_code != other.exit_code)

    def __gt__(self, other):
        return (self.exit_code > other.exit_code)
