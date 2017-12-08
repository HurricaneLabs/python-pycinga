"""
Contains tests for pycinga.response.PerfData
"""

import pytest

from pycinga.perf_data import PerfData
from pycinga.range import Range


class TestPerfData(object):

    def test_exception_if_value_invalid(self):
        """
        Tests to verify that an exception is raised if value
        is an invalid format.
        """
        with pytest.raises(ValueError):
            PerfData("foo", "bar")

    def test_exception_if_minval_invalid(self):
        """
        Tests to verify that an exception is raised if minval
        is an invalid format.
        """
        with pytest.raises(ValueError):
            PerfData("foo", "7", minval="foo")

    def test_exception_if_maxval_invalid(self):
        """
        Tests to verify that an exception is raised if maxval
        is an invalid format.
        """
        with pytest.raises(ValueError):
            PerfData("foo", "7", maxval="foo")

    def test_exception_if_invalid_uom(self):
        """
        Tests to verify that an exception is raised if the
        unit of measure is an invalid format.
        """
        invalids = ["p", "bytes", "nope"]
        for value in invalids:
            with pytest.raises(ValueError):
                PerfData("foo", "7", uom=value)

    def test_setting_valid_uom(self):
        """
        Tests to verify that an exception is not raised if the
        unit of measure is a valid format.
        """
        valids = [None, "", "s", "%", "B", "KB", "MB", "GB", "TB", "c"]
        for value in valids:
            PerfData("foo", "7", uom=value)

    def test_invalid_warn_range(self):
        """
        Tests to verify that an exception is raised if the warning
        range is invalid.
        """
        with pytest.raises(ValueError):
            PerfData("foo", "7", warn="boo")

    def test_invalid_crit_range(self):
        """
        Tests to verify that an exception is raised if the crit
        range is invalid.
        """
        with pytest.raises(ValueError):
            PerfData("foo", "7", crit="boo")

    def test_valid_warn_range_as_string(self):
        """
        Tests to verify that warnings are converted to range
        object if a string is given.
        """
        instance = PerfData("foo", "7", warn="10:20")
        assert isinstance(instance.warn, Range)
        assert 10.0 == instance.warn.start
        assert 20.0 == instance.warn.end

    def test_valid_crit_range_as_string(self):
        """
        Tests to verify that crit range is converted to range
        object if a string is given.
        """
        instance = PerfData("foo", "7", crit="10:20")
        assert isinstance(instance.crit, Range)
        assert 10.0 == instance.crit.start
        assert 20.0 == instance.crit.end

    def test_valid_warn_range_as_range(self):
        """
        Tests to verify that warning range can be set to range object.
        """
        value = Range("10:20")
        instance = PerfData("foo", "7", warn=value)
        assert value == instance.warn

    def test_valid_crit_range_as_range(self):
        """
        Tests to verify that crit range can be set to range object.
        """
        value = Range("10:20")
        instance = PerfData("foo", "7", crit=value)
        assert value == instance.crit

    def test_valid_string(self):
        """
        Tests to verify that a valid string representation is
        returned for a basic case of only having a label and
        value.
        """
        instance = PerfData("foo", "7")
        assert "foo=7;;;;" == str(instance)

    def test_quote_label(self):
        """
        Tests to verify that the label is quoted if it needs to be.
        """
        instance = PerfData("with=", "7")
        assert "'with='=7;;;;" == str(instance)

        instance = PerfData("I have spaces", "7")
        assert "'I have spaces'=7;;;;" == str(instance)

        instance = PerfData("quote'", "7")
        assert "'quote'''=7;;;;" == str(instance)

    def test_include_other_values(self):
        """
        Tests to verify that uom, warn, crit, etc. are properly
        included in the output.
        """
        instance = PerfData("foo", "1", uom="b", warn="10:20", crit="20:30",
                            minval="1", maxval="5")
        assert "foo=1b;10:20;20:30;1;5" == str(instance)
