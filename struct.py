import sys
from clang.cindex import *;

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

def real_type(ty):
    if ty.kind == TypeKind.TYPEDEF:
        ty = ty.get_canonical()
    return ty
def array_type_resolve(ty):
    ty = real_type(ty)
    if ty.kind == TypeKind.POINTER:
        ty = ty.get_pointee()
        if ty.kind == TypeKind.UNEXPOSED:
            name =  ty.get_declaration().spelling + " "
        elif ty.kind == TypeKind.TYPEDEF or  ty.kind == TypeKind.POINTER:
            name = array_type_resolve(ty)
        else:
            name = typeconv[ty.kind] + " "
        if name == None:
            name = "void "
        return name + "*"
    elif ty.kind == TypeKind.RECORD:
            name = ty.get_declaration().spelling
            return name + " "
    return typeconv[ty.kind] + " "

def visit_struct(node, indent=0):
    if node.kind.name == 'STRUCT_DECL' and not str(node.location.file).startswith('/usr') and not str(node.location.file).startswith('None') and not node.displayname in structenv:
        structenv[node.displayname] = 1
        print 'struct %s {' % (node.displayname)
        print_struct(node,indent)
        print '};'
    elif node.kind.name == 'UNION_DECL' and not str(node.location.file).startswith('/usr') and not str(node.location.file).startswith('None') and not node.displayname in structenv and node.displayname != "":
        structenv[node.displayname] = 1
        print 'union %s {' % (node.displayname)
        print_struct(node,indent)
        print '};'
    else:
        for c in node.get_children():
            visit_struct(c, indent+1)

def print_struct(node, indent=0,uniontab=""):
    for c in node.get_children():
        ret_type = c.type
        ret_type = real_type(ret_type);

        if ret_type.kind == TypeKind.POINTER:
            print uniontab +'\t%s%s;' % (array_type_resolve(ret_type), c.displayname)
        elif ret_type.kind == TypeKind.CONSTANTARRAY:
            print uniontab +'\t%s%s[%d];' % (array_type_resolve(ret_type.get_array_element_type()), c.displayname,ret_type.get_array_size())
        elif ret_type.kind == TypeKind.RECORD:
            name = ret_type.get_declaration().spelling
            if name == "":
                print "\tunion {"
                print_struct(c,indent+1,'\t')
                print "\t};"
            else:
                print uniontab + '\t%s %s;' % (name, c.displayname)
        elif ret_type.kind != None:
            print uniontab + '\t%s %s;' % (typeconv[ret_type.kind], c.displayname)
        else:
            print uniontab + '\t%s %s;' % (ret_type.get_declaration().spelling, c.displayname)

index = Index.create()
tree = index.parse(sys.argv[1])
visit_struct(tree.cursor)

