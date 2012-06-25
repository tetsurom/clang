import sys
from clang.cindex import *

class clanganalyzer:
    """
    Tool for Konoha powered by clang.cindex .
    """

    def __init__(self,files ,args = []):
        """
        filename is a file you want to analyze.
        """
        self.files = files
        self.args = args
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
        self.decl_list = []
        self.type_map = {}

    def start(self):
        pass #abstract

    def convert(self):
        pass #abstract

    def real_type(self,ty):
        if ty.kind == TypeKind.TYPEDEF:
            ty = ty.get_canonical()
        return ty

    def functionproto(self,ty,node):
        name = []
        ret = self.get_member(ty,node)
        for c in node.get_children():
            name.append((self.get_member(c.type,c),c.displayname))
        return ("-functionproto" , [ret,node.spelling,name])

    def ret_functionproto(self,ty,node):
        name = []
        ret = ""
        spel = ""
        for c in node.get_children():
            if c.kind.name == "TYPE_REF":
                ret = self.get_member(ty,c)
                spel = c.displayname
                for g in c.get_definition().get_children():
                    name.append((self.get_member(g.type,g),g.displayname))
        return ("-functionproto" , [ret,spel,name])

    def uniondecl(self,ty,node):
        mem = []
        for c in node.get_children():
            if c.kind.name == 'FIELD_DECL':
                mem.append((self.get_member(c.type,c),c.displayname))
        return ("-union", mem)

    def struct_ref_check(self,name,node):
        child =  list(node.get_children())
        if child.__len__() == 0:
            return name
        child = child[0]
        if child.kind.name == "TYPE_REF":
            return name
        else:
            params = []
            for c in child.get_children():
                if c.kind.name == 'FIELD_DECL' or c.kind.name == 'UNION_DECL':
                    decl = self.get_member(c.type,c)
                    if type(decl) == str:
                        params.append((decl, c.displayname))
                    else:
                        params.append(decl)
            return ["-struct",name,node.spelling,params]
                

    def get_member(self,ty,node):
        ty = self.real_type(ty)
        if   ty.kind == TypeKind.POINTER:
            ty = ty.get_pointee()
            ret = self.get_member(ty,node)
            if type(ret) == str:
                return "*" + ret
            return ret
        elif ty.kind == TypeKind.CONSTANTARRAY:
            ret = self.get_member(ty.get_array_element_type(),node)
            if type(ret) == str:
                return "*" + ret
            return ret
        elif ty.kind == TypeKind.FUNCTIONPROTO:
            return self.ret_functionproto(ty.get_result(),node)
        elif ty.kind != None and ty.kind != TypeKind.ENUM and ty.kind != TypeKind.RECORD and ty.kind != TypeKind.UNEXPOSED:
            return self.typeconv[ty.kind]
        else:
            name = ty.get_declaration().spelling
            if name == "":
                return self.uniondecl(ty,node)
            elif type(name) == type(None):
                return self.functionproto(ty.get_result(),node)
            else: #struct
                name = self.struct_ref_check(name,node)
                return name


