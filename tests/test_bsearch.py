#!/usr/bin/env python

import unittest
from StringIO import StringIO

import bsearch

DATA = """\
A first line
AA second line
B next line
Z last line"""


class Test(unittest.TestCase):

    def setUp(self):
        self.stream = StringIO(DATA)
        self.stream_size = len(DATA)

    def test_read_last_line(self):
        self.stream.seek(2)
        self.assertEquals("first line\n", self.stream.readline())

        line = bsearch._read_last_line(self.stream, self.stream_size)
        self.assertEquals("Z last line", line)

    def test_getitem(self):
        items = bsearch._LinesAsBytes(self.stream, self.stream_size)
        self.assertEquals(self.stream_size, len(items))
        self.assertEquals("A first line\n", items[0])
        self.assertEquals("AA second line\n", items[1])
        self.assertEquals("B next line\n", items[DATA.index("B")])
        self.assertEquals("Z last line", items[DATA.index("B") + 1])
        self.assertEquals("Z last line", items[self.stream_size -4])
        self.assertEquals("Z last line", items[self.stream_size -1])

    def test_get_after_empty_line(self):
        data = "\nA line\nB line\n"
        items = bsearch._LinesAsBytes(StringIO(data), len(data))
        self.assertEquals("\n", items[0])
        self.assertEquals("A line\n", items[1])
        self.assertEquals("B line\n", items[2])

    def test_bsearch(self):
        self.assertEquals(["A first line\n", "AA second line\n"],
                bsearch._bsearch_stream(self.stream, self.stream_size, "A"))
        self.assertEquals(["B next line\n"],
                bsearch._bsearch_stream(self.stream, self.stream_size, "B n"))
        self.assertEquals(DATA.splitlines(True),
                bsearch._bsearch_stream(self.stream, self.stream_size, ""))

    def test_bsearch_with_key(self):
        key = lambda x: x.lower()
        data = "\nAA line\nab line\nbb line\n"
        stream = StringIO(data)
        self.assertEquals(["AA line\n", "ab line\n"],
                bsearch._bsearch_stream(stream, len(data), "A", key=key))
