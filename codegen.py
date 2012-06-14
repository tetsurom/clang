import sys
import types
from pprint import pprint

debug_mode = 1

if not debug_mode == 0:
    def DBG_P(str):
        print str
        return
else:
    def DBG_P(str):
        return

# func_decl_list = [["void", "func1", [("int", "i")]],
#                   ["int", "func2", [("char", "j"), ("long", "k")]]]

class CodeGen:
    def __init__(self):
        self.args_pattern_list = {
            "void"       : "",
            "bool"       : "$(Tabs)$(AT) $(AN) = Int_to($(AT), sfp[$(SN)]);\n",
            "char"       : "$(Tabs)$(AT) $(AN) = *String_to(char *, sfp[$(SN)]);\n",
            "unsigned char"  : "$(Tabs)$(AT) $(AN) = *String_to(char *, sfp[$(SN)]);\n", #FIX ME!!
            "int16_t"    : "$(Tabs)$(AT) $(AN) = Int_to($(AT), sfp[$(SN)]);\n",
            "int32_t"    : "$(Tabs)$(AT) $(AN) = Int_to($(AT), sfp[$(SN)]);\n",
            "unsigned short"     : "$(Tabs)$(AT) $(AN) = Int_to($(AT), sfp[$(SN)]);\n",
            "unsigned int"       : "$(Tabs)$(AT) $(AN) = Int_to($(AT), sfp[$(SN)]);\n",
            "unsigned long"      : "$(Tabs)$(AT) $(AN) = Int_to($(AT), sfp[$(SN)]);\n",
            "unsigned long long" : "$(Tabs)$(AT) $(AN) = Int_to($(AT), sfp[$(SN)]);\n",
            "short"       : "$(Tabs)$(AT) $(AN) = Int_to($(AT), sfp[$(SN)]);\n",
            "int"         : "$(Tabs)$(AT) $(AN) = Int_to($(AT), sfp[$(SN)]);\n",
            "long"        : "$(Tabs)$(AT) $(AN) = Int_to($(AT), sfp[$(SN)]);\n",
            "long long"   : "$(Tabs)$(AT) $(AN) = Int_to($(AT), sfp[$(SN)]);\n",
            "float"       : "$(Tabs)$(AT) $(AN) = Float_to($(AT), sfp[$(SN)]);\n",
            "double"      : "$(Tabs)$(AT) $(AN) = Float_to($(AT), sfp[$(SN)]);\n",
            "long double" : "$(Tabs)$(AT) $(AN) = Float_to($(AT), sfp[$(SN)]);\n",
            "*char"       : "$(Tabs)char* $(AN) = String_to(char *, sfp[$(SN)]);\n",
            "[char"       : "$(Tabs)char* $(AN) = String_to(char *, sfp[$(SN)]);\n",
            "rawptr"      : "$(Tabs)$(AT) $(AN) = RawPtr_to($(AT), sfp[$(SN)]);\n",
            }
        self.return_pattern_list = {
            "void"       : "$(Tabs)RETURNvoid_();\n",
            "bool"       : "$(Tabs)RETURNb_(ret_v);\n",
            "char"       : "$(Tabs)RETURN_(new_kString(&ret_v, 1, SPOL_ASCII));\n",
            "unsigned char"  : "$(Tabs)FIX ME!!\n",
            "int16_t"    : "$(Tabs)RETURNi_(ret_v);\n",
            "int32_t"    : "$(Tabs)RETURNi_(ret_v);\n",
            "unsigned short"     : "$(Tabs)RETURNi_(ret_v);\n",
            "unsigned int"       : "$(Tabs)RETURNi_(ret_v);\n",
            "unsigned long"      : "$(Tabs)RETURNi_(ret_v);\n",
            "unsigned long long" : "$(Tabs)RETURNi_(ret_v);\n",
            "short"       : "$(Tabs)RETURNi_(ret_v);\n",
            "int"         : "$(Tabs)RETURNi_(ret_v);\n",
            "long"        : "$(Tabs)RETURNi_(ret_v);\n",
            "long long"   : "$(Tabs)RETURNi_(ret_v);\n",
            "float"       : "$(Tabs)RETURNf_(ret_v);\n",
            "double"      : "$(Tabs)RETURNf_(ret_v);\n",
            "long double" : "$(Tabs)RETURNf_(ret_v);\n",
            "*char"       : "$(Tabs)RETURN_(new_kString(&ret_v, 1, SPOL_ASCII));\n",
            "[char"       : "$(Tabs)RETURN_(new_kString(&ret_v, 1, SPOL_ASCII));\n",
            "rawptr"      : "$(Tabs)RETURN_(new_RawPtr());\n", #FIX ME!!
            }

    def func_basic_patten(self):
        DBG_P("func_basic_patten")

    def args_gen(self, args):
        ret = ""
        asize = len(args)
        i = 0
        while i < asize:
            at = args[i][0]
            an = args[i][1]
            tmp = ""
            if type(at) != types.StringType:
                return ""

            if at in self.args_pattern_list:
                tmp = self.args_pattern_list[at]
            else:
                DBG_P("Warnning: \"" + at + "\" is handled as rawptr!")
                tmp = self.args_pattern_list["rawptr"]
            tmp = tmp.replace("$(AT)", at)
            tmp = tmp.replace("$(AN)", an)
            tmp = tmp.replace("$(SN)", str(i + 1))
            ret += tmp
            i += 1
        return ret

    def func_call_gen(self, return_type):
        if return_type == "void":
            return "$(Tabs)$(FN)($(ArgNames));\n"
        else:
            return "$(Tabs)$(RT) ret_v = $(FN)($(ArgNames));\n"

    def ret_gen(self, return_type):
        if return_type in self.return_pattern_list:
            return self.return_pattern_list[return_type]
        else:
            DBG_P("Warnning: \"" + return_type + "\" is handled as rawptr!")
            return self.return_pattern_list["rawptr"]

    def bind_preface(self):
        return """
//#include <package_extra_header>

#define Int_to(T, a)      ((T)a.ivalue)
#define String_to(T, a)   ((T)S_text(a.s))
#define Float_to(T, a)    ((T)a.fvalue)
#define RawPtr_to(T, a)   ((T)a.rawptr)


"""

    def args2csv(self, args, flag):
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

    def func_bind_gen(self, func_decl):
        DBG_P("func_bind_gen")
        func_name = func_decl[1]
        return_type = func_decl[0]
        args = func_decl[2]
        ret = ""
        ret += "static KMETHOD $(CN)_$(FN)(CTX, ksfp_t *sfp _RIX)\n"
        ret += "{\n"
        ret += self.args_gen(args)
        ret += self.func_call_gen(return_type)
        ret += self.ret_gen(return_type)
        ret += "}\n"
        ret = ret.replace("$(Tabs)", "\t")
        ret = ret.replace("$(CN)", "CLASSNAME") #FIX ME!!
        ret = ret.replace("$(FN)", func_name)
        ret = ret.replace("$(RT)", return_type)
        ret = ret.replace("$(ArgNames)", self.args2csv(args, "name"))
        return ret

    def TY_(self, t):
        if type(t) == types.StringType:
            if t == "int":
                return "TY_Int"
            elif t == "float" or t == "double":
                return "TY_Float"
            elif t == "char" or t == "*char":
                return "TY_String"
            else:
                DBG_P("TY_() error!! undefined type \"" + t + "\"")
                return "TY_" + t
        else:
            return "TY_FUNC" # TODO

    def method_data_gen(self, func_decl):
        ret = "$(Tabs)_Public, _F($(CN)_$(FN), $(TY_RT), $(TY_CN), MN_(\"$(FN)\"),"
        return_type = func_decl[0]
        func_name = func_decl[1]
        args = func_decl[2]
        asize = len(args)
        for i in range(asize):
            ret += self.TY_(args[i][0]) + ", "
            ret += "FN_arg" + str(i) + ", "
        ret += "\n"
        ret = ret.replace("$(CN)", "CLASSNAME") #FIX ME!!
        ret = ret.replace("$(FN)", func_name)
        ret = ret.replace("$(TY_RT)", self.TY_(return_type))
        ret = ret.replace("$(Tabs)", "\t\t")
        return ret

    def init_package_gen(self, func_decl_list):
        ret = """
statickbool_t $(CN)_initPackage(CTX, kKonohaSpace *ks, int argc, const char**args, kline_t pline)
{
	static KDEFINE_CLASS $(CN)Def = {
			.structname = "$(CN)"/*structname*/,
			.cid = CLASS_newid/*cid*/,
	};
	kclass_t *c$(CN) = Konoha_addClassDef(ks->packid, ks->packdom, NULL, &$(CN)Def, pline);
	int FN_x = FN_("arg1");
	int FN_y = FN_("arg2");
	intptr_t MethodData[] = {
"""
        for func_decl in func_decl_list:
            ret += self.method_data_gen(func_decl)
            
        ret += """
		DEND,
	};
	kKonohaSpace_loadMethodData(ks, MethodData);
	return true;
"""
        return ret

    def codegen(self, func_decl_list):
        DBG_P("codegen")
        pprint(func_decl_list)
        ret = ""
        ret += self.bind_preface()
        for func_decl in func_decl_list:
            ret += self.func_bind_gen(func_decl)
        ret += self.init_package_gen(func_decl_list)
        print ret
