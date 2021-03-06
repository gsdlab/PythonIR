'''
Created on Nov 21, 2013

@author: ezulkosk
'''
#from common import Common
import z3
#from z3core import *
from z3core import Z3_benchmark_to_smtlib_string, Ast

def convertToSMTLib(f, status="unknown", name="benchmark", logic=""):
    '''
    SMTLIB
    '''
    assertions = f.assertions()
    num_assertions = len(assertions)
    v = (Ast * num_assertions)()
    for i in range(num_assertions):
        v[i] = assertions[i].as_ast()
    return Z3_benchmark_to_smtlib_string(f.ctx.ref(), name, logic, status, "", num_assertions, v, z3.BoolVal(True).as_ast())


'''
###################################
# Z3-Str
###################################
'''

'''
def printZ3StrConstraints(cfr):
    f_n = open("z3str_in", 'w')
    f_n.write("(set-option :auto-config true)\n")
    f_n.write("(set-option :produce-models true)\n")
    f_n.write("(declare-variable " + "EMPTYSTRING String)\n")
    f_n.write("(assert (= EMPTYSTRING \"\"))\n")
    for i in cfr.cfr_sorts.values():    
        for j in i.instances:
            f_n.write("(declare-variable " + str(j) + " Int)\n")
        if i.refs:
            if i.refSort.type == "string":
                sort = "String"
            elif i.refSort.type == "integer":
                sort = "Int"
            elif i.refSort.type == "real":
                sort = "Real"
            else:
                print(i.refSort.type)
                sys.exit("Bug in printZ3StrConstraints")
            for j in i.refs:
                f_n.write("(declare-variable " + str(j) + " " + sort + ")\n")
    for i in cfr.cfr_sorts.values():
        i.constraints.z3str_print(f_n)
    cfr.join_constraints.z3str_print(f_n)
    for i in cfr.smt_bracketed_constraints:
        i.z3str_print(f_n)
    
    f_n.write("(check-sat)\n")
    f_n.write("(get-model)\n")
    
    f_n.close()
    
def obj_to_string(constraint):
    return ("(assert " + strprint(constraint) + ")")
        
def strprint(c):
    
    k = c.decl().kind()
    if(z3_op_to_str.get(k)):
        op = z3_op_to_str.get(k)
        if op == "Distinct":
            return ("(not (= " + " ".join([str(strprint(d)) for d in c.children()]) + "))")
        elif op == "true" or op == "false":
            return op
        else:
            return ("(" + op + " " + " ".join([str(strprint(d)) for d in c.children()]) + ")")
    if k in z3_infix:
        return ("(" + str(c.decl()) + " " + " ".join([str(strprint(d)) for d in c.children()]) + ")")
    elif z3.is_const(c):
        c = str(c)
        if c.find("$") != -1:
            array = c.split("$")
            op = array.pop(0)
            retStr = "(" + op
            if op in ["Length"]:
                arity = 1
            elif op in ["Indexof", "Contains", "Concat"]:
                arity = 2
            elif op in ["Substring", "Replace"]:
                arity = 3
            for _ in range(arity):
                arg = array.pop(0)
                if arg.startswith(Common.STRCONS_SUB):
                    retStr = retStr + " " + strprint(Common.string_map[arg])
                else:
                    retStr = retStr + " " + strprint("$".join([arg] + array))
            retStr = retStr + ")"
            return retStr
        elif c == "EMPTYSTRING":
            return c
        elif c.startswith(Common.STRCONS_SUB):
            return("\"" + Common.string_map[c] + "\"")
        return(c)
    else:
        sys.exit("Bug in Z3Str_Printer: " + str(c))

#Z3 operator names to Z3Py
z3_op_to_str = {
    Z3_OP_TRUE : 'true', Z3_OP_FALSE : 'false', Z3_OP_EQ : '=', Z3_OP_DISTINCT : 'Distinct', 
    Z3_OP_ITE : 'ite', Z3_OP_AND : 'and', Z3_OP_OR : 'or', Z3_OP_IFF : '==', Z3_OP_XOR : 'Xor',
    Z3_OP_NOT : 'not', Z3_OP_IMPLIES : '=>', Z3_OP_IDIV : 'div', Z3_OP_MOD : '%',
    Z3_OP_TO_REAL : 'ToReal', Z3_OP_TO_INT : 'ToInt', Z3_OP_POWER : '**', Z3_OP_IS_INT : 'IsInt', 
    Z3_OP_BADD : '+', Z3_OP_BSUB : '-', Z3_OP_BMUL : '*', Z3_OP_BOR : '|', Z3_OP_BAND : '&',
    Z3_OP_BNOT : '~', Z3_OP_BXOR : '^', Z3_OP_BNEG : '-', Z3_OP_BUDIV : 'UDiv', Z3_OP_BSDIV : '/', Z3_OP_BSMOD : '%',
    Z3_OP_BSREM : 'SRem', Z3_OP_BUREM : 'URem', Z3_OP_EXT_ROTATE_LEFT : 'RotateLeft', Z3_OP_EXT_ROTATE_RIGHT : 'RotateRight',
    Z3_OP_SLEQ : '<=', Z3_OP_SLT : '<', Z3_OP_SGEQ : '>=', Z3_OP_SGT : '>',
    Z3_OP_ULEQ : 'ULE', Z3_OP_ULT : 'ULT', Z3_OP_UGEQ : 'UGE', Z3_OP_UGT : 'UGT',
    Z3_OP_SIGN_EXT : 'SignExt', Z3_OP_ZERO_EXT : 'ZeroExt', Z3_OP_REPEAT : 'RepeatBitVec', 
    Z3_OP_BASHR : '>>', Z3_OP_BSHL : '<<', Z3_OP_BLSHR : 'LShR', 
    Z3_OP_CONCAT : 'Concat', Z3_OP_EXTRACT : 'Extract', Z3_OP_BV2INT : 'BV2Int',
    Z3_OP_ARRAY_MAP : 'Map', Z3_OP_SELECT : 'Select', Z3_OP_STORE : 'Store', 
    Z3_OP_CONST_ARRAY : 'K' 
    }

# List of infix operators
z3_infix = [ 
    Z3_OP_EQ, Z3_OP_IFF, Z3_OP_ADD, Z3_OP_SUB, Z3_OP_MUL, Z3_OP_DIV, Z3_OP_IDIV, Z3_OP_MOD, Z3_OP_POWER,
    Z3_OP_LE, Z3_OP_LT, Z3_OP_GE, Z3_OP_GT, Z3_OP_BADD, Z3_OP_BSUB, Z3_OP_BMUL, Z3_OP_BSDIV, Z3_OP_BSMOD, Z3_OP_BOR, Z3_OP_BAND,
    Z3_OP_BXOR, Z3_OP_BSDIV, Z3_OP_SLEQ, Z3_OP_SLT, Z3_OP_SGEQ, Z3_OP_SGT, Z3_OP_BASHR, Z3_OP_BSHL
    ]

z3_unary = [ Z3_OP_UMINUS, Z3_OP_BNOT, Z3_OP_BNEG ]

# Precedence
_z3_precedence = {
    Z3_OP_POWER : 0,
    Z3_OP_UMINUS : 1, Z3_OP_BNEG : 1, Z3_OP_BNOT : 1,
    Z3_OP_MUL : 2, Z3_OP_DIV : 2, Z3_OP_IDIV : 2, Z3_OP_MOD : 2, Z3_OP_BMUL : 2, Z3_OP_BSDIV : 2, Z3_OP_BSMOD : 2,
    Z3_OP_ADD : 3, Z3_OP_SUB : 3, Z3_OP_BADD : 3, Z3_OP_BSUB : 3,
    Z3_OP_BASHR : 4, Z3_OP_BSHL : 4,
    Z3_OP_BAND : 5,
    Z3_OP_BXOR : 6,
    Z3_OP_BOR : 7,
    Z3_OP_LE : 8, Z3_OP_LT : 8, Z3_OP_GE : 8, Z3_OP_GT : 8, Z3_OP_EQ : 8, Z3_OP_SLEQ : 8, Z3_OP_SLT : 8, Z3_OP_SGEQ : 8, Z3_OP_SGT : 8,
    Z3_OP_IFF : 8
    }
'''
