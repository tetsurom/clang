import sys
from clang.cindex import *
from pprint import pprint

class dumpstruct:
    """ 
    Show struct tool for Konoha powered by clang.cindex . 
    """

    def __init__(self,filename):
        """
        filename is a file you want to analyze.
        """
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
        self.struct_decl_list = []
        self.struct_info = {}

    def start(self):
        """
        Start analyzing.it returns analyzed functions list.
        """
        index = Index.create()
        tree = index.parse(self.filename)
        self.visit_node(tree.cursor)
        self.convert()
        return self.struct_decl_list

    def convert(self):
        self.struct_info["include_files"] = sys.argv[1:]
        self.struct_info["struct"] = {}
        for i in self.struct_decl_list:
            self.struct_info["struct"][i[0]] = {
                "struct_name":i[0],
                "member_types":self.arg_types(i[1]),
                "member_names":self.arg_names(i[1])
            }

    def make_ret_type(self,args,name,ret):
        return  {
                    "func_name":name,
                    "return_value_type":self.return_value_type(ret),
                    "arg_types":self.arg_types(args),
                    "arg_names":self.arg_names(args)
                }

    def return_value_type(self,ret):
        if type(ret) == str:
            return ret
        return self.make_ret_type(ret[1][2],ret[1][1],ret[1][0])

    def arg_types(self,list):
        ret = []
        for i in list:
            if i[0] != "-functionproto":
                ret.append(i[0])
            else:
                ret.append(self.make_ret_type(i[1][2],i[1][1],i[1][0]))
        return ret

    def arg_names(self,list):
        ret = []
        for i in list:
            if i[0] != "-functionproto":
                ret.append(i[1])
            else:
                ret.append(i[1][1])
        return ret

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
            mem.append((self.get_member(c.type,c),c.displayname))
        return ("-union", mem)

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
        elif ty.kind != None and ty.kind != TypeKind.RECORD and ty.kind != TypeKind.UNEXPOSED:
            return self.typeconv[ty.kind]
        else:
            name = ty.get_declaration().spelling
            if name == "":
                return self.uniondecl(ty,node)
            elif type(name) == type(None):
                return self.functionproto(ty.get_result(),node)
            else:
                return name

    def analyze_struct(self,node):
        params = []
        for child in node.get_children():
            if child.kind.name == 'FIELD_DECL' or child.kind.name == 'UNION_DECL':
                decl = self.get_member(child.type,child)
                if type(decl) == str:
                    params.append((decl, child.displayname))
                else:
                    params.append(decl)
        self.struct_decl_list.append([node.spelling,params])

    def visit_node(self,node):
        if node.kind.name == 'STRUCT_DECL':# and not str(node.location.file).startswith('/usr'):
            self.analyze_struct(node)
        else:
            for c in node.get_children():
                self.visit_node(c)


b = dumpstruct(sys.argv[1])
pprint(b.start())
