import sys
from bind import Bind
import codegen

b = Bind(sys.argv[1])
b.start()
c = codegen.CodeGen("GL")
c.codegen(b.func_decl_list)
