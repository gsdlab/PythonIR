'''
Created on Mar 24, 2013

@author: ezulkosk
'''

class DeclPExp(object):
    '''
    classdocs
    '''


    def __init__(self, quantifier, declaration, bodyParentExp):
        self.quantifier = quantifier
        self.declaration = declaration
        self.bodyParentExp = bodyParentExp
        
        
    def __str__(self):
        return self.declaration