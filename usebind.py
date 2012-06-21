import sys
from pprint import pprint
from bind2 import bind

b = bind(sys.argv[1])
pprint(b.start())
