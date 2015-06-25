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
        # verwachting bij deze regels is dat constante vóór variable staat bij vermenigvuldiging
        ## toevoegen Constanten bij elkaar schrijven tot één constante?
        # 'x+x=2*x'
        if self==Constant(0):
            return other
        elif other==Constant(0):
            return self
        elif self==other:
            return MulNode(Constant(2),self)
            
        # 'a*x+b*x=(a+b)*x' ## waarbij 'voorkeur' gaat naar Constanten bij elkaar schrijven
        elif isinstance(self,MulNode) and isinstance(other,MulNode) and type(self.lhs)==type(other.lhs)==Constant and self.rhs==other.rhs:
            a=self.lhs.value+other.lhs.value
            return MulNode(Constant(a),self.rhs)
        # 'a*x+x=(a+1)*x'
        elif isinstance(self, MulNode) and self.rhs==other:
            a=self.lhs.value+1
            return MulNode(Constant(a),other)
        # 'x+a*x=(a+1)*x'
        elif isinstance(other,MulNode) and other.rhs==self:
            a=other.lhs.value+1
            return MulNode(Constant(a),self)
        else:
            return AddNode(self, other)
        
    def __sub__(self, other):
        # 'x-x=0*x'
        if type(self)==type(other)==Variable and self==other:
            return MulNode(Constant(0),self)
        # 'a*x-b*x=(a-b)*x'
        elif isinstance(self,MulNode) and isinstance(other,MulNode) and type(self.lhs)==type(other.lhs)==Constant and self.rhs==other.rhs:
            a=self.lhs.value-other.lhs.value
            return MulNode(Constant(a),self.rhs)
        # 'a*x-x=(a-1)*x'
        elif isinstance(self, MulNode) and self.rhs==other:
            a=self.lhs.value-1
            return MulNode(Constant(a),other)
        # 'x-a*x=(1-a)*x'
        elif isinstance(other,MulNode) and other.rhs==self:
            a=1-other.lhs.value
            return MulNode(Constant(a),self)
        else:
            return SubNode(self, other)
        
    def __mul__(self, other):
        if self == Constant(0) or other == Constant(0):
            return Constant(0)
        # We want a Constant in front of a non Constant
        if self== Constant(0) or other == Constant(0):
            return Constant(0)
        elif self == Constant(1):
            return other
        elif other == Constant(1):
            print('hoi')
            return self
        elif isinstance(other, Constant) and not isinstance(self, Constant):
            return MulNode(other, self)
        # 'x*x=x**2'
        elif self==other:
            return PowNode(self,Constant(2))
        # 'a*x*x=a*x**2' # drietallen moeten apart omdat eerste tweetal andere combi
        elif isinstance(self,MulNode) and self.rhs==other:
            return MulNode(self.lhs, PowNode(self.rhs, Constant(2)))
        # 'x**a*x**b=x**(a+b)
        elif isinstance(self, PowNode) and isinstance(other,PowNode) and self.lhs==other.lhs:
            #a=self.rhs.value+other.rhs.value
            return PowNode(self.lhs,AddNode(self.rhs,other.rhs))
        # 'c*x**a*x**b=c*x**(a+b)' ##### WERKT NIET
        elif isinstance(self, MulNode) and isinstance(self.rhs, PowNode) and isinstance(other, PowNode) and self.rhs.lhs==other.lhs:
            return MulNode(self.lhs,MulNode(self.rhs,other))
        # 'x**a*x=x**(a+1)'
        elif isinstance(self, PowNode) and self.lhs==other and isinstance(self.rhs, Constant):
            a=self.rhs.value+1
            return PowNode(self.lhs,Constant(a))
        # 'x*x**a=x**(a+1)'
        elif isinstance(other, PowNode) and self==other.lhs and isinstance(other.rhs, Constant):
            a=other.rhs.value+1
            return PowNode(self,Constant(a))
        else:
            return MulNode(self, other)
        
    def __truediv__(self, other):
        # 'a*x/b=a/b*x'
        if other==Constant(1):
            print('hoi divnode')
            print(type(self))
            return self
        elif isinstance(self,MulNode) and type(self.lhs)==type(other)==Constant and not isinstance(self.rhs, Constant):
            return MulNode(DivNode(self.lhs, other), self.rhs)
        # 'x/x=x**0'
        elif self==other:
            return PowNode(self,Constant(0))
        # 'x**a/x**b=x**(a-b)
        elif isinstance(self, PowNode) and isinstance(other,PowNode) and self.lhs==other.lhs and type(self.rhs)==type(other.rhs)==Constant:
            a=self.rhs.value-other.rhs.value
            return PowNode(self.lhs,Constant(a))
        # 'x**a/x=x**(a-1)'
        elif isinstance(self, PowNode) and self.lhs==other and isinstance(self.rhs, Constant):
            a=self.rhs.value-1
            return PowNode(self.lhs,Constant(a))
        # 'x/x**a=x**(1-a)'
        elif isinstance(other, PowNode) and self==other.lhs and isinstance(other.rhs, Constant):
            a=1-other.rhs.value
            return PowNode(self.lhs,Constant(a))
        else:
            return DivNode(self, other)
        
    def __pow__(self, other):
        if other==Constant(1):
            return self
        else:
            return PowNode(self, other)
    
    def __neg__(self):
        return NegNode(self)
        
    # TODO: other overloads, such as __sub__, __mul__, etc.
    
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
        oplist = {'+','-','/','*','**'}
        index=-1
        for token in tokens:
            index=index+1
            if isnumber(token):
                if stack[-1]=='&':
                    # numbers go directly to the output
                    if isint(token):
                        output.append(NegNode(int(token)))
                    else:
                        output.append(NegNode(float(token)))
                else:
                    if isint(token):
                        output.append(int(token))
                    else:
                        output.append(float(token))
            elif token == '-':
                if oplist[index-1] in oplist:
                    stack.append('&')
                elif oplist[index-1] == '(':
                    stack.append('&')
                else:
                    stack.append(token)
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
        
    def evaluate(self, dictionary):
        return self
    
        
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
        
    def evaluate(self, dictionary):
        if self.value in dictionary:
            x = dictionary[str(self.value)]
            print('x = '+str(x))
            return Constant(x)
        else:
            return Variable(self)
        
        
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
            a = Constant(eval("%s %s %s" % (links, self.op_symbol, rechts)))
            return a
            
                
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

def deriv(y,x):
    if y==x:
        return Constant(1)
    else:
        return Constant(0)