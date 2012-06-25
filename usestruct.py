import sys
from dumpstruct import dumpstruct
from pprint import pprint

pprint(sys.argv)
print dumpstruct(sys.argv[1:]).start()
