"""
Contains a class to represent a range that adheres to the range
format defined by Icinga.
"""


class RangeValueError(ValueError):
    """
    This exception is raised when an invalid value is passed to
    :py:class:`Range`. The message of this exception will contain a
    human readable explanation of the error.
    """
    pass


class Range(object):
    """
    Encapsulates an Icinga range value. This is the value which would
    be passed to command line arguments involving ranges. Examples
    of ranges:

      10 - < 0 OR > 10
      10:20 - < 10 OR > 20
      @10:20 - >= 10 AND <= 20
      ~:10 - > 10 (~ = -inf)
      10:~ - < 10

    """

    def __init__(self, value):
        """
        Initializes an Icinga range with the given value. The value should be
        in the Icinga range format, which is the following:

        ::

          [@]start:end

        Notes:

          - ``start`` must be less than or equal to ``end``
          - Ranges by default are exclusive. A range of ``10:20`` will match values
            that are ``< 10 OR >20``.
          - ``@`` means the range is `inclusive`. So ``@10:20`` is valid in the
            case that the value is ``>= 10 AND <= 20``.
          - If ``start`` or ``end`` is ``~``, this value is negative or positive
            inifinity, respectively. A range of ``~:20`` will match values that
            are ``> 20`` only.
          - If ``start`` is not given, then it is assumed to be 0.
          - If ``end`` is not given, but a ``:`` exists, then ``end`` is assumed
            to be infinity. Example: ``5:`` would match ``< 5``.
        """
        # Clean up the value by clearing whitespace. Also note that an empty
        # value is invalid.
        value = value.strip()
        if len(value) == 0:
            raise RangeValueError("Range must not be empty")

        # Test for the inclusivity marked by the "@" symbol at the beginning
        if value.startswith("@"):
            self.inclusive = True
            value = value[1:]
        else:
            self.inclusive = False

        # Split by the ":" character to get the start/end parts.
        parts = value.split(":")
        if len(parts) > 2:
            raise RangeValueError("Range cannot have more than two parts.")
        if len(parts) == 1:
            parts.insert(0, "0")

        # Parse the start value. If no ":" is included in value (e.g. "10")
        # then the start is assumed to be 0. Otherwise, it is an integer
        # value which can possibly be infinity.
        try:
            if parts[0] == "~":
                start = float("-inf")
            else:
                start = float(parts[0])
        except ValueError:
            raise RangeValueError("invalid start value: %s" % parts[0])

        # Parse the end value, which can be positive infinity.
        try:
            if parts[1] == "" or parts[1] == "~":
                end = float("inf")
            else:
                end = float(parts[1])
        except ValueError:
            raise RangeValueError("invalid end value: %s" % parts[1])

        # The start must be less than the end
        if start > end:
            raise RangeValueError("start must be less than or equal to end")

        # Set the instance variables
        self.start = start
        self.end = end

    def in_range(self, value):
        """
        Tests whether ``value`` is in this range.
        """
        if self.inclusive:
            return value >= self.start and value <= self.end
        else:
            return value < self.start or value > self.end

    def __str__(self):
        """
        Turns this range object back into a valid range string which can
        be passed to another plugin or used for debug output. The string returned
        from here should generally be equivalent to the value given to the
        constructor, but sometimes it can be slightly different. However,
        it will always be functionally equivalent.

        Examples:

        ::

          >> str(Range("@10:20")) == "@10:20"
          >> str(Range("10")) == "10"
          >> str(Range("10:")) == "10:~"
        """
        result = "@" if self.inclusive else ""

        # Setup some proxy variables since typing `self` all the time is tiring
        start = self.start
        end = self.end

        # Only put start in the result if it is not equal to 0, since
        # it can otherwise be omitted
        if start == float("-inf"):
            result += "~:"
        elif start != 0.0:
            value = int(start) if start.is_integer() else start
            result += str(value) + ":"

        # Append the end value next
        if end == float("inf"):
            result += "~"
        else:
            value = int(end) if end.is_integer() else end
            result += str(value)

        return result
