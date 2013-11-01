'''
Created on April 27, 2013

@author: ezulkosk

'''
from common import Common, Options
from front.Z3Instance import Z3Instance
from test import TestClafers
import cProfile
import sys





def main(args):
    '''
    :param args: Python output file of the Clafer compiler. Generated with argument "-m python".
    :type args: file
    
    Starting point for ClaferZ3.
    '''
    Common.MODE = Options.MODE 
    
    if Common.MODE == Common.TEST:
        TestClafers.run()
    elif Common.MODE == Common.ONE:
        TestClafers.runForOne()
    else:
        module = Options.MODULE
        
        z3 = Z3Instance(module)
        z3.run()
        #z3.run()
        
        
   
if __name__ == '__main__':
    if Options.CPROFILING:
        cProfile.run("main(sys.argv[1:])", sort=1)
    else:
        main(sys.argv[1:])
