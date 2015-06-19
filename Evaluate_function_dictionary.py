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
                    # geval '-3' aan het begin van uitdrukking
                    if len(output)==0 and stack[-1]=='-':
                        output.append(NegNode(int(token)))
                    # geval '-3' rhs-element van eerste binary node
                    if len(output)==2 and output[-1] in oplist and stack[-1]=='-':
                        output[2]=output[1]
                        output[1]=NegNode(int(token))
                        stack.pop()
                    if len(output)>2 and output[-1] in oplist and output[-2] in oplist and stack[-1]=='-':
                        output.append(output[-1])
                        output[-2]= NegNode(int(token))
                else:
                    # geval '-3' aan het begin van uitdrukking
                    if len(output)==0 and stack[-1]=='-':
                        output.append(NegNode(float(token)))
                    # geval '-3' rhs-element van eerste binary node
                    if len(output)==2 and output[-1] in oplist and stack[-1]=='-':
                        output[2]=output[1]
                        output[1]=NegNode(float(token))
                        stack.pop()
                        #geval '-3' element van twede binary node
                    if len(output)>2 and output[-1] in oplist and output[-2] in oplist and stack[-1]=='-':
                        output.append(output[-1])
                        output[-2]= NegNode(float((token)))
                    
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