"""
Tools for creating performance data for Icinga plugin responses.
If you're adding performance data to a :py:class:`~pycinga.response.Response`
object, then :py:func:`~pycinga.response.Response.set_perf_data` can be
called instead of having to create an entire :py:class:`PerfData` object.
"""

import re

from .range import Range


class PerfData(object):
    """
    This class represents performance data for a response. Since
    performance data has a non-trivial response format, this class
    is meant to ease the formation of performance data.
    """

    def __init__(self, label, value, uom=None, warn=None, crit=None,
                 minval=None, maxval=None):
        """Creates a new object representing a single performance data
        item for an Icinga response.

        Performance data is extra key/value data that can be returned
        along with a response. The performance data is not used immediately
        by Icinga itself, but can be extracted by 3rd party tools and can
        often be helpful additional information for system administrators
        to view. The `label` can be any string, but `value` must be a
        numeric value.

        Raises :class:`ValueError` if any of the parameters are invalid.
        The exact nature of the error is in the human readable message
        attribute of the exception.

        :Parameters:
          - `label`: Label for the performance data. This must be a
            string.
          - `value`: Value of the data point. This must be a number whose
            characters are in the class of `[-0-9.]`
          - `uom` (optional): Unit of measure. This must only be `%`, `s`
            for seconds, `c` for continous data, or a unit of bit space
            measurement ("b", "kb", etc.)
          - `warn` (optional): Warning range for this metric.
          - `crit` (optional): Critical range for this metric.
          - `minval` (optional): Minimum value possible for this metric,
            if one exists.
          - `maxval` (optional): Maximum value possible for this metric,
            if one exists.
        """
        self.label = label
        self.value = value
        self.uom = uom
        self.warn = warn
        self.crit = crit
        self.minval = minval
        self.maxval = maxval

    @property
    def value(self):
        """The value of this metric."""
        return self._value

    @value.setter
    def value(self, value):
        if value is None:
            raise ValueError("value must not be None")
        elif not self._is_valid_value(value):
            raise ValueError("value must be in class [-0-9.]")

        self._value = value

    @property
    def warn(self):
        """
        The warning range of this metric. This return value of this
        will always be a :py:class:`~pycinga.range.Range` object, even
        if it was set with a string.
        """
        return self._warn

    @warn.setter
    def warn(self, value):
        if value is not None and not isinstance(value, Range):
            value = Range(value)

        self._warn = value

    @property
    def crit(self):
        """
        The critical range of this metric. This return value of this
        will always be a :py:class:`~pycinga.range.Range` object,
        even if it was set with a string.
        """
        return self._crit

    @crit.setter
    def crit(self, value):
        if value is not None and not isinstance(value, Range):
            value = Range(value)

        self._crit = value

    @property
    def minval(self):
        """
        The minimum value possible for this metric. This doesn't make
        a lot of sense if the `uom` is "%", since that is obviously going
        to be 0, but this will return whatever was set.
        """
        return self._minval

    @minval.setter
    def minval(self, value):
        if not self._is_valid_value(value):
            raise ValueError("minval must be in class [-0-9.]")

        self._minval = value

    @property
    def maxval(self):
        """
        The maximum value possible for this metric. This doesn't make
        a lot of sense if the `uom` is "%", since that is obviously going
        to be 100, but this will return whatever was set.
        """
        return self._maxval

    @maxval.setter
    def maxval(self, value):
        if not self._is_valid_value(value):
            raise ValueError("maxval must be in class [-0-9.]")

        self._maxval = value

    @property
    def uom(self):
        """
        The unit of measure (UOM) for this metric.
        """
        return self._uom

    @uom.setter
    def uom(self, value):
        valids = ["", "s", "%", "b", "kb", "mb", "gb", "tb", "c"]
        if value is not None and not str(value).lower() in valids:
            raise ValueError("uom must be in: %s" % valids)

        self._uom = value

    def __str__(self):
        """
        Returns the proper string format that should be outputted
        in the plugin response string. This format is documented in
        depth in the Icinga developer guidelines, but in general looks
        like this:

            | 'label'=value[UOM];[warn];[crit];[min];[max]

        """
        # Quotify the label
        label = self._quote_if_needed(self.label)

        # Check for None in each and make it empty string if so
        uom = self.uom or ""
        warn = self.warn or ""
        crit = self.crit or ""
        minval = self.minval or ""
        maxval = self.maxval or ""

        # Create the proper format and return it
        return "%s=%s%s;%s;%s;%s;%s" % (label, self.value, uom, warn, crit, minval, maxval)

    def _is_valid_value(self, value):
        """
        Returns boolean noting whether a value is in the proper value
        format which certain values for the performance data must adhere to.
        """
        value_format = re.compile(r"[-0-9.]+$")
        return value is None or value_format.match(str(value))

    def _quote_if_needed(self, value):
        """
        This handles single quoting the label if necessary. The reason that
        this is not done all the time is so that characters can be saved
        since Icinga only reads 80 characters and one line of stdout.
        """
        if "=" in value or " " in value or "'" in value:
            # Quote the string and replace single quotes with double single
            # quotes and return that
            return "'%s'" % value.replace("'", "''")
        else:
            return value
