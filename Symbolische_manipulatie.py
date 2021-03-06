#created by L. Ruijg, R. Silfhout and F. Gerken

import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

# split a string into mathematical tokens
# returns a list of numbers, operators, parantheses and commas
# output will not contain spaces
def tokenize(string):
    splitchars = list("+-*/(),")
    
    # surround any splitchar by spaces
    tokenstring = []
    for c in string:
        if c in splitchars:
            tokenstring.append(' %s ' % c)
        else:
            tokenstring.append(c)
    tokenstring = ''.join(tokenstring)
    #split on spaces - this gives us our tokens
    tokens = tokenstring.split()

    #special casing for **:
    ans = []
    for t in tokens:
        if len(ans) > 0 and t == ans[-1] == '*':
            ans[-1] = '**'
        else:
            ans.append(t)
    return ans
    
   
# check if a string represents a numeric value
def isnumber(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

# check if a string represents an integer value        
def isint(string):
    try:
        int(string)
        return True
    except ValueError:
        return False



class Expression():
    """A mathematical expression, represented as an expression tree"""
    
    """
    Any concrete subclass of Expression should have these methods:
     - __str__(): return a string representation of the Expression.
     - __eq__(other): tree-equality, check if other represents the same expression tree.
    """
    # operator overloading:
    # this allows us to perform 'arithmetic' with expressions, and obtain another expression
    def __add__(self, other):
        return AddNode(self, other)
        
    def __sub__(self, other):
        return SubNode(self, other)
        
    def __mul__(self, other):
        return MulNode(self, other)
        
    def __truediv__(self, other):
        return DivNode(self, other)
        
    def __pow__(self, other):
        return PowNode(self, other)
    
    def __neg__(self):
        return NegNode(self)
        
    # basic Shunting-yard algorithm
    def fromString(string):
        # split into tokens
        tokens = tokenize(string)
        
        # stack used by the Shunting-Yard algorithm
        stack = []
        # output of the algorithm: a list representing the formula in RPN
        # this will contain Constant's and operators
        output = []
        
        # list of operators incl their operator value
        # Comment: we created the precedence property on BinaryNodes etc but we failed to use this in this function instead of the 'oplist'
        oplist = {'+':1,'-':1,'/':2,'*':2,'**':4}
        index=-1
        for token in tokens:
            index=index+1
            #we included some standard functions(sin, cos, tan, ln). 
            if token == 'cos':
                stack.append('cos')
            elif token == 'sin':
                stack.append('sin')
            elif token == 'log':
                stack.append('log')
            elif token == 'tan':
                stack.append('tan')
                
            elif isnumber(token):
                #we used the & sign to indicate the negation
                if len(stack)==0:
                    if isint(token):
                        output.append(Constant(int(token)))
                    else:
                        output.append(Constant(float(token)))
                elif stack[-1]=='&':
                    if isint(token):
                        output.append(NegNode(Constant(int(token))))
                        stack.pop()
                    else:
                        output.append(NegNode(Constant(float(token))))
                        stack.pop()
                else:
                    if isint(token):
                        output.append(Constant(int(token)))
                    else:
                        output.append(Constant(float(token)))
            #if the '-'-sign is a negative operator, we use the indicator '&' in the stack list, 
            #otherwise he just saves the '-'-operator in the stack list
            elif token == '-':
                if len(stack)==0 and len(output)==0:
                    stack.append('&')
                elif tokens[index-1] in oplist:
                    stack.append('&')
                elif tokens[index-1] == '(':
                    stack.append('&')
                else:
                    while True:
                        if len(stack) == 0 or stack[-1] not in oplist or oplist[token] == 4 or oplist[token] > oplist[stack[-1]]:
                            break
                        output.append(stack.pop())
                    stack.append(token)
            elif token in oplist:
                # pop operators from the stack to the output until the top is no longer an operator
                while True:
                    #also stop output.append(stack.pop() when operator value of stack[-1] is smaller then operator value of token, 
                    #or when token=='**' (because of right associativity)
                    if len(stack) == 0 or stack[-1] not in oplist or oplist[token] == 4 or oplist[token] > oplist[stack[-1]]:
                        break
                    output.append(stack.pop())
                # push the new operator onto the stack
                stack.append(token)
            
            elif token == '(':
                #if it is a letter it saves the indicator '?' to check in a later moment whether this is a FunctionNode 
                if ord(tokens[index-1])>=97 and ord(tokens[index-1])<= 122:
                    stack.append('?')
                else:
                    # left parantheses go to the stack
                    stack.append(token)
            elif token == ')':
                # right paranthesis: pop everything upto the last left paranthesis to the output
                while not stack[-1] in ['(', '?'] :
                    output.append(stack.pop())
                # pop the left paranthesis from the stack (but not to the output)
                if stack[-1]=='?':
                    stack.pop()
                    x=output.pop()
                    f=output.pop()
                    output.append(FunctionNode(f,x))
                elif len(stack)==1:
                    stack.pop()
                #check if the brackets are from a cos(x)
                elif stack[-1]=='(' and stack[-2]=='cos':
                    z=output.pop()
                    output.append(CosNode(z))
                    stack.pop()
                    stack.pop()
                #check if the brackets are from a sin(x)
                elif stack[-1]=='(' and stack[-2]=='sin':
                    z=output.pop()
                    output.append(SinNode(z))
                    stack.pop()
                    stack.pop()
                #check if the brackets are from a log(x)
                elif stack[-1]=='(' and stack[-2]== 'log':
                    z=output.pop()
                    output.append(LogNode(z))
                    stack.pop()
                    stack.pop()
                #check if the brackets are from a tan(x)
                elif stack[-1]=='(' and stack[-2]== 'tan':
                    z=output.pop()
                    output.append(TanNode(z))
                    stack.pop()
                    stack.pop()
                else:
                    stack.pop()
            # if token is a small alphabetic letter --> make it an Variable and send it to output
            elif ord(token)>=97 and ord(token)<=122:
                if len(stack)==0:
                    output.append(Variable(token))
                elif stack[-1]=='&':
                    output.append(NegNode(Variable(token)))
                else:
                    output.append(Variable(token))
            else:
                # unknown token
                raise ValueError('Unknown token: %s' % token)
     
        # pop any tokens still on the stack to the output
        while len(stack) > 0:
            output.append(stack.pop())
        

        # convert RPN to an actual expression tree
        oplist = list(oplist)
        for t in output:
            if t in oplist:
                # let eval and operator overloading take care of figuring out what to do
                y = stack.pop()
                x = stack.pop()
                stack.append(eval('x %s y' % t))
            else:
                # a constant, push it to the stack
                stack.append(t)
        # the resulting expression tree is what's left on the stack
        return stack[0]

class Constant(Expression):
    """Represents a constant value"""
    def __init__(self, value, precedence = 6, associativity='both', identity=None):
        self.value = value
        #if self.value is less than zero, then it's a negative number and we want precedence = 3, for a NegNode 
        if int(self.value) < 0 : 
            self.precedence = 3
        #if self.value is equal or greater than zero, give it precedence = 6
        else: 
            self.precedence = 6
            
    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.value == other.value
        else:
            return False
        
    def __str__(self):
        return str(self.value)
        
    # allow conversion to numerical values
    def __int__(self):
        return int(self.value)
        
    def __float__(self):
        return float(self.value)
        
    def simplify(self):
        return self
        
    def evaluate(self, dictionary={}):
        return self
    
    def derivative(self,variable):
        return Constant(0)

        
class Variable(Expression):
    """Represents a variable"""
    def __init__(self, value, precedence=6, associativity='both', identity = None):
        self.value = value
        self.precedence=precedence
        
    def __str__(self):
        return str(self.value)
    
    def __eq__(self,other):
        if isinstance(other,Variable):
            return self.value==other.value
        else:
            return False
    
    def simplify(self):
        return self
        
    def evaluate(self, dictionary={}):
        # check whether the variable does appear in the dictionary
        if self.value in dictionary:
            # if so, give the variable his new value
            x = dictionary[str(self.value)]
            # then return it as a constant
            return Constant(x)
        else:
            # if not, then return the variable
            return Variable(self)
    
    def derivative(self,variable):
        if self==variable:
            return Constant(1)
        else:
            return Constant(0)
    
        
class BinaryNode(Expression):
    """A node in the expression tree representing a binary operator."""

    def __init__(self, lhs, rhs, op_symbol, precedence=0, associativity=0, identity=Constant(0)):
        self.lhs = lhs
        self.rhs = rhs
        self.op_symbol = op_symbol
        self.precedence = precedence
        self.associativity = associativity
        self.identity = identity
            
    def __eq__(self, other):
        if type(self) == type(other):
            return self.lhs == other.lhs and self.rhs == other.rhs
        else:
            return False
            
    def __str__(self):
        lstring = str(self.lhs)
        rstring = str(self.rhs)
        # check whether the precedence of the current BinaryNode is greater than the precendence of the lhs node. 
        # Then we need parenthesis at least around the lhs node
        if self.precedence > self.lhs.precedence:
            # check whether the precendence of the current BinaryNode is greater than the precedence of the rhs node
            # or (if the precendence of the current BinaryNode is equal to the precendence of the rhs node and the associativity of the current BinaryNode is left)
            # if one of this also holds, then we need parenthesis around the lhs and rhs node
            if self.precedence > self.rhs.precedence or (self.precedence == self.rhs.precedence and self.associativity == 'left'):
                return "(%s) %s (%s)" % (lstring, self.op_symbol, rstring)
            # if not, add only parenthesis to the lhs node   
            else:
                return "(%s) %s %s" % (lstring, self.op_symbol, rstring)
        # if not, check whether the precendence of the current BinaryNode is greater than the precendence of the rhs node 
        # or (if the precendence of the current BinaryNode is equal to the precendence of the rhs node and the associativity of the current BinaryNode is left)
        # if one of these holds, then we need parenthesis only around the rhs node
        elif self.precedence > self.rhs.precedence or (self.precedence == self.rhs.precedence and self.associativity == 'left'):
            return "%s %s (%s)" % (lstring, self.op_symbol, rstring)
       # if everything doesn't hold, then return the general case without parenthesis. 
        else:
            return "%s %s %s" % (lstring, self.op_symbol, rstring)

    # evaluate the input with of without the given dictionary for variables   
    def evaluate(self, dictionary = {}):
        # evaluate the left- and righthandside of the expressiontree 
        # in the beginning the leaves of the tree(i.e. the constants and variables) can be evaluated
        links = self.lhs.evaluate(dictionary)
        rechts = self.rhs.evaluate(dictionary)
        # if the lefthandside isn't a constant, then run BinaryNode with "links" and "rechts"
        if not isinstance(links, Constant):
            return BinaryNode(links, rechts, self.op_symbol, self.precedence, self.associativity)
        # if the righthandside isn't a constant either, then also run BinaryNode with "links" and "rechts"
        elif not isinstance(rechts, Constant):
            return BinaryNode(links, rechts, self.op_symbol, self.precedence, self.associativity)
        # if the left- and righthandside are constants, then evaluate the value
        else: 
            # check whether the lefthandside has precedence three, then it's a NegNode and we want parenthesis around it
            if links.precedence == 3:
                return Constant(eval("(%s) %s %s" % (links, self.op_symbol, rechts)))
            # check whether the righthandside has precedence three, then it's a NegNode and we want parenthesis around it.    
            elif rechts.precedence == 3:
                return Constant(eval("%s %s (%s)" % (links, self.op_symbol, rechts)))
            # if not, then we don't want parenthesis and we can eval it immediately
            else:
                return Constant(eval("%s %s %s" % (links, self.op_symbol, rechts)))

    def simplify(self):
        left=(self.lhs).simplify()
        right=(self.rhs).simplify()
        z=self.simplify_specific()
        T=type(z)
        if T==Constant:
            return z
        elif T==Variable:
            return z
        elif T==NegNode:
            return z
        elif T in [CosNode,SinNode,TanNode,LogNode]:
            return z
        else:
            left=z.lhs.simplify()
            right=z.rhs.simplify()
            op_symbol=z.op_symbol
            # writes a BinaryNode of Constants, incl NegNode(Constant), to one Constant
            if (type(left)==Constant or (type(left)==NegNode and type(left.operand)==Constant)) and (type(right)==Constant or (type(right)==NegNode and type(right.operand)==Constant)):
                return Constant(eval("(%s) %s (%s)" % (left, op_symbol, right)))
            elif z.associativity=='both':
                if left==z.identity:
                    return right
                elif right==z.identity:
                    return left
                # ex: x+a+b=x+(b+a) and x-a+b=x+(b-a)
                elif left.precedence==z.precedence and T(right,left.rhs).simplify() != T(right,left.rhs):
                    K=type(left)
                    return T(left.lhs,K(right, left.rhs)).simplify()
                # ex: a-b+c=(a+c)-b
                elif left.precedence==z.precedence and T(left.lhs,right).simplify() != T(left.lhs,right):
                    K=type(left)
                    return K(T(left.lhs,right),left.rhs).simplify()
                # ex: a+(b-x)=(a+b)-x
                elif right.precedence==z.precedence and T(left,right.lhs).simplify() != T(left,right.lhs):
                    K=type(right)
                    return K(T(left,right.lhs),right.rhs).simplify()
                else:
                    return T(left,right)
            elif z.associativity=='left':
                if right==z.identity:
                    return left
                elif T==SubNode and left==z.identity:
                    return NegNode(right)
                # ex: a+b-c=a+(b-c) 
                elif left.precedence==z.precedence and left.associativity=='both' and T(left.rhs,right).simplify() != T(left.rhs,right):
                    K=type(left)
                    return K(left.lhs,T(left.rhs,right)).simplify()
                # ex: a-b-c=(a-c)-b or a+b-c=(a-c)+b
                elif left.precedence==z.precedence and T(left.lhs,right).simplify() != T(left.lhs,right):
                    K=type(left)
                    return K(T(left.lhs,right),left.rhs).simplify()
                else:
                    return T(left,right)
            elif right==z.identity:
                    return left
            else:
                return T(left,right)
            
    def derivative(self,variable):
        # derivative function for BinaryNodes, comparable function exists for UnaryNodes, Constants etc
        self=self.simplify()
        T=type(self)
        if T in [MulNode,DivNode,PowNode]:
            return self.derivative_specific(variable).simplify()
        elif T in [AddNode,SubNode]:
            return T(self.lhs.derivative(variable),self.rhs.derivative(variable)).simplify()
        else:
            return self.derivative(variable).simplify()
        
class UnaryNode(Expression):
    """A node in the expression tree representing a unary operator."""
    def __init__(self, operand, op_symbol, precedence=0):
        self.operand = operand
        self.op_symbol = op_symbol
        self.precedence = precedence
    
    def __str__(self):
        if self.op_symbol in ['sin', 'cos', 'tan', 'log']:
            return "%s(%s)" % (self.op_symbol, self.operand)
        elif type(self)==FunctionNode:
            return "%s(%s)" % (self.op_symbol,self.operand)
        elif type(self)==NegNode:
            if self.operand==Constant(0):
                return str(Constant(0))
            elif type(self.operand) in [Constant,Variable]:
                return self.op_symbol+str(self.operand)
            else:
                return "%s(%s)" % (self.op_symbol, self.operand)   
        else:
            return self.op_symbol+str(self.operand)
        
    def __eq__(self, other):
        if type(self)==type(other):
            return self.operand==other.operand
        else:
            return False
            
    def evaluate(self, dictionary = {}):
        # first evaluate the operand with the dictionary
        x = self.operand.evaluate(dictionary)
        # check whether the op_symbol is a standard function
        if self.op_symbol in ['sin', 'cos', 'tan', 'log']:
            # check whether x represents a variable
            if isinstance(x, Variable):
                # if so, then it can't be evaluated. So we want the whole operation to represent as a variable 
                return Variable("%s(%s)" % (self.op_symbol, x))
            # if not, then eval it and return it as a constant
            else:
                return Constant(eval('math.'+str(self.op_symbol)+'('+str(x)+')'))
        # check whether x is a variable
        if isinstance(x, Variable):
            #if so, return it as a variable
            return Variable("%s%s" % (self.op_symbol, x))
        #if not, return it as a constant
        else:
            return Constant(eval("%s%s" % (self.op_symbol, x)))

    
class AddNode(BinaryNode):
    """Represents the addition operator"""
    def __init__(self, lhs, rhs):
        super(AddNode, self).__init__(lhs, rhs, '+', 1, 'both', )

    def simplify_specific(self):
        left=self.lhs
        right=self.rhs
        
        #rules for NegNode
        # ex: a+-b=a-b
        if type(right)==NegNode:
            return (left-right.operand).simplify()
        # ex: a+-b*c=a-b*c and a+-b/c=a-b/c
        elif type(right) in [MulNode,DivNode] and type(right.lhs)==NegNode:
            K=type(right)
            return (left-K(right.lhs.operand,right.rhs)).simplify()
    
        # Constants should be right of a non Constant/NedNode
        elif type(left)==Constant and type(right)!=Constant and type(right)!=NegNode:
            return (right+left).simplify()
        # ex: x+x=2*x
        elif left==right:
            return (Constant(2)*right)
        # ex: a*x+b*x=(a+b)*x
        elif type(left)==type(right)==MulNode and left.rhs==right.rhs:
            return ((left.lhs+right.lhs)*left.rhs).simplify()
        # ex: a*x+x=(a+1)*x
        elif type(left)==MulNode and left.rhs==right:
            return ((left.lhs+Constant(1))*left.rhs).simplify()
        # ex: x+a*x=(1+a)*x
        elif type(right)==MulNode and left==right.rhs:
            return ((Constant(1)+right.lhs)*left).simplify()
        else:
            return left+right

class SubNode(BinaryNode):
    """Represents the substraction operator"""
    def __init__(self, lhs, rhs):
        super(SubNode, self).__init__(lhs, rhs, '-', 1, 'left', )

    def simplify_specific(self):
        left=self.lhs
        right=self.rhs
        
        #extra rules for NegNode:
        # ex: x-(-a)=x+a
        if type(right)==NegNode:
            return (left+right.operand).simplify()
        # ex: a--b*c=a+b*c and a--b/c=a+b/c
        elif type(right) in [MulNode,DivNode] and type(right.lhs)==NegNode:
            K=type(right)
            return (left+K(right.lhs.operand,right.rhs)).simplify()
        # ex: (x-a)-b=x-(a+b)
        elif type(left)==SubNode and type(left.rhs)==type(right)==Constant:
            a=left.rhs.value+right.value
            return (left.lhs-Constant(a)).simplify()
        # ex: x-x=0
        elif left==right:
            return Constant(0)
        # ex: a*x-b*x=(a-b)*x
        elif type(left)==type(right)==MulNode and left.rhs==right.rhs:
            return ((left.lhs-right.lhs)*left.rhs).simplify()
        # ex: a*x+x=(a-1)*x
        elif type(left)==MulNode and left.rhs==right:
            return ((left.lhs-Constant(1))*left.rhs).simplify()
        # ex: x-a*x=(1-a)*x
        elif type(right)==MulNode and left==right.rhs:
            return ((Constant(1)-right.lhs)*left).simplify()
        else:
            return left-right

class MulNode(BinaryNode):
    """Represents the multiplication operator"""
    def __init__(self, lhs, rhs):
        super(MulNode, self).__init__(lhs, rhs, '*', 2, 'both', Constant(1))

    def simplify_specific(self):
        left=self.lhs
        right=self.rhs
        
        # rules for NegNode
        # ex: (-a)*(-b)=a*b
        if type(left)==type(right)==NegNode:
            return (left.operand*right.operand).simplify()
        # ex: a*(-b)=-(a*b)
        elif type(right)==NegNode:
            return (-(left*right.operand)).simplify() 
        # ex: x*a=a*x
        elif type(right)==Constant and type(left)!=Constant:
            return (right*left).simplify()
        # ex: a*(b*x)=(a*b)*x
        elif type(right)==MulNode and type(left)==type(right.lhs)==Constant:
            a=left.value*right.lhs.value
            return (Constant(a)*right.rhs).simplify()
        # ex: 0*x=0
        elif left==Constant(0) or left==NegNode(Constant(0)):
            return Constant(0)
        # ex: x*x=x**2
        elif left==right:
            return (left**Constant(2)).simplify()
        # ex: x**a*x**b=x**(a+b)
        elif type(left)==type(right)==PowNode and left.lhs==right.lhs:
            return (left.lhs**(left.rhs+right.rhs)).simplify()
        # ex: x**a*x=x**(a+1)
        elif type(left)==PowNode and left.lhs==right:
            return (left.lhs**(left.rhs+Constant(1))).simplify()
        # ex: x*x**a=x**(1+a)
        elif type(right)==PowNode and left==right.lhs:
            return (left**(Constant(1)+right.rhs)).simplify()
        # ex: a(b+x)=a*b+a*x and a(b-x)=a*b-a*x
        elif right.precedence==1:
            return type(right)(left*right.lhs,left*right.rhs).simplify()
        else:
            return left*right

    def derivative_specific(self,variable):
        # product rule for derivatives
        L=self.lhs.simplify()
        R=self.rhs.simplify()
        left=L.derivative(variable)
        right=R.derivative(variable)
        return (L*right+left*R).simplify()
        
class DivNode(BinaryNode):
    """Represents the division operator"""
    def __init__(self, lhs, rhs):
        super(DivNode, self).__init__(lhs, rhs, '/', 2, 'left', Constant(1))

    def simplify_specific(self):
        left=self.lhs
        right=self.rhs
        
        # rules for NegNode
        # ex: (-a)/(-b)=a/b
        if type(left)==type(right)==NegNode:
            return (left.operand/right.operand).simplify()
        # ex: a/(-b)=-(a/b)
        elif type(right)==NegNode:
            return (-(left/right.operand)).simplify() 
        
        # ex: 0/x=0
        elif left==Constant(0):
            return Constant(0)
        # ex: x/x=1
        elif left==right:
            return Constant(1)
        # ex: x**a/x**b=x**(a-b)
        elif type(left)==type(right)==PowNode and left.lhs==right.lhs:
            return (left.lhs**(left.rhs-right.rhs)).simplify()
        # ex: x**a*x=x**(a-1)
        elif type(left)==PowNode and left.lhs==right:
            return (left.lhs**(left.rhs-Constant(1))).simplify()
        # ex: x*x**a=x**(1-a)
        elif type(right)==PowNode and left==right.lhs:
            return (left**(Constant(1)-right.rhs)).simplify()
        else:
            return left/right

    def derivative_specific(self,variable):
        # quotient rule for derivatives
        L=self.lhs.simplify()
        R=self.rhs.simplify()
        left=L.derivative(variable)
        right=R.derivative(variable)
        return ((left*R-L*right)/(R*R)).simplify()
        
class PowNode(BinaryNode):
    """Represents the power operator"""
    def __init__(self, lhs, rhs):
        super(PowNode, self).__init__(lhs, rhs, '**', 4, 'right', Constant(1))


    def simplify_specific(self):
        left=self.lhs
        right=self.rhs

        # ex: x**0=1
        if right==Constant(0):
            return Constant(1)
        # ex: (x**a)**b=x**(a*b)
        elif type(left)==PowNode:
            return (left.lhs**(left.rhs*right)).simplify()
        # ex: (a*x)**b=a**b*x**b
        elif type(left)==MulNode:
            return (left.lhs**right*left.rhs**right).simplify()
        else:
            return left**right

    def derivative_specific(self,variable):
        L=self.lhs.simplify()
        R=self.rhs.simplify()
        left=L.derivative(variable)
        right=R.derivative(variable)
        # if at least L is a function with the specific variable
        if str(variable) in str(L):
            # if also R is a function with the specific variable
            if str(variable) in str(R):
                return (Constant(math.e)**(R*LogNode(L))*(right*LogNode(L)+left*R/L)).simplify()
            #only L is a function:
            else:
                return ((R*L**(R-Constant(1)))*left).simplify()
        # if only R is a function with the specific variable
        elif str(variable) in str(R):
            return (L**R*LogNode(L)*right).simplify()
        # both L and R do not contain the specific variable, so the derivative is the one of the Constant
        else:
            return Constant(0)

class NegNode(UnaryNode):
    """Represents the negation operator"""
    def __init__(self, operand):
        super(NegNode, self).__init__(operand, '-', 3)

    def simplify(self):
        if type(self.operand)==NegNode:
            return self.operand.operand.simplify()
        # check whether the operand can be simplified
        elif self.operand.simplify() != self.operand:
            return NegNode(self.operand.simplify())
        #rules for eliminating brackets
        elif type(self.operand)==AddNode:
            return (NegNode(self.operand.lhs)-self.operand.rhs).simplify()
        elif type(self.operand)==SubNode:
            return (NegNode(self.operand.lhs)+self.operand.rhs).simplify()
        else:
            return self

    def derivative(self,variable):
        O=self.operand.simplify()
        return (-O.derivative(variable)).simplify()
    

class CosNode(UnaryNode): #we have to write cos(x), only works with bracket
    """ Represents the function Cosinus"""
    def __init__(self,operand):
        super(CosNode, self).__init__(operand, 'cos', 3)

    def simplify(self):
        return self

    def derivative(self,variable):
        O=self.operand.simplify()
        op=O.derivative(variable)
        return (NegNode(SinNode(O))*op).simplify()
   
class SinNode(UnaryNode): #we have to write sin(x), only works with bracket
    """ Represents the function Sinus"""
    def __init__(self,operand):
        super(SinNode, self).__init__(operand, 'sin', 3)

    def simplify(self):
        return self
    
    def derivative(self,variable):
        O=self.operand.simplify()
        op=O.derivative(variable)
        return (CosNode(O)*op).simplify()
    
class TanNode(UnaryNode): #we have to write tan(x), only works with bracket
    """ Represents the function Tangens"""
    def __init__(self,operand):
        super(TanNode, self).__init__(operand, 'tan', 3)

    def simplify(self):
        return self

    def derivative(self,variable):
        O=self.operand.simplify()
        op=O.derivative(variable)
        return (op/(CosNode(O)*CosNode(O))).simplify()

class LogNode(UnaryNode): #we have to write log(x), only works with bracket
    """ Represents the function Logarithm"""
    def __init__(self,operand):
        super(LogNode, self).__init__(operand, 'log', 3)     

    def simplify(self):
        if self.operand==Constant(math.e):
            return Constant(1)
        else:
            return self

    def derivative(self,variable):
        O=self.operand.simplify()
        op=O.derivative(variable)
        return (op/O).simplify()

            
class FunctionNode(UnaryNode): #we can use a function in a string written with two letters or one letter and one constant, e.g. f(x) or f(2) 
    """Represents an arbitrary function"""
    def __init__(self,naam, operand):
        super(FunctionNode,self).__init__(operand, naam, 3)
        

# with this function, you plot a polynomial. Call it with graph(function, range(-x, +x))
def graph(formula, x_range):
    function = str(formula)
    with PdfPages("Graph.pdf") as pdf:
        x = np.array(x_range)
        y = eval(function)
        plt.plot(x, y)
        plt.grid()
        plt.xlabel('$X\ axis$')
        plt.ylabel('$Y\ axis$')
        plt.title('$Graph\ of\ \ $' + function)
        plt.show()  
        pdf.savefig()        
    