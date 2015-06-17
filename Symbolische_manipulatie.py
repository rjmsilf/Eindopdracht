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
###TODO: How to import made variables and constants in the __main__ document?
def isconstant(string):
    if ord(str(string))>=97 and ord(str(string))<=122:
        A=isnumber(eval('string'))
        return A
    else:
        return False
            
def isvariable(string):
    if ord(string)>=97 and ord(string)<=122:
        try:
            a=eval('string')
            if isnumber(a)==True:
                return False
            elif isnumber(a)==False:
                return True
        except TypeError:
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
            #ADDED: if token is Variable or a Constant --> send it to output
            elif isinstance(token,Variable) or isinstance(token,Constant):
                output.append(token)
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
    def __init__(self, value):
        self.value = value
        
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
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return str(self.value)
        
        
class BinaryNode(Expression):
    """A node in the expression tree representing a binary operator."""

    def __init__(self, lhs, rhs, op_symbol):
        self.lhs = lhs
        self.rhs = rhs
        self.op_symbol = op_symbol
    #ADDED: list of operators incl their operator value
    oplist = {'+':2,'-':2,'/':3,'*':3,'**':4}

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
        if isinstance(self.lhs,BinaryNode) and BinaryNode.oplist[self.op_symbol]>BinaryNode.oplist[self.lhs.op_symbol]:
            # ADDED: check whether the type of the rhs node is a BinaryNode and if parenthesis are needed around rhs node, by checking if one of the following is true:
                #the operator value of current BinaryNode is greater than the operator value of the rhs node, or 
                #the value of the current BinaryNode AND of the rhs node are equal to '**', (ergo power operation value of 4 and right associative) 
            # Notice: we check the last condition only for the rhs, because the power operator is right associative.
            if isinstance(self.rhs,BinaryNode) and (BinaryNode.oplist[self.op_symbol]>BinaryNode.oplist[self.rhs.op_symbol] or str(self.op_symbol)==str(self.rhs.op_symbol)=='**'):
                return "(%s) %s (%s)" % (lstring, self.op_symbol, rstring)
            # ADDED: if not, add only parenthesis to the lhs    
            else:
                return "(%s) %s %s" % (lstring, self.op_symbol, rstring)
    
        # ADDED: if not, check whether the type of the rhs node is a BinaryNode and if parenthesis are necessary for the rhs node (checking procedure equal to the above one)
        elif isinstance(self.rhs,BinaryNode) and  (BinaryNode.oplist[self.op_symbol]>BinaryNode.oplist[self.rhs.op_symbol] or str(self.op_symbol)==str(self.rhs.op_symbol)=='**'):
            return "%s %s (%s)" % (lstring, self.op_symbol, rstring)
        
        # ADDED: if everything doesn't hold, then return the general case without parenthesis. 
        else:
             a = "%s %s %s" % (lstring, self.op_symbol, rstring)
             #return a
             return partial_evaluation(a)

class AddNode(BinaryNode):
    """Represents the addition operator"""
    def __init__(self, lhs, rhs):
        super(AddNode, self).__init__(lhs, rhs, '+')

class SubNode(BinaryNode):
    """Represents the substraction operator"""
    def __init__(self, lhs, rhs):
        super(SubNode, self).__init__(lhs, rhs, '-')
        
class MulNode(BinaryNode):
    """Represents the multiplication operator"""
    def __init__(self, lhs, rhs):
        super(MulNode, self).__init__(lhs, rhs, '*')
        
class DivNode(BinaryNode):
    """Represents the division operator"""
    def __init__(self, lhs, rhs):
        super(DivNode, self).__init__(lhs, rhs, '/')

class PowNode(BinaryNode):
    """Represents the power operator"""
    def __init__(self, lhs, rhs):
        super(PowNode, self).__init__(lhs, rhs, '**')
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

