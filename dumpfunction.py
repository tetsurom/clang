import sys
from clang.cindex import *
from clanganalyzer import clanganalyzer

class dumpfunction(clanganalyzer):
    """ 
    Show function tool for Konoha powered by clang.cindex . 
    """

    def start(self):
        """
        Start analyzing.it returns analyzed function list.
        """
        for filename in self.files:
            print filename
            index = Index.create()
            tree = index.parse(filename,self.args)
            self.visit_node(tree.cursor)
            self.convert()
            self.decl_list = []
        return self.type_map

    def convert(self):
        for i in self.decl_list:
            self.type_map[i[1]] = (i[0],i[2])

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
        if len(params) > 0:
            self.decl_list.append([ret,node.spelling,params])

    def visit_node(self,node):
        if node.kind.name == 'FUNCTION_DECL':# and not str(node.location.file).startswith('/usr'):
            self.analyze_function(node)
        else:
            for c in node.get_children():
                self.visit_node(c)

