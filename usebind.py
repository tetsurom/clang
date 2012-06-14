import sys
from pprint import pprint
from bind import Bind

b = Bind(sys.argv[1])
pprint(b.start())
