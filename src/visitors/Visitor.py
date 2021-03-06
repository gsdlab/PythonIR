'''
Created on Mar 26, 2013

@author: ezulkosk
'''
import ast.Clafer
import ast.Module
import ast.ClaferId
import ast.IRConstraint
import ast.Declaration
import ast.DeclPExp
import ast.Exp
import ast.FunExp
import ast.GCard
import ast.Goal
import ast.LocalDeclaration
import ast.Supers
import ast.IntegerLiteral
import ast.DoubleLiteral
import ast.StringLiteral
import ast.RealLiteral



def visit(visitor, element):
    '''
    Method used to determine which visit method to call, based on the type of element.
    
    :param element: A Clafer AST node.
    :type element: ast.* 
    
    *see* :doc:`ast`
    '''
    if isinstance(element, ast.Clafer.Clafer):
        visitor.claferVisit(element)
    elif isinstance(element, ast.ClaferId.ClaferId):
        visitor.claferidVisit(element)
    elif isinstance(element, ast.IRConstraint.IRConstraint):
        visitor.constraintVisit(element)
    elif isinstance(element, ast.Declaration.Declaration):
        visitor.declarationVisit(element)
    elif isinstance(element, ast.DeclPExp.DeclPExp):
        visitor.declpexpVisit(element)
    elif isinstance(element, ast.Exp.Exp):
        visitor.expVisit(element)
    elif isinstance(element, ast.FunExp.FunExp):
        visitor.funexpVisit(element)
    elif isinstance(element, ast.GCard.GCard):
        visitor.gcardVisit(element)
    elif isinstance(element, ast.Goal.Goal):
        visitor.goalVisit(element)
    elif isinstance(element, ast.LocalDeclaration.LocalDeclaration):
        visitor.localdeclarationVisit(element)
    elif isinstance(element, ast.Module.Module):
        visitor.moduleVisit(element)
    elif isinstance(element, ast.Supers.Supers):
        visitor.supersVisit(element)
    elif isinstance(element, ast.IntegerLiteral.IntegerLiteral):
        visitor.integerliteralVisit(element)
    elif isinstance(element, ast.DoubleLiteral.DoubleLiteral):
        visitor.realliteralVisit(element)
    elif isinstance(element, ast.RealLiteral.RealLiteral):
        visitor.realliteralVisit(element)
    elif isinstance(element, ast.StringLiteral.StringLiteral):
        visitor.stringliteralVisit(element)
    elif element == None:
        visitor.noneVisit()
    else:
        print("Error in visitor: " + str(element))
    