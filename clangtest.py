import sys
import re
from dumpstruct import dumpstruct
from pprint import pprint

typechecker = {
    "void":1,
    "bool":1,
    "char":1,
    "unsigned char":1,
    "int16_t":1,
    "int32_t":1,
    "unsinged short":1,
    "unsigned int":1,
    "unsigned long":1,
    "unsigned long long":1,
    "char":1,
    "short":1,
    "int":1,
    "long":1,
    "long long":1,
    "float":1,
    "double":1,
    "long double":1
}

def tycheck(name):
    if name in typechecker:
        return name + " "
    else:
        return "struct " + name + " *"


def print_function(type_map,route_str):
    route_list = route_str.split("->")
    root_obj = re.compile("([a-zA-Z0-9_]+) : ([a-zA-Z0-9_]+)").search(route_list[0]).group(0).split(" : ")
    root_obj.reverse()
    route_list = route_list[1:]
    member_list =  type_map[root_obj[0]]
    output_list = []
    for x in route_list:
        x_type = ""
        for y in member_list:
            if x == y[1]:
                x_type = y[0]
                break;
        x_type = re.compile("[a-zA-Z0-9_]+").search(x_type).group(0)
        output_list.append((x_type,x))
        if x_type in typechecker:
            member_list = []
        else:
            member_list = type_map[x_type]
    print "%sf(void *ptr)\n{\n\t%s%s = (%s)ptr;" % (tycheck(output_list[-1][0]),tycheck(root_obj[0]),root_obj[1],tycheck(root_obj[0]))
    p = root_obj[1]
    for t in output_list:
        print "\t%s%s = %s->%s;" % (tycheck(t[0]),t[1],p,t[1])
        if t[1].endswith("NULL"):
            print "\tif(IS_NULL(%s)) {\n\t\treturn K_NULL; //Error Handling\n\t}" % (t[1])
        p = t[1]
    print "\treturn %s;\n}" % (output_list[-1][1])



b = dumpstruct(sys.argv[1])
type_map = b.start()

#for type_name in ["kcontext_t", "_kObject", "ksfp_t"]:
def dumpstruct(name):
    try:
        print ""
        tdata = type_map[name]
        for t in tdata:
            print t[0],t[1]
    except:
        print "No such name."

def dumproute(name):
    print ""
    print_function(type_map,name)
"""
def dumpreftrace(name):
    try:
        print ""
        tdata = type_map[name]
        count = 0
        out_list = []
        for t in tdata:
            if t[0].startswith("_k"):
                fmt = "KREFTRACE%s(obj->%s)";
                d = "v"
                if t[0].endswith("NULL"):
                    d = "n"
                out_list.append((fmt) % (d,t[1])
        print "static void %s_reftrace(CTX, kObject *o)\n{\n\tBEGIN_REFTRACE(%d);" % (len(out_list))
        print "%s obj = )o;" % ()
        for x in out_list:
    except:
        print "error"
"""

for x in type_map:
    print x

print ">>> ",

for line in iter(sys.stdin.readline, ""):
    if line.startswith("exit"):
        break
    elif line.startswith("struct("):
        line = line[7:]
        dumpstruct(line.rstrip("\n)"));
    elif line.startswith("accessTo("):
        line = line[9:]
        dumproute(line.rstrip(")\n"));
    elif line.startswith("reftrace("):
        line = line[9:]
        #dumpreftrace(line.rstrip(")\n")
    print ">>> ",


