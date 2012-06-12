import sys
import clang.cindex

def visit_node(node, indent=0):
	print '%s%s : %s' % ('  ' * indent, node.kind.name, node.spelling)
	if node.spelling is "f":
		print node.type.kind.name
	for c in node.get_children():
		visit_node(c, indent=indent+1)

index = clang.cindex.Index.create()
tree = index.parse(sys.argv[1])
visit_node(tree.cursor)

