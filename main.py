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