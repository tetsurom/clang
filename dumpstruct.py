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

    def analyze_struct(self,node,name = ""):
        params = []
        if name == "":
            name = node.spelling
        for child in node.get_children():
            if child.kind.name == 'FIELD_DECL' or child.kind.name == 'UNION_DECL':
                decl = self.get_member(child.type,child)
                if type(decl) == str:
                    params.append((decl, child.displayname))
                else:
                    params.append(decl)
        if len(params) > 0 and name != '':
            self.decl_list.append([name,params])

    def visit_node(self,node):
        if node.kind.name == 'STRUCT_DECL':# and not str(node.location.file).startswith('/usr'):
            self.analyze_struct(node)
        if node.kind.name == 'TYPEDEF_DECL':
            child = list(node.get_children())
            if len(child) > 0:
                self.analyze_struct(child[0],node.spelling)
        else:
            for c in node.get_children():
                self.visit_node(c)

