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
        oplist = {'+':1,'-':1,'/':2,'*':2,'**':4}
        index=-1
        for token in tokens:
            index=index+1
            
            if isnumber(token):
                if len(stack)==0:
                    if isint(token):
                        output.append(Constant(int(token)))
                    else:
                        output.append(Constant(float(token)))
                elif stack[-1]=='&':
                    if isint(token):
                        output.append(NegNode(int(token)))
                        stack.pop()
                    else:
                        output.append(NegNode(float(token)))
                        stack.pop()
                else:
                    if isint(token):
                        output.append(Constant(int(token)))
                    else:
                        output.append(Constant(float(token)))
                        
           
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
                    # push the new operator onto the stack
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
                if len(stack)==0:
                    output.append(Variable(str(token)))
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
        # check whether the variable does appear in the dictionary
        if self.value in dictionary:
            # if so, give the variable his new value
            x = dictionary[str(self.value)]
            # then return it as a constant
            return Constant(x)
        else:
            # if not, the return the variable
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
            # check whether the lefthandside has precedence three, then it's a NegNode and we want parenthesis around it
            if links.precedence == 3 :
                a = Constant(eval("(%s) %s %s" % (links, self.op_symbol, rechts)))
                return a
            # check whether the righthandside has precedence three, then it's a NegNode and we want parenthesis around it.    
            elif rechts.precedence == 3:
                a = Constant(eval("%s %s (%s)" % (links, self.op_symbol, rechts)))
                return a
            # if not, then we don't want parenthesis and we can eval it immediately
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
        
    def __eq__(self, other):
        if type(self)==type(other):
            return self.operand==other.operand
            
    def evaluate(self, dictionary = {}):
        # first evaluate the operand with the dictionary
        x = self.operand.evaluate(dictionary)
        # check whether x is a variable
        if isinstance(x, Variable):
            # if so, return it as a variable
            a = Variable("%s%s" % (self.op_symbol, x))
            return a
        # if not, return it as a constant
        else:
            a = Constant(eval("%s%s" % (self.op_symbol, x)))
            return a

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
