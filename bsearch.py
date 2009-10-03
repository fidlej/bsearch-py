#!/usr/bin/env python
"""\
Usage: %prog PREFIX [FILE]
Finds lines with the given prefix in the sorted file.
"""

import sys
import optparse

def _parse_args():
    parser = optparse.OptionParser(__doc__)

    options, args = parser.parse_args()
    if len(args) == 0:
        parser.error("Specify a prefix!")
    if len(args) > 2:
        parser.error("Specify one sorted file!")

    return options, args

def main():
    options, args = _parse_args()


if __name__ == "__main__":
    main()
