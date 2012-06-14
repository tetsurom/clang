import sys
from clang.cindex import *
from pprint import pprint

class Bind:
    """ Bind tool for Konoha powered by clang.cindex . """

    def __init__(self,filename):
        self.filename = filename
        self.typeconv = {
            TypeKind.VOID      : "void",
            TypeKind.BOOL      : "bool",
            TypeKind.CHAR_U    : "char",
            TypeKind.UCHAR     : "unsigned char",
            TypeKind.CHAR16    : "int16_t",
            TypeKind.CHAR32    : "int32_t",
            TypeKind.USHORT    : "unsinged short",
            TypeKind.UINT      : "unsigned int",
            TypeKind.ULONG : "unsigned long",
            TypeKind.ULONGLONG : "unsigned long long",
            TypeKind.UINT128   : "TODO",
            TypeKind.CHAR_S    : "char",
            TypeKind.SCHAR     : "char",
            TypeKind.WCHAR     : "TODO",
            TypeKind.SHORT     : "short",
            TypeKind.INT       : "int",
            TypeKind.LONG      : "long",
            TypeKind.LONGLONG  : "long long",
            TypeKind.INT128     : "TODO",
            TypeKind.FLOAT      : "float",
            TypeKind.DOUBLE     : "double",
            TypeKind.LONGDOUBLE : "long double",
        }
        self.structenv = {}
        self.struct_decl_list = []
        self.func_decl_list = []


    def start(self):
        index = Index.create()
        tree = index.parse(self.filename)
        self.visit_node(tree.cursor)
        #print "----------------- Struct Decl ----------------------"
        #pprint(self.struct_decl_list) #dump
        #print "----------------- Function Decl ----------------------"
        #pprint(self.func_decl_list)
        return self.func_decl_list

    def real_type(self,ty):
        if ty.kind == TypeKind.TYPEDEF:
            ty = ty.get_canonical()
        return ty

    def pointer_type(self,ty):
        ty = ty.get_pointee()
        if ty.kind == TypeKind.UNEXPOSED or ty.kind == TypeKind.RECORD:
            if not type(ty.get_declaration().spelling) is type(None):
                name =  ty.get_declaration().spelling
            else:
                return "functionalpointer",self.type_resolve(ty.get_result())
        elif ty.kind == TypeKind.TYPEDEF or  ty.kind == TypeKind.POINTER:
            name = self.type_resolve(ty)
        elif ty.kind == TypeKind.FUNCTIONPROTO:
            return "functionalpointer",self.type_resolve(ty.get_result())
        elif ty.kind == TypeKind.CONSTANTARRAY:
            return "[" + self.type_resolve(ty.get_array_element_type())
        else:
            name = self.typeconv[ty.kind]
        if name == None:
            name = "void"
        return "*" + name

    def type_resolve(self,ty):
        ty = self.real_type(ty)
        if ty.kind == TypeKind.POINTER:
            return self.pointer_type(ty)
        elif ty.kind == TypeKind.RECORD:
            name = ty.get_declaration().spelling
            return name
        elif ty.kind == TypeKind.CONSTANTARRAY:
            return "[" + self.type_resolve(ty.get_array_element_type())
        return self.typeconv[ty.kind]

    def solve_pointer(self,ty,node):
        name = self.type_resolve(ty)
        if type(name) == tuple :
            funcname = self.solve_funcpointer(node)
            return [funcname,name[1]]
        return name

    def solve_funcpointer(self,node):
        name = []
        for c in node.get_children():
            name.append((self.type_resolve(c.type),c.displayname))
        return name

    def visit_node(self,node, indent=0):
        if node.kind.name == 'STRUCT_DECL' and not str(node.location.file).startswith('None') and not node.displayname in self.structenv:# and not str(node.location.file).startswith('/usr'):
            self.structenv[node.displayname] = 1
            self.analyze_struct(node)
        elif node.kind.name == 'UNION_DECL' and not str(node.location.file).startswith('None') and not node.displayname in structenv and node.displayname != "":# and not str(node.location.file).startswith('/usr'):
            self.structenv[node.displayname] = 1
            self.analyze_struct(node)
        elif node.kind.name == 'FUNCTION_DECL':# and not str(node.location.file).startswith('/usr'):
            self.analyze_function(node)
        else:
            for c in node.get_children():
                self.visit_node(c, indent+1)

    def get_member(self,node):
        ty = self.real_type(node.type)
        if   ty.kind == TypeKind.POINTER:
            return self.solve_pointer(ty,node)
        elif ty.kind == TypeKind.CONSTANTARRAY:
            return "[" + self.type_resolve(ty.get_array_element_type())
        elif ty.kind == TypeKind.FUNCTIONPROTO:
            return self.solve_pointer(ty.get_result(),node)
        elif ty.kind != None and ty.kind != TypeKind.RECORD:
            return self.typeconv[ty.kind]
        else:
            name = ty.get_declaration().spelling
            if name == "":
                #analyze_struct(node,indent+1)
                return "TODO:union"
            else:
                return name

    def analyze_struct(self,node, indent=0):
        members = []
        for child in node.get_children():
            members.append((self.get_member(child), child.displayname))
        self.struct_decl_list.append([node.displayname,members])

    def analyze_function(self,node, indent=0):
        params = []
        ret = self.get_member(node)
        for child in node.get_children():
            if child.kind.name == 'PARM_DECL':
                params.append((self.get_member(child), child.displayname))
        self.func_decl_list.append([ret,node.spelling,params])

## Use this Class##

#bind = Bind(sys.argv[1])
#pprint(bind.start())
