import sys
import re
from clang.cindex import *
from pprint import pprint

typeconv = {
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
structenv = {}
struct_decl_list = []
func_decl_list = []

def real_type(ty):
    if ty.kind == TypeKind.TYPEDEF:
        ty = ty.get_canonical()
    return ty

def pointer_type(ty):
    ty = ty.get_pointee()
    if ty.kind == TypeKind.UNEXPOSED or ty.kind == TypeKind.RECORD:
        if not type(ty.get_declaration().spelling) is type(None):
            name =  ty.get_declaration().spelling
        else:
            return "functionalpointer",type_resolve(ty.get_result())
    elif ty.kind == TypeKind.TYPEDEF or  ty.kind == TypeKind.POINTER:
        name = type_resolve(ty)
    elif ty.kind == TypeKind.FUNCTIONPROTO:
        return "functionalpointer",type_resolve(ty.get_result())
    else:
        name = typeconv[ty.kind]
    if name == None:
        name = "void"
    return "*" + name

def type_resolve(ty):
    ty = real_type(ty)
    if ty.kind == TypeKind.POINTER:
        return pointer_type(ty)
    elif ty.kind == TypeKind.RECORD:
        name = ty.get_declaration().spelling
        return name
    return typeconv[ty.kind]

def solve_pointer(ty,node):
    name = type_resolve(ty)
    if type(name) == tuple :
        funcname = solve_funcpointer(node)
        return [funcname,name[1]]
    return name

def solve_funcpointer(node):
    name = []
    for c in node.get_children():
        name.append((type_resolve(c.type),c.displayname))
    return name

def visit_node(node, indent=0):
    if node.kind.name == 'STRUCT_DECL' and not str(node.location.file).startswith('None') and not node.displayname in structenv:# and not str(node.location.file).startswith('/usr'):
        structenv[node.displayname] = 1
        analyze_struct(node)
    elif node.kind.name == 'UNION_DECL' and not str(node.location.file).startswith('None') and not node.displayname in structenv and node.displayname != "":# and not str(node.location.file).startswith('/usr'):
        structenv[node.displayname] = 1
        analyze_struct(node)
    elif node.kind.name == 'FUNCTION_DECL':# and not str(node.location.file).startswith('/usr'):

        analyze_function(node)
    else:
        for c in node.get_children():
            visit_node(c, indent+1)

def get_member(node):
    ty = real_type(node.type)
    if   ty.kind == TypeKind.POINTER:
        return solve_pointer(ty,node)
    elif ty.kind == TypeKind.CONSTANTARRAY:
        return "[" + type_resolve(ty.get_array_element_type())
    elif ty.kind == TypeKind.FUNCTIONPROTO:
        return solve_pointer(ty.get_result(),node)
    elif ty.kind != None and ty.kind != TypeKind.RECORD:
        return typeconv[ty.kind]
    else:
        name = ty.get_declaration().spelling
        if name == "":
            #analyze_struct(node,indent+1)
            return "TODO:union"
        else:
            return name

def analyze_struct(node, indent=0):
    members = []
    for child in node.get_children():
        members.append((get_member(child), child.displayname))
    struct_decl_list.append([node.displayname,members])


def analyze_function(node, indent=0):
    params = []
    ret = get_member(node)
    funcname = re.match(r'^[0-9a-zA-Z_]+',node.displayname).group(0)
    for child in node.get_children():
        if child.kind.name == 'PARM_DECL':
            params.append((get_member(child), child.displayname))
    func_decl_list.append([ret,funcname,params])


index = Index.create()
tree = index.parse(sys.argv[1])
visit_node(tree.cursor)
print "----------------- Struct Decl ----------------------"
pprint(struct_decl_list) #dump
print "----------------- Function Decl ----------------------"
pprint(func_decl_list)
