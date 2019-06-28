#############################################################################
# Copyright (C) 2019 Olaf Japp
#
# This file is part of Py2Dart.
#
#  Py2Dart is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Py2Dart is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Py2Dart. If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

import sys
import os

from parser import Parser


_VERSION = "1.0"

def usage():
    print("Py2Dart " + _VERSION)
    print("Usage: py2dart [options] file\n")
    print("Options:")
    print("-h --help      Display this information")
    print("-v --version   Display the program version")
    sys.exit(1)

def version():
    print("Py2Dart " + _VERSION)
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
    if sys.argv[1] == "-h" or sys.argv[1] == "--help":
        usage()
    elif sys.argv[1] == "-v" or sys.argv[1] == "--version":
        version()
    elif sys.argv[1][0] == "-":
        usage()
    else:
        input_file = sys.argv[1]
        if not os.path.exists(input_file):
            print("file '" + input_file + "' does not exist")
            sys.exit(1)
        parser = Parser()
        parser.parse(open(input_file).read())