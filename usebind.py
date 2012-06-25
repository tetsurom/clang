import sys
from pprint import pprint
from dumpfunction import dumpfunction

b = dumpfunction(sys.argv[1:])
b.start()
pprint(b.type_map)
