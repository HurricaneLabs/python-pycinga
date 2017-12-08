"""
Contains tests for the pycinga.Response class.
"""

import sys
from io import BytesIO, StringIO

import pycinga
from pycinga import Response


class TestResponse(object):

    def test_status_gets_set_by_initializer(self):
        "Tests that the status can be set by the constructor."
        instance = Response(pycinga.OK)
        assert pycinga.OK == instance.status

    def test_message_gets_set_by_initializer(self):
        "Tests that the message can be set by the constructor."
        instance = Response(message="Hello!")
        assert "Hello!" == instance.message

    def test_str_has_blank_message(self):
        """
        Tests that a response with no message given will not include
        anything in the output.
        """
        instance = Response(pycinga.OK)
        expected = "%s:" % pycinga.OK.name
        assert expected == str(instance)

    def test_str_has_status_and_message(self):
        """
        Tests that without performance data, the status output
        will output the proper thing with status and a message.
        """
        instance = Response(pycinga.OK, message="Hi")
        expected = "%s: %s" % (pycinga.OK.name, "Hi")
        assert expected == str(instance)

    def test_str_has_performance_data(self):
        """
        Tests that with performance data, the status output
        will output the value along with the performance data.
        """
        instance = Response(pycinga.OK, message="yo")
        instance.set_perf_data("users", 20)
        instance.set_perf_data("foos", 80)
        expected = "%s: %s|users=20;;;; foos=80;;;;" % (pycinga.OK.name, "yo")
        assert expected == str(instance)

    def test_exit(self, monkeypatch):
        """
        Tests that responses exit with the proper exit code and
        stdout output.
        """
        def mock_exit(code):
            mock_exit.exit_status = code

        mock_exit.exit_status = None

        if sys.version_info[0] == 3:
            output = StringIO()
        else:
            output = BytesIO()
        monkeypatch.setattr(sys, "stdout", output)
        monkeypatch.setattr(sys, "exit", mock_exit)

        instance = Response(pycinga.OK)
        instance.exit()

        assert pycinga.OK.exit_code == mock_exit.exit_status
        assert "%s\n" % str(instance).encode() == output.getvalue()
