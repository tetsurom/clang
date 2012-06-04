import sys
import clang.cindex

def visit_node(node, indent=0):
    if node.kind.name == 'FUNCTION_DECL' and not node.location.file.name.startswith('/usr'):
        ret_type = node.type.get_result();
        if True or ret_type.kind.name.endswith("VOID"):
            print '%s %s;' % (ret_type.kind.name, node.displayname)
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


index = clang.cindex.Index.create()
tree = index.parse(sys.argv[1])
visit_node(tree.cursor)

