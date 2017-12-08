"""
Contains tests to test the Range class, which is responsible for
parsing and storing the values of an Icinga range format.
"""

import pytest

from pycinga.range import Range, RangeValueError


class TestRangeParsing(object):

    def test_range_with_empty(self):
        """
        Tests empty ranges should throw an error.
        """
        with pytest.raises(RangeValueError):
            Range("")

    def test_range_with_too_many_values(self):
        """
        Tests ranges with too many values throws an error.
        """
        with pytest.raises(RangeValueError):
            Range("10:20:30")

    def test_range_with_empty_start(self):
        """
        Tests ranges with an empty start value.
        """
        with pytest.raises(RangeValueError):
            Range(":10")

    def test_range_with_bad_start(self):
        """
        Tests ranges with a bad start value are invalid.
        """
        with pytest.raises(RangeValueError):
            Range("bad:10")

    def test_range_with_bad_end(self):
        """
        Tests ranges with a bad end value are invalid.
        """
        with pytest.raises(RangeValueError):
            Range("10:bad")

    def test_range_with_only_beginning(self):
        """
        Tests ranges with only a beginning are parsed properly.
        """
        instance = Range("10:")
        assert 10.0 == instance.start
        assert float("inf") == instance.end

    def test_range_with_only_end(self):
        """
        Tests ranges with only an end value, such as "10"
        """
        instance = Range("10")
        assert 0.0 == instance.start
        assert 10.0 == instance.end
        assert not instance.inclusive

    def test_range_with_both(self):
        """
        Tests ranges with a valid float for start and end and
        ensures they are valid.
        """
        instance = Range("10:20")
        assert 10.0 == instance.start
        assert 20.0 == instance.end
        assert not instance.inclusive

    def test_range_with_negative_inf(self):
        """
        Tests that negative infinity is valid for start.
        """
        instance = Range("~:20")
        assert float("-inf") == instance.start
        assert 20.0 == instance.end
        assert not instance.inclusive

    def test_range_with_positive_inf(self):
        """
        Tests that positive infinity is a valid end.
        """
        instance = Range("10:~")
        assert 10.0 == instance.start
        assert float("inf") == instance.end
        assert not instance.inclusive

    def test_range_with_end_smaller_than_start(self):
        """
        Tests that ranges which have an end larger than the start
        are invalid.
        """
        with pytest.raises(RangeValueError):
            Range("20:10")

    def test_range_with_equal_start_and_small(self):
        """
        Tests that the start and end can be equal.
        """
        instance = Range("10:10")
        assert 10.0 == instance.start
        assert 10.0 == instance.end
        assert not instance.inclusive

    def test_range_with_inclusive(self):
        """
        Tests that a range can be inclusive.
        """
        instance = Range("@10:20")
        assert 10.0 == instance.start
        assert 20.0 == instance.end
        assert instance.inclusive


class TestRangeChecking(object):

    def test_in_range_inclusive_equal_to_start(self):
        """
        Tests that on inclusive ranges, values that are equal to
        the start are valid.
        """
        instance = Range("@10:20")
        assert instance.in_range(10)

    def test_in_range_inclusive_equal_to_end(self):
        """
        Tests that on inclusive ranges, values that are equal to
        the end are valid.
        """
        instance = Range("@10:20")
        assert instance.in_range(20)

    def test_in_range_inclusive(self):
        """
        Tests that on inclusive ranges, values that are in the range
        are valid.
        """
        instance = Range("@10:20")
        assert instance.in_range(15)

    def test_in_range_exclusive_equal_to_start_invalid(self):
        """
        Tests that exclusive ranges do not count the start value.
        """
        instance = Range("10:20")
        assert not instance.in_range(10)

    def test_in_range_exclusive_equal_to_end_invalid(self):
        """
        Tests that exclusive ranges do not count the end value.
        """
        instance = Range("10:20")
        assert not instance.in_range(20)

    def test_in_range_below_valid(self):
        """
        Tests that values outside the lower end of the range are valid.
        """
        instance = Range("10:20")
        assert instance.in_range(9)

    def test_in_range_above_valid(self):
        """
        Tests that values outside the upper end of the range are valid.
        """
        instance = Range("10:20")
        assert instance.in_range(21)

    def test_range_as_string(self):
        """
        Tests that the range can be converted back to a valid string
        format.
        """
        tests = ["10", "10:20", "20", "~:10", "@10:15", "@~:~", "10:~"]
        for test in tests:
            assert test == str(Range(test))
