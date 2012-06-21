import sys
from clang.cindex import *
from pprint import pprint

class bind:
    """ 
    Bind tool for Konoha powered by clang.cindex . 
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
        self.const_decl_list = {}
        self.func_decl_list = []
        self.bind_info = {}

    def start(self):
        """
        Start analyzing.it returns analyzed functions list.
        """
        index = Index.create()
        tree = index.parse(self.filename)
        self.visit_node(tree.cursor)
        self.convert()
        return self.bind_info

    def convert(self):
        self.bind_info["include_files"] = sys.argv[1:]
        self.bind_info["methods"] = {}
        self.bind_info["constant"] = self.const_decl_list
        for i in self.func_decl_list:
            self.bind_info["methods"][i[1]] = {
                "func_name":i[1],
                "return_value_type":self.return_value_type(i[0]),
                "arg_types":self.arg_types(i[2]),
                "arg_names":self.arg_names(i[2])
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

    def get_member(self,ty,node):
        ty = self.real_type(ty)
        if   ty.kind == TypeKind.POINTER:
            ty = ty.get_pointee()
            ret = self.get_member(ty,node)
            if type(ret) == type(""):
                return "*" + ret
            return ret
        elif ty.kind == TypeKind.CONSTANTARRAY:
            return "[" + self.get_member(ty.get_array_element_type(),node)
        elif ty.kind == TypeKind.FUNCTIONPROTO:
            return self.ret_functionproto(ty.get_result(),node)
        elif ty.kind != None and ty.kind != TypeKind.RECORD and ty.kind != TypeKind.UNEXPOSED and ty.kind != TypeKind.ENUM:
            return self.typeconv[ty.kind]
        else:
            name = ty.get_declaration().spelling
            if name == "":
                #analyze_struct(node,indent+1)
                return "TODO:union"
            elif type(name) == type(None):
                return self.functionproto(ty.get_result(),node)
            else:
                return name

    def analyze_function(self,node):
        params = []
        ret = self.get_member(node.type.get_result(),node)
        for child in node.get_children():
            if child.kind.name == 'PARM_DECL':
                decl = self.get_member(child.type,child)
                if type(decl) == str:
                    params.append((decl, child.displayname))
                else:
                    params.append(decl)
        self.func_decl_list.append([ret,node.spelling,params])

    def visit_node(self,node):
        if node.kind.name == 'FUNCTION_DECL':# and not str(node.location.file).startswith('/usr'):
            self.analyze_function(node)
        elif node.kind.name == 'ENUM_DECL':
            for c in node.get_children():
                self.const_decl_list[c.spelling] = c.enum_value
        else:
            for c in node.get_children():
                self.visit_node(c)

