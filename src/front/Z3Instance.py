'''
Created on Apr 30, 2013

@author: ezulkosk
'''

from ast.IntegerLiteral import IntegerLiteral
from common import Common, Options, Clock
from common.Common import debug_print, standard_print, mOr
from common.Exceptions import UnusedAbstractException
from constraints import Constraints, IsomorphismConstraint
from front import Z3Str
from visitors import Visitor, CreateSorts, CreateHierarchy, \
    CreateBracketedConstraints, ResolveClaferIds, PrintHierarchy, Initialize, \
    SetScopes, AdjustAbstracts
from z3 import Solver, set_option, sat, is_array, Or, Real, And, is_real
from z3consts import Z3_UNINTERPRETED_SORT
from z3types import Z3Exception
import sys


class Z3Instance(object):
    ''' 
    :var module: The Clafer AST

    Stores and instantiates all necessary constraints for the ClaferZ3 model.
    '''
    def __init__(self, module):
        Common.reset() #resets variables if in test mode
        self.module = module
        self.z3_bracketed_constraints = []
        self.z3_sorts = {}
        self.solver = Solver()
        self.setOptions()
        self.clock = Clock.Clock()
        #print(self.solver.help())
        #print(get_version_string())
        
        """ Create simple objects used to store Z3 constraints. """
        self.join_constraints = Constraints.GenericConstraints("Z3Instance")
        
        """ 
        Used to map constraints in the UNSAT core to Boolean variables.
        Will eventually be used to map UNSAT core back to the Clafer model.
        """
        self.unsat_core_trackers = []
        self.unsat_map = {}
    
    def createGroupCardConstraints(self):
        for i in self.z3_sorts.values():
            i.addGroupCardConstraints()
            
    def createRefConstraints(self):
        for i in self.z3_sorts.values():
            i.addRefConstraints()
            
    def createCardinalityConstraints(self):
        for i in self.z3_sorts.values():
            i.createCardinalityConstraints()
    
    def mapColonClafers(self):
        for i in self.z3_sorts.values():
            if i.superSort:
                i.superSort.addSubSort(i)     
    
    def addSubSortConstraints(self):
        for i in self.z3_sorts.values():
            if i.superSort:
                i.superSort.addSubSortConstraints(i)     
    
    def getScope(self, sort):
        if sort.element.isAbstract:
            summ = 0
            for i in sort.subs:
                summ = summ + self.getScope(i)
            return summ
        else:
            return sort.numInstances 
    
    def setAbstractScopes(self):
        hasChanged = False
        for i in self.z3_sorts.values():
            if i.element.isAbstract:
                summ = 0
                for j in i.subs:
                    summ = summ + self.getScope(j)
                (lower, upper) = i.element.glCard
                i.element.glCard = (lower, IntegerLiteral(summ))
                if upper.value != summ:
                    #print(str(upper) + " " + str(summ))
                    hasChanged = True
                #i.numInstances = summ#max(summ, Options.GLOBAL_SCOPE)#summ #temp
                #i.upperCardConstraint = summ
                if summ == 0:
                    raise UnusedAbstractException(i.element.uid)
        return hasChanged
                
    def adjustAbstracts(self):
        for i in self.z3_sorts.values():
            if i.element.isAbstract:
                Visitor.visit(AdjustAbstracts.AdjustAbstracts(self), i.element)
    
    def findUnusedAbstracts(self):
        for i in self.z3_sorts.values():
            if i.element.isAbstract:
                summ = 0
                for j in i.subs:
                    summ = summ + self.getScope(j)
                if summ == 0:
                    raise UnusedAbstractException(i.element.uid)
    
    def setOptions(self):
        """
        Sets basic options for the Z3 solver.
        Adds additional options for better pretty-printing, if debugging.
        """
        self.solver.set(unsat_core=True)
        self.solver.set(model_completion=True)
        #self.solver.set(produce_models=True)
        #set_option(auto_config=False)
        #set_option(candidate_models=True)
        if Common.MODE == Common.DEBUG:
            #set_option(max_width=2)
            set_option(max_depth=1000)
            set_option(max_args=1000)
            set_option(auto_config=False)
    
    def run(self):
        '''
        :param module: The Clafer AST
        :type module: Module
        
        Converts Clafer constraints to Z3 constraints and computes models.
        '''
        try:
            self.clock.tick("translation")
            
            """ Create a ClaferSort associated with each Clafer. """  
            Visitor.visit(CreateSorts.CreateSorts(self), self.module)
            
            """ Resolve any 'parent' or 'this' ClaferID's. """
            Visitor.visit(ResolveClaferIds.ResolveClaferIds(self), self.module)
            
            """ Add subclafers to the *fields* variable in the corresponding parent clafer. Also handles supers and refs. """
            Visitor.visit(CreateHierarchy.CreateHierarchy(self), self.module)
            
            debug_print("Mapping colon clafers.")
            self.mapColonClafers()
          
            debug_print("Adjusting instances for scopes.")
            Visitor.visit(SetScopes.SetScopes(self), self.module)
          
            debug_print("Adjusting abstract scopes.")
            ''' I think these have to loop until fixed-point??? ''' 
            ''' success?!?!?!? '''
            hasChanged = True
            while hasChanged:
                #print("A")
                hasChanged = self.setAbstractScopes()
                self.adjustAbstracts()
            
            """ Initializing ClaferSorts and their instances. """
            Visitor.visit(Initialize.Initialize(self), self.module)
            
            debug_print("Creating cardinality constraints.")
            self.createCardinalityConstraints()
            
            debug_print("Creating ref constraints.")
            self.createRefConstraints()
            
            debug_print("Adding subsort constraints.")
            self.addSubSortConstraints()
            
            debug_print("Creating group cardinality constraints.")
            self.createGroupCardConstraints()
            
            debug_print("Creating bracketed constraints.")
            Visitor.visit(CreateBracketedConstraints.CreateBracketedConstraints(self), self.module)
               
            if Options.STRING_CONSTRAINTS:
                self.printZ3StrConstraints()
                Z3Str.clafer_to_z3str("z3str_in")
                return 1
               
            debug_print("Asserting constraints.")
            self.assertConstraints()     
            
            debug_print("Printing constraints.") 
            self.printConstraints()
            
            debug_print("Getting models.")  
            self.clock.tock("translation")
            models = self.get_models(Options.NUM_INSTANCES)
            
            self.clock.printEvents()
            return len(models)
        except UnusedAbstractException as e:
            print(str(e))
            return 0
        
    def printVars(self, model, count):
        self.clock.tick("printing")
        standard_print("###########################")
        standard_print("# Model: " + str(count+1))    
        standard_print("###########################")
        ph = PrintHierarchy.PrintHierarchy(self, model)
        Visitor.visit(ph, self.module)
        ph.printTree()
        standard_print("")
        self.clock.tack("printing")
    
    def assertConstraints(self):
        for i in self.z3_sorts.values():
            i.constraints.assertConstraints(self)
        self.join_constraints.assertConstraints(self)
        for i in self.z3_bracketed_constraints:
            i.assertConstraints(self)
    
    def printConstraints(self):
        if not (Common.MODE == Common.DEBUG and Options.PRINT_CONSTRAINTS):
            return
        #print(self.solver.sexpr())
        for i in self.z3_sorts.values():
            i.constraints.debug_print()
        self.join_constraints.debug_print()
        for i in self.z3_bracketed_constraints:
            i.debug_print()
            
    def printZ3StrConstraints(self):
        f_n = open("z3str_in", 'w')
        f_n.write("(set-option :auto-config true)\n")
        f_n.write("(set-option :produce-models true)\n")
        
        for i in self.z3_sorts.values():
            for j in i.instances + i.refs:
                f_n.write("(declare-variable " + str(j) + " Int)\n")
        
        for i in self.z3_sorts.values():
            i.constraints.z3str_print(f_n)
        self.join_constraints.z3str_print(f_n)
        for i in self.z3_bracketed_constraints:
            i.z3str_print(f_n)
        
        f_n.write("(check-sat)\n")
        f_n.write("(get-model)\n")
        
        f_n.close()
        
    #this is not my method, some stackoverflow or z3.codeplex.com method. Can't remember, should find it.
    # i no longer need this method, if i implement the isomorphism detection
    def get_models(self, desired_number_of_models):
        result = []
        count = 0
        #print(self.solver.sexpr())
        self.clock.tick("first model")
        while True:
            self.clock.tick("unsat")
            if (Common.MODE != Common.DEBUG and self.solver.check() == sat and count != desired_number_of_models) or \
                (Common.MODE == Common.DEBUG and self.solver.check(self.unsat_core_trackers) == sat and count != desired_number_of_models):
                if count == 0:
                    self.clock.tock("first model")
                m = self.solver.model()
                #if count ==0:
                #print(m)
                result.append(m)
                #print(self.solver.statistics())
                # Create a new constraint the blocks the current model
                
                if not Common.MODE == Common.TEST and not Common.MODE == Common.EXPERIMENT:
                    self.printVars(m, count)
                if Options.GET_ISOMORPHISM_CONSTRAINT:
                    #Common.FLAG = True
                    IsomorphismConstraint.IsomorphismConstraint(self, m).createIsomorphicConstraint()
                    #self.printConstraints()
                    #print("AFTER")
                    isoConstraint = self.z3_bracketed_constraints.pop()
                    isoConstraint.assertConstraints(self)
                    #Common.FLAG = False
                else:
                    block = []
                    for d in m:
                        # d is a declaration
                        if d.arity() > 0:
                            continue #raise Z3Exception("uninterpreted functions are not supported")
                        # create a constant from declaration
                        c = d()
                        if (str(c)).startswith("z3name!") or is_real(c):
                            continue
                        if is_array(c) or c.sort().kind() == Z3_UNINTERPRETED_SORT:
                            raise Z3Exception("arrays and uninterpreted sorts are not supported")
                        block.append(c != m[d])
                        #print(str(d) + " = " + str(m[d]))
                    if not block:
                        #input was an empty clafer model (no concretes)
                        return [[]]
                    self.solver.add(Or(block))
                count += 1
            else:
                self.clock.tock("unsat")
                if Common.MODE == Common.DEBUG and count == 0:
                    debug_print(self.solver.check(self.unsat_core_trackers))
                    core = self.solver.unsat_core()
                    debug_print(len(core))
                    for i in core:
                        print(str(i) + " ==> " + str(self.unsat_map[str(i)]))
                        print()
                    return result
                if count == 0:
                    standard_print("UNSAT")
                return result
    
    def getSort(self, uid):
        return self.z3_sorts.get(uid)
        
    def getSorts(self): 
        '''
        :returns: z3_sorts
        '''
        return self.z3_sorts.values()
        
    def addSort(self, sortID, sort):
        '''
        :param sortID: The uid of the Clafer
        :type sortID: str
        :param sort: A ClaferSort.
        :type sort: :mod:`common.ClaferSort`
        '''
        self.z3_sorts[sortID] = sort
    
    def __str__(self):
        return (str(self.getSorts())) + "\n" +\
            ("\n".join(map(str,self.getConstraints())))