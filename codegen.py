import sys

debug_mode = 1

if not debug_mode == 0:
    def DBG_P(str):
        print str
        return
else:
    def DBG_P(str):
        return

func_decl_list = [["void", "func1", [("int", "i")]],
                  ["int", "func2", [("char", "j"), ("long", "k")]]]

def func_basic_patten():
    DBG_P("func_basic_patten")

args_pattern_list = {
    "void"  : "",
    "int"   : "$(Tabs)$(AT) $(AN) = Int_to($(AT), sfp[$(SN)]);\n",
    "long"  : "$(Tabs)$(AT) $(AN) = Int_to($(AT), sfp[$(SN)]);\n",
    "float" : "$(Tabs)$(AT) $(AN) = Float_to($(AT), sfp[$(SN)]);\n",
    "char"  : "$(Tabs)$(AT) $(AN) = *String_to(char *, sfp[$(SN)]);\n"
}
def args_gen(args):
    ret = ""
    asize = len(args)
    i = 0
    while i < asize:
        at = args[i][0]
        an = args[i][1]
        tmp = args_pattern_list[at]
        tmp = tmp.replace("$(AT)", at)
        tmp = tmp.replace("$(AN)", an)
        tmp = tmp.replace("$(SN)", str(i + 1))
        ret += tmp
        i += 1
    return ret

def func_call_gen(return_type):
    if return_type == "void":
        return "$(Tabs)$(FN)($(ArgNames));\n"
    else:
        return "$(Tabs)$(RT) ret_v = $(FN)($(ArgNames));\n"

return_patten_list = {
    "void"  : "$(Tabs)RETURNvoid_();\n",
    "int"   : "$(Tabs)RETURNi_(ret_v);\n",
    "float" : "$(Tabs)RETURNf_(ret_v);\n",
    "char"  : "$(Tabs)RETURN_(new_kString(&ret_v, 1, SPOL_ASCII));\n"
    }
def ret_gen(return_type):
    return return_patten_list[return_type]

def bind_preface():
    return """
//#include <package_extra_header>

#define Int_to(T, a)      ((T)a.ivalue)
#define String_to(T, a)   ((T)S_text(a.s))
#define Float_to(T, a)    ((T)a.fvalue)


"""

def args2csv(args, flag):
    if flag == "name":
        flag = 1
    elif flag == "type":
        flag = 0
    else:
        print "args2csv:error!!"
        return ""

    ret = ""
    lsize = len(args)
    for i in range(lsize):
        ret += args[i][flag]
        if i < lsize - 1:
            ret += ", "
    return ret

def func_bind_gen(func_decl):
    DBG_P("func_bind_gen")
    func_name = func_decl[1]
    return_type = func_decl[0]
    args = func_decl[2]
    ret = ""
    ret += "static KMETHOD $(CN)_$(FN)(CTX, ksfp_t *sfp _RIX)\n"
    ret += "{\n"
    ret += args_gen(args)
    ret += func_call_gen(return_type)
    ret += ret_gen(return_type)
    ret += "}\n"
    ret = ret.replace("$(Tabs)", "\t")
    ret = ret.replace("$(CN)", "CLASSNAME") #FIX ME!!
    ret = ret.replace("$(FN)", func_name)
    ret = ret.replace("$(RT)", return_type)
    ret = ret.replace("$(ArgNames)", args2csv(args, "name"))
    return ret

def codegen():
    DBG_P("codegen")
    print func_decl_list
    ret = ""
    ret += bind_preface()
    for func_decl in func_decl_list:
        ret += func_bind_gen(func_decl)
    print ret

codegen()
