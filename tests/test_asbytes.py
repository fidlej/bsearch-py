#!/usr/bin/env python

import unittest
from StringIO import StringIO

import bsearch

DATA = """\
a first line
aa second line
b next line
z last line"""

class Test(unittest.TestCase):
    def setUp(self):
        self.stream = StringIO(DATA)
        self.stream_size = len(DATA)

    def test_read_last_line(self):
        self.stream.seek(2)
        self.assertEquals("first line\n", self.stream.readline())

        line = bsearch._read_last_line(self.stream, self.stream_size)
        self.assertEquals("z last line", line)


if __name__ == "__main__":
    unittest.main()

