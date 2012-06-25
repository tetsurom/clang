import sys
from clang.cindex import *
from clanganalyzer import clanganalyzer

class dumpstruct(clanganalyzer):
    """ 
    Show struct tool for Konoha powered by clang.cindex . 
    """

    def start(self):
        """
        Start analyzing.it returns analyzed struct list.
        """
        for filename in self.files:
            print filename
            index = Index.create()
            tree = index.parse(filename,self.args)
            self.visit_node(tree.cursor)
            self.convert()
            self.struct_decl_list = []
        return self.type_map

    def convert(self):
        for i in self.decl_list:
            self.type_map[i[0]] = i[1]
    """
    def make_ret_type(self,args,name,ret):
        return  {
                    "func_name":name,
                    "return_value_type":self.return_value_type(ret),
                    "arg_types":self.arg_types(args),
                    "arg_names":self.arg_names(args)
                }
    def make_union_type(self,args):
        return { "union" : {
                    "arg_types" : self.arg_types(args),
                    "arg_names" : self.arg_names(args)
               }}

    def return_value_type(self,ret):
        if type(ret) == str:
            return ret
        return self.make_ret_type(ret[1][2],ret[1][1],ret[1][0])

    def make_struct_type(self,struct_type,struct_name,member):
        return { struct_type : { "struct_name":struct_type,
                                 "member_types":self.arg_types(member),
                                 "member_names":self.arg_names(member)
        }}

    def arg_types(self,list):
        ret = []
        for i in list:
            if i[0] == "-functionproto":
                ret.append(self.make_ret_type(i[1][2],i[1][1],i[1][0]))
            elif i[0] == "-union":
                ret.append(self.make_union_type(i[1]))
            elif i[0] == "-struct":
                ret.append(self.make_struct_type(i[1],i[2],i[3]))
            elif type(i[0]) == type([]):
                ret.append(self.make_struct_type(i[0][1],i[0][2],i[0][3]))
            else:
                ret.append(i[0])
        return ret

    def arg_names(self,list):
        ret = []
        for i in list:
            if i[0] == "-functionproto":
                ret.append(i[1][1])
            elif i[0] == "-union":
                ret.append('union')
            elif i[0] == "-struct":
                ret.append(i[2])
            else:
                ret.append(i[1])
        return ret
    """

    def analyze_struct(self,node):
        params = []
        for child in node.get_children():
            if child.kind.name == 'FIELD_DECL' or child.kind.name == 'UNION_DECL':
                decl = self.get_member(child.type,child)
                if type(decl) == str:
                    params.append((decl, child.displayname))
                else:
                    params.append(decl)
        if len(params) > 0:
            self.decl_list.append([node.spelling,params])

    def visit_node(self,node):
        if node.kind.name == 'STRUCT_DECL':# and not str(node.location.file).startswith('/usr'):
            self.analyze_struct(node)
        else:
            for c in node.get_children():
                self.visit_node(c)

