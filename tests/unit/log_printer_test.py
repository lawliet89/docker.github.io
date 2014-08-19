from __future__ import absolute_import
from __future__ import unicode_literals

import os

import six

from .. import unittest
from compose.cli.log_printer import LogPrinter


class LogPrinterTest(unittest.TestCase):
    def get_default_output(self, monochrome=False):
        def reader(*args, **kwargs):
            yield "hello\nworld"

        container = MockContainer(reader)
        output = run_log_printer([container], monochrome=monochrome)
        return output

    def test_single_container(self):
        output = self.get_default_output()

        self.assertIn('hello', output)
        self.assertIn('world', output)

    def test_monochrome(self):
        output = self.get_default_output(monochrome=True)
        self.assertNotIn('\033[', output)

    def test_polychrome(self):
        output = self.get_default_output()
        self.assertIn('\033[', output)

    @unittest.skipIf(six.PY3, "Only test unicode in python2")
    def test_unicode(self):
        glyph = u'\u2022'

        def reader(*args, **kwargs):
            yield glyph + '\n'

        container = MockContainer(reader)
        output = run_log_printer([container])

        self.assertIn(glyph, output.decode('utf-8'))


def run_log_printer(containers, monochrome=False):
    r, w = os.pipe()
    reader, writer = os.fdopen(r, 'r'), os.fdopen(w, 'w')
    printer = LogPrinter(containers, output=writer, monochrome=monochrome)
    printer.run()
    writer.close()
    return reader.read()


class MockContainer(object):
    def __init__(self, reader):
        self._reader = reader

    @property
    def name(self):
        return 'myapp_web_1'

    @property
    def name_without_project(self):
        return 'web_1'

    def attach(self, *args, **kwargs):
        return self._reader()

    def wait(self, *args, **kwargs):
        return 0
