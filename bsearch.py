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

    options, args = parser.parse_args()
    if len(args) != 2:
        parser.error("Specify a sorted file and a prefix!")

    return options, args

def bsearch(filename, prefix):
    stream_size = os.path.getsize(filename)
    with open(filename, "rb") as stream:
        return _bsearch_stream(stream, stream_size, prefix)

def _bsearch_stream(stream, stream_size, prefix):
    items = _LinesAsBytes(stream, stream_size)
    index = bisect.bisect_left(items, prefix)

    results = []
    line = items[index]
    while line and line.startswith(prefix):
        results.append(line)
        line = stream.readline()

    return results


class _LinesAsBytes(object):
    """Maps byte indices to the file lines.
    The same line could be returned from many positions.
    The order of the lines is preserved
    and every line is accessible by an index.
    """
    def __init__(self, stream, stream_size):
        self.stream = stream
        self.len = stream_size

    def __getitem__(self, pos):
        """Returns the first line after the position.
        When the position is zero, the first line is returned.
        When the position is from the last line, the last line is returned.

        The seek is moved after the read line.
        """
        assert pos >= 0
        self.stream.seek(pos)
        if pos > 0:
            uncomplete = self.stream.readline()

        line = self.stream.readline()
        if not line:
            line = _read_last_line(self.stream, self.len)

        return line

    def __len__(self):
        return self.len

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

def main():
    options, args = _parse_args()
    filename, prefix = args
    lines = bsearch(filename, prefix)
    for line in lines:
        print line,

if __name__ == "__main__":
    main()
