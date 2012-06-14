import sys
from bind import Bind
import codegen

print sys.argv[1]
b = Bind(sys.argv[1])
b.start()
c = codegen.CodeGen()
c.codegen(b.func_decl_list)
