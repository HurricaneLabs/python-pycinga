"""
Contains tests to test the Plugin class.
"""

import sys
from argparse import ArgumentError, ArgumentParser

import pytest

import pycinga  # NOQA: I100
from pycinga import Plugin, Range, Response


class TestPlugin(object):
    Klass = Plugin

    def test_child_plugin_inherits_parent_options(self):
        """
        Tests that subclasses of Plugin inherit the options from
        the parent class.
        """
        class MyChild(Plugin):
            pass

        plugin = MyChild(["-H", "foo.com"])
        assert "foo.com" == plugin.options.hostname

    def test_conflicting_options_explode(self):
        """
        Tests that conflicting options will raise an exception.
        """
        with pytest.raises(ArgumentError):
            class MyChild(Plugin):
                parser = ArgumentParser(add_help=False)
                parser.add_argument("-H", type=str)

    def test_plugin_parses_sys_argv(self, monkeypatch):
        """
        Tests that plugins by default parse the passed in
        arguments.
        """
        # Update the argv in-place since the default arguments
        # are evaluated at "compile" time of Python
        if len(sys.argv) > 1:
            del sys.argv[1:]
        sys.argv.extend(["-H", "foo.com"])

        plugin = self.Klass()
        assert "foo.com" == plugin.options.hostname

    def test_plugin_parses_hostname(self):
        """
        Tests that plugins properly parse the hostname option.
        """
        plugin = self.Klass(["-H", "foo.com"])
        assert "foo.com" == plugin.options.hostname

    def test_plugin_parses_warning_range(self):
        """
        Tests that plugins can properly parse warning ranges from
        the command line via the "-w" option.
        """
        plugin = self.Klass(["-w", "10:20"])
        assert isinstance(plugin.options.warning, Range)
        assert 10.0 == plugin.options.warning.start
        assert 20.0 == plugin.options.warning.end

    def test_plugin_parses_critical_range(self):
        """
        Tests that plugins can properly parse critical ranges
        from the command line via the "-c" option.
        """
        plugin = self.Klass(["-c", "10:20"])
        assert isinstance(plugin.options.critical, Range)

    def test_plugin_parses_timeout(self):
        """
        Tests that plugins can properly parse timeout
        from the command line via the "-t" option.
        """
        plugin = self.Klass(["-t", "17"])
        assert 17 == plugin.options.timeout

    def test_plugin_parses_verbosity(self):
        """
        Tests that plugins can properly parse verbosity.
        """
        plugin = self.Klass(["-v"])
        assert 1 == plugin.options.verbosity

        plugin = self.Klass(["-vv"])
        assert 2 == plugin.options.verbosity

        plugin = self.Klass(["-vvv"])
        assert 3 == plugin.options.verbosity

    def test_plugin_errors_on_check(self):
        """
        Tests that the base plugin throws an exception for check
        since it is not implemented.
        """
        with pytest.raises(NotImplementedError):
            Plugin([]).check()

    def test_plugin_can_return_response_for_value(self):
        """
        Tests that the plugin can return a proper response for the given
        value.
        """
        plugin = self.Klass(["-w", "10:20", "-c", "0:40"])
        assert pycinga.OK == plugin.response_for_value(15).status
        assert pycinga.WARNING == plugin.response_for_value(27).status
        assert pycinga.CRITICAL == plugin.response_for_value(50).status

    def test_plugin_can_set_message_on_response_for_value(self):
        """
        Tests that plugins can set a message when getting a response for
        a given value.
        """
        plugin = self.Klass(["-w", "10:20", "-c", "0:40"])
        assert "foo!" == plugin.response_for_value(15, "foo!").message

    def test_warning_is_optional(self):
        """
        Tests that if warning and critical are not set on the command line
        then the response is OK.
        """
        plugin = self.Klass([])
        assert pycinga.OK == plugin.response_for_value(15).status

    def test_multiple_responses_default(self):
        """
        Test that the default parameter to all_responses is working
        """

        plugin = self.Klass()
        assert pycinga.OK == plugin.all_responses().status

        r1 = Response(pycinga.UNKNOWN, "default test")
        assert r1.status == plugin.all_responses(r1).status
        assert r1.message == plugin.all_responses(r1).message

    def test_multiple_responses(self):
        """
        Test that the add_response and all_responses mechanism is working
        """
        plugin = self.Klass()
        r1 = Response(pycinga.OK, "foo")
        r2 = Response(pycinga.CRITICAL, "bar")
        r3 = Response(pycinga.OK, "baz")
        plugin.add_response(r1)
        plugin.add_response(r2)
        plugin.add_response(r3)
        assert pycinga.CRITICAL == plugin.all_responses().status
        assert "bar OK: foo, baz" == plugin.all_responses().message
