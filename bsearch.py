#!/usr/bin/env python
"""\
Usage: %prog PREFIX FILE
Finds lines with the given prefix in the sorted file.
"""

from __future__ import with_statement

import optparse
import os.path
import bisect

def _parse_args():
    parser = optparse.OptionParser(__doc__)

    options, args = parser.parse_args()
    if len(args) == 0:
        parser.error("Specify a prefix!")
    if len(args) != 2:
        parser.error("Specify one sorted file!")

    return options, args

def bsearch(prefix, filename):
    stream_size = os.path.getsize(filename)
    with open(filename, "rb") as stream:
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
    for pos in xrange(stream_size - bufsize, 0, -2 * bufsize):
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
    prefix, filename = args
    lines = bsearch(prefix, filename)
    for line in lines:
        print line,

if __name__ == "__main__":
    main()