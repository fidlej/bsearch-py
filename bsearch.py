#!/usr/bin/env python
"""\
Usage: %prog SORTED_FILE PREFIX
Finds lines with the given prefix in the sorted file.
"""

from __future__ import with_statement

import optparse
import os.path
import bisect

def _parse_args():
    parser = optparse.OptionParser(__doc__)
    parser.add_option("-i", "--ignore-case", action="store_true",
            help="ignore case distinctions")

    options, args = parser.parse_args()
    if len(args) != 2:
        parser.error("Specify a sorted file and a prefix!")

    return options, args

def bsearch(filename, prefix, key=None):
    """Finds all lines that starts with the prefix.
    The given file should be already sorted.
    """
    stream_size = os.path.getsize(filename)
    with open(filename, "rb") as stream:
        return _bsearch_stream(stream, stream_size, prefix, key=key)

def _bsearch_stream(stream, stream_size, prefix, key=None):
    if key is None:
        key = lambda x: x
    prefix = key(prefix)
    items = _LinesAsBytes(stream, stream_size, key=key)
    index = bisect.bisect_left(items, prefix)

    results = []
    line = items.get_raw(index)
    # Empty prefix is also supported
    while line and key(line).startswith(prefix):
        results.append(line)
        line = stream.readline()

    return results


class _LinesAsBytes(object):
    """Maps byte indices to the file lines.
    The same line could be returned from many positions.
    The order of the lines is preserved
    and every line is accessible by an index.
    """
    NUM_FIRST_LINE_INDICES = 1

    def __init__(self, stream, stream_size, key=None):
        if key is None:
            key = lambda x: x
        self.stream = stream
        self.stream_size = stream_size
        self.key = key

    def __getitem__(self, pos):
        """Returns the first line after the position.
        When the position is zero, the first line is returned.
        When the position is from the last line, the last line is returned.

        The seek is moved after the read line.
        """
        return self.key(self.get_raw(pos))

    def get_raw(self, pos):
        """Returns the unconverted line for the given position.
        It returns empty line when end-of-file was reached.
        """
        assert pos >= 0
        pos -= self.NUM_FIRST_LINE_INDICES
        if pos < 0:
            self.stream.seek(0)
            return self.stream.readline()

        self.stream.seek(pos)
        uncomplete = self.stream.readline()
        line = self.stream.readline()
        if not line:
            line = _read_last_line(self.stream, self.stream_size)

        return line

    def __len__(self):
        return self.stream_size + self.NUM_FIRST_LINE_INDICES

def _read_last_line(stream, stream_size):
    bufsize = 8192
    # Read by big steps and also from 0.
    for pos in xrange(stream_size - bufsize, -2 * bufsize, -2 * bufsize):
        pos = max(0, pos)
        stream.seek(pos)
        data = stream.read(bufsize)
        index = data.rfind("\n")
        if index != -1:
            stream.seek(pos + index + 1)
            return stream.readline()

    stream.seek(0)
    return stream.readline()

def _define_key(options):
    """Returns a function that exctracts the key from a compared string.
    Returns None when no special comparison is required.
    """
    if options.ignore_case:
        return lambda x: x.lower()
    return None

def main():
    options, args = _parse_args()
    filename, prefix = args
    key = _define_key(options)
    lines = bsearch(filename, prefix, key=key)
    for line in lines:
        print line,

if __name__ == "__main__":
    main()
