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
    TypeKind.CHAR_S    : "TODO",
    TypeKind.SCHAR     : "char",
    TypeKind.WCHAR     : "TODO",
    TypeKind.SHORT     : "short",
    TypeKind.INT       : "int",
    TypeKind.LONG      : "long",
    TypeKind.LONGLONG  : "long long",
    TypeKind.INT128     : "TODO",
    TypeKind.FLOAT      : "float",
    TypeKind.DOUBLE     : "double",
    TypeKind.LONGDOUBLE : "long double"
}

def real_type(ty):
    if ty.kind == TypeKind.TYPEDEF:
        ty = ty.get_canonical()
    return ty

def visit_node(node, indent=0):
    if node.kind.name == 'FUNCTION_DECL' and not node.location.file.name.startswith('/usr'):
        ret_type = node.type.get_result();
        ret_type = real_type(ret_type);

        if ret_type.kind == TypeKind.POINTER:
            ty = ret_type.get_pointee()
            decl = ty.get_declaration()
            name = decl.spelling
            if name == None:
                name = "void"
            print '%s *%s;' % (name, node.displayname)
        elif ret_type.kind != None:
            print '%s %s;' % (typeconv[ret_type.kind], node.displayname)
        else:
            print '%s %s;' % (ret_type.get_declaration().spelling, node.displayname)
        #for c in node.get_children():
        #    visit_func(c, indent=indent+1)
    else:
        for c in node.get_children():
            visit_node(c, indent=indent+1)

def visit_func(node, indent=0):
    if node.kind.name == 'PARM_DECL' and not node.location.file.name.startswith('/usr'):
        print '%s%s : %s' % ('  ' * indent, node.kind.name, node.spelling)
    for c in node.get_children():
        visit_func(c, indent=indent+1)

def print_node(node, indent=0):
    print '%s%s : %s' % ('  ' * indent, node.kind.name, node.displayname)
    for c in node.get_children():
        print_node(c, indent=indent+1)


index = Index.create()
tree = index.parse(sys.argv[1])
visit_node(tree.cursor)

