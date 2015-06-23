import math

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
    #ADDED: special casting for '-' as a negative ###(TODO: how to evaluate -Constant and -Var etc)###
    ans = []
    for t in tokens:
        if len(ans) > 0 and t == ans[-1] == '*':
            ans[-1] = '**'
        elif len(ans)==1 and ans[0]=='-':
            ans[0]='-'+t
        elif len(ans)>1 and ans[-1]=='-' and ans[-2] in ['+','-','/','*','**','(']:
            ans[-1]='-'+t
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
    
    # TODO: when adding new methods that should be supported by all subclasses, add them to this list
    
    # operator overloading:
    # this allows us to perform 'arithmetic' with expressions, and obtain another expression
    
    #### goed onderscheid maken: wat willen wij NIET zien --> in binaryNode extra if deel, wat willen wij WEL zien HIERONDER
    #### in binary stijl, dus 5*x=5x hoor bij wat we NIET willen zien

    def __add__(self, other):
        return AddNode(self, other)
        
    def __sub__(self, other):
        # 'x-x=0*x'
        if type(self)==type(other)==Variable and self==other:
            return Constant(0)*self
        # 'a*x-b*x=(a-b)*x'
        elif isinstance(self,MulNode) and isinstance(other,MulNode) and type(self.lhs)==type(other.lhs)==Constant and self.rhs==other.rhs:
            return (Constant(sel.lhs)-Constant(other.lhs))*self.rhs
        # 'a*x-x=(a-1)*x'
        elif isinstance(self, MulNode) and self.rhs==other:
            return (Constant(self.lhs)-Constant(1))*other
        # 'x-a*x=(1-a)*x'
        elif isinstance(other,MulNode) and other.rhs==self:
            a=1-other.lhs.value
            return (Constant(1)-other.lhs)*self
        else:
            return SubNode(self, other)
        
    def __mul__(self, other):
        # We want a Constant in front of a non Constant
        if isinstance(other, Constant) and not isinstance(self, Constant):
            return other*self
        elif self==Constant(1):
            return other
        elif other==Constant(1):
            return self
        # 'x*x=x**2'
        elif self==other:
            return self**Constant(2)
        # 'a*x*x=a*x**2' # drietallen moeten apart omdat eerste tweetal andere combi
        #elif isinstance(self,MulNode) and self.rhs==other:
        #    return MulNode(self.lhs, PowNode(self.rhs, Constant(2)))
        # 'x**a*x**b=x**(a+b)
        elif isinstance(self, PowNode) and isinstance(other,PowNode) and self.lhs==other.lhs:
            return self.lhs**(self.rhs+other.rhs)
        # 'c*x**a*x**b=c*x**(a+b)' ##### WERKT NIET
        #elif isinstance(self, MulNode) and isinstance(self.rhs, PowNode) and isinstance(other, PowNode) and self.rhs.lhs==other.lhs:
        #    return MulNode(self.lhs,MulNode(self.rhs,other))
        # 'x**a*x=x**(a+1)'
        elif isinstance(self, PowNode) and self.lhs==other and isinstance(self.rhs, Constant):
            return self.lhs**(self.rhs+Constant(1))
        # 'x*x**a=x**(1+a)'
        elif isinstance(other, PowNode) and self==other.lhs and isinstance(other.rhs, Constant):
            return self**(Constant(1)+other.rhs)
        else:
            return MulNode(self, other)
        
    def __truediv__(self, other):
        # 'a*x/b=a/b*x'
        if isinstance(self,MulNode) and type(self.lhs)==type(other)==Constant and not isinstance(self.rhs, Constant):
            return (self.lhs/other)*self.rhs
        # 'x/x=x**0'
        elif self==other:
            return self**Constant(0)
        # 'x**a/x**b=x**(a-b)
        elif isinstance(self, PowNode) and isinstance(other,PowNode) and self.lhs==other.lhs and type(self.rhs)==type(other.rhs)==Constant:
            return self.lhs**(self.rhs-other.rhs)
        # 'x**a/x=x**(a-1)'
        elif isinstance(self, PowNode) and self.lhs==other and isinstance(self.rhs, Constant):
            return self.lhs**(self.rhs-Constant(1))
        # 'x/x**a=x**(1-a)'
        elif isinstance(other, PowNode) and self==other.lhs and isinstance(other.rhs, Constant):
            return self.lhs**(Constant(1)-other.rhs)
        else:
            return DivNode(self, other)
        
    def __pow__(self, other):
        if isinstance(other,PowNode):
            return self**(other.lhs*other.rhs)
        return PowNode(self, other)
    
    def __neg__(self):
        return NegNode(self)
        
    # TODO: other overloads, such as __sub__, __mul__, etc.
    def evaluate(self,dictionary=None):
        # the second object represents the dictionary which we will give by ourself (looks for example like {'x':2, 'y':3})
        # the eval class in python uses this automatically (definition)
        if dictionary==None:
            answer = eval(str(self))
            return answer
        else:
            answer=eval(str(self),dictionary)
            return answer
        
    # basic Shunting-yard algorithm
            
    def fromString(string):
        # split into tokens
        tokens = tokenize(string)
        
        # stack used by the Shunting-Yard algorithm
        stack = []
        # output of the algorithm: a list representing the formula in RPN
        # this will contain Constant's and '+'s
        output = []
        
        # list of operators incl their operator value
        oplist = {'+':2,'-':2,'/':3,'*':3,'**':4}
        
        for token in tokens:
            if isnumber(token):
                # numbers go directly to the output
                if isint(token):
                    output.append(Constant(int(token)))
                else:
                    output.append(Constant(float(token)))
                    
            elif token in oplist:
                # pop operators from the stack to the output until the top is no longer an operator
                while True:
                    # TODO: when there are more operators, the rules are more complicated
                    # look up the shunting yard-algorithm
                    # ADDED: also stop output.append(stack.pop() when operator value of stack[-1] is smaller then operator value of token, or when token=='**' (because of right associativity)
                    if len(stack) == 0 or stack[-1] not in oplist or oplist[token] == 4 or oplist[token] > oplist[stack[-1]]:
                        break
                    output.append(stack.pop())
                # push the new operator onto the stack
                stack.append(token)
            elif token == '(':
                # left parantheses go to the stack
                    stack.append(token)
            elif token == ')':
                # right paranthesis: pop everything upto the last left paranthesis to the output
                while not stack[-1] == '(':
                    output.append(stack.pop())
                # pop the left paranthesis from the stack (but not to the output)
                stack.pop()
            # TODO: do we need more kinds of tokens?
            #ADDED: if token is a small alphabetic letter --> make it an Variable and send it to output
            ####TODO: Do we want to leave some letters (a-e?) to auto make them Constants?
            elif ord(token)>=97 and ord(token)<=122:
                output.append(Variable(str(token)))
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
    def __init__(self, value, precedence = 6):
        self.value = value
        if self.value < 0 : 
            self.precedence = 3
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
        
    
    
        
class Variable(Expression):
    """Represents a variable value"""
    def __init__(self, value, precedence=6):
        self.value = value
        self.precedence=precedence
        
    def __str__(self):
        return str(self.value)
    
    def __eq__(self,other):
        if isinstance(other,Variable):
            return self.value==other.value
        else:
            return False
        
    
        
        
class BinaryNode(Expression):
    """A node in the expression tree representing a binary operator."""

    def __init__(self, lhs, rhs, op_symbol, precedence=0, associativity=0):
        self.lhs = lhs
        self.rhs = rhs
        self.op_symbol = op_symbol
        self.precedence = precedence
        self.associativity = associativity
    #ADDED: list of operators incl their operator value

    # TODO: what other properties could you need? Precedence, associativity, identity, etc.
            
    def __eq__(self, other):
        if type(self) == type(other):
            return self.lhs == other.lhs and self.rhs == other.rhs
        else:
            return False
            
    def __str__(self):
        lstring = str(self.lhs)
        rstring = str(self.rhs)
        
        # ADDED: check whether the type of the lhs node is a BinaryNode and if parenthesis are necessary for AT LEAST the lhs node

        if self.precedence > self.lhs.precedence:

            # ADDED: check whether the type of the rhs node is a BinaryNode and if parenthesis are needed around rhs node, by checking if one of the following is true:
            #the operator value of current BinaryNode is greater than the operator value of the rhs node, or 
            #the value of the current BinaryNode AND of the rhs node are equal to '**', (ergo power operation value of 4 and right associative) 
            # Notice: we check the last condition only for the rhs, because the power operator is right associative.
            if self.precedence > self.rhs.precedence or (self.precedence == self.rhs.precedence and self.associativity == 'left'):
                return "(%s) %s (%s)" % (lstring, self.op_symbol, rstring)
            # ADDED: if not, add only parenthesis to the lhs    
            else:
                return "(%s) %s %s" % (lstring, self.op_symbol, rstring)
    
        # ADDED: if not, check whether the type of the rhs node is a BinaryNode and if parenthesis are necessary for the rhs node (checking procedure equal to the above one)

        elif self.precedence > self.rhs.precedence or (self.precedence == self.rhs.precedence and self.associativity == 'left'):
            return "%s %s (%s)" % (lstring, self.op_symbol, rstring)
        
                
        #ADDED: Simplify trivial expressions, e.g 'x+0'='x' for example
        if isinstance(self, MulNode):
            # 'x*0'='0' and '0*x'='0'
            if self.lhs==Constant(0) or self.rhs==Constant(0):
                return str(Constant(0))
            # 'x*1'='x'
            #elif self.rhs==Constant(1):
            #    return lstring
            # '1*x'='x'
            #elif self.lhs == Constant(1):
            #    return rstring
            ###### HIER ALLE VERSIMPELINGEN VOOR ÉÉN NODE ########
            else:
                a = "%s %s %s" % (self.lhs, self.op_symbol, self.rhs)
                return a

        elif isinstance(self, PowNode):
            # 'x**0 = 1'
            if self.rhs==Constant(0):
                return Constant(1)
            # 'x**1=x'
            elif self.rhs==Constant(1):
                return lstring
            else:
                a = "%s %s %s" % (lstring, self.op_symbol, rstring)
                return a
                #return partial_evaluation(a)

        elif isinstance(self, AddNode):
            #'0+x'='x'
            if self.lhs==Constant(0):
                return rstring
            #'x+0'='x'
            elif self.rhs==Constant(0):
                return lstring
            else:
                a = "%s %s %s" % (lstring, self.op_symbol, rstring)
                return a
                #return partial_evaluation(a)
                
        elif isinstance(self, DivNode):
            ### TODO: zorgen dat float altijd naar breuk middels aparte functie
            ## TODO: maak aparte functie die breuk combi naar kleinste breuk N schrijft
            # 'x/1'='x'
            if self.rhs==Constant(1):
                return lstring
            elif type(self.lhs)==type(self.rhs)==Constant and isint(str(self.lhs)) and isint(str(self.rhs)):
                rest=ggd(self.lhs.value,self.rhs.value)
                teller=int(self.lhs.value/rest)
                noemer=int(self.rhs.value/rest)
                return "%s %s %s" % (teller, self.op_symbol, noemer)
            else:
                a = "%s %s %s" % (lstring, self.op_symbol, rstring)
                return a
                #return partial_evaluation(a)
                
        
        # ADDED: if everything doesn't hold, then return the general case without parenthesis. 
        else:
            a = "%s %s %s" % (lstring, self.op_symbol, rstring)
            return a
            #return partial_evaluation(a)


        
class UnaryNode(Expression):
    """A node in the expression tree representing a unary operator."""
    def __init__(self, operand, op_symbol=None, precedence=0):
        self.operand = operand
        self.op_symbol = op_symbol
        self.precedence = precedence
    
    def __str__(self):
        return self.op_symbol+str(self.operand)

#class Derivative(BinaryNode): 

class AddNode(BinaryNode):
    """Represents the addition operator"""
    def __init__(self, lhs, rhs):
        super(AddNode, self).__init__(lhs, rhs, '+', 1, 'both')

    def simplify(self):
        left=self.lhs
        right=self.rhs
        
        # verwachting bij deze regels is dat constante vóór variable staat bij vermenigvuldiging
        ## toevoegen Constanten bij elkaar schrijven tot één constante?
        # We willen constante achteraan in de optelling
        #if isinstance(left,Constant) and not isinstance(right,Constant):
        #    return (other+self).simplify()
        #elif isinstance(self,AddNode) and isinstance(self.rhs,Constant) and not isinstance(other, Constant):
        #    return AddNode(self.lhs,AddNode(self.rhs,other))
        if type(left)==type(right)==Constant:
            a=left.value+right.value
            return Constant(a)
        # 'x+x=2*x'
        elif left==right:
            return Constant(2)*left
        # 'a*x+b*x=(a+b)*x' ## waarbij 'voorkeur' gaat naar Constanten bij elkaar schrijven
        elif isinstance(left,MulNode) and isinstance(right,MulNode) and type(left.lhs)==type(right.lhs)==Constant and left.rhs==right.rhs:
            return (left.lhs+right.lhs).simplify()*left.rhs
        # 'a*x+x=(a+1)*x'
        #elif isinstance(self, MulNode) and self.rhs==other:
        #    return (self.lhs+Constant(1))*other
        # 'x+a*x=(1+a)*x'
        #elif isinstance(other,MulNode) and other.rhs==self:
        #    return (Constant(1)+other.lhs)*self
        else:
            return self

class SubNode(BinaryNode):
    """Represents the substraction operator"""
    def __init__(self, lhs, rhs):
        super(SubNode, self).__init__(lhs, rhs, '-', 1, 'left')
        
class MulNode(BinaryNode):
    """Represents the multiplication operator"""
    def __init__(self, lhs, rhs):
        super(MulNode, self).__init__(lhs, rhs, '*', 2, 'both')
        
class DivNode(BinaryNode):
    """Represents the division operator"""
    def __init__(self, lhs, rhs):
        super(DivNode, self).__init__(lhs, rhs, '/', 2, 'left')

class PowNode(BinaryNode):
    """Represents the power operator"""
    def __init__(self, lhs, rhs):
        super(PowNode, self).__init__(lhs, rhs, '**', 4, 'right')

class NegNode(UnaryNode):
    """Represents the negation operator"""
    def __init__(self, operand):
        super(NegNode, self).__init__(operand, '-', 3)



# TODO: add more subclasses of Expression to represent operators, variables, functions, etc.

# ADDED: evaluate a part of the string
def deler(x,y):
    antwoord=y%x
    return antwoord

def ggd(x,y):
    if y<x:
        return ggd(y,x)
    elif x == y:
        return x
    elif x == 0 and y == 0:
        return 0
    elif x == 0:
        return y
    elif y == 0:
        return x
    else:
        return ggd(x,deler(x,y))

def partial_evaluation(a):
    # ADDED: try whether there is something in the string that could be evaluated
    try:
        b = eval(a)
        if isinstance(b,float):
            return a
        else:
            return str(b)
    # ADDED: if not, then return a if there is a TypeError
    except TypeError: 
        return a
    # ADDED: if not, then return a if there is a NameError
    except NameError: 
        return a

def deriv(y,x):
    if y==x:
        return Constant(1)
    else:
        return Constant(0)