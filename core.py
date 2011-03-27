import sys,time

def cleanInput(input): #standardises input
    
    return input.replace(' ', '').replace('**','^').lower()

def setMainVar(input): #Allows for any variable, not just x to be used.
                       #Can later allow for multiple variables? #24-03-11 15:22PM WTF did I mean here?
    global varname
    varname = input

def isOp (input):
    oplist = ['^', 'neg()', '*', '/', '+', '-', '(', ')']
    if input in oplist:
        return True
    else:
        return False

def isInt (input): #takes a string as input, hence isintance can't be used
    try:
        a = int(input)
        return True
    except ValueError:
        return False
        
def isVar (input): # can (and will) be expanded to take multiple variables #WTF did I mean here?
    if input == varname:
        return True
    else:
        return False

def returnOpDetails(operator): #returns list, [0] is precedence, [1] is associativity, [2] is grasp
    
    optable = {'^':[4,'r',2], 'neg()':[3,'r',1], '*':[3, 'l',2], '/':[3,'l',2], '+':[2,'l',2], '-':[2,'l',2]}
    
    return optable[operator]
    
def neg(operand): #a unary minus function
    if isInt(operand): #check that an integer has been passed
        return -int(operand)
    else:
        return False

#REFERENCE IMPLEMENTATION
#OVERLY VERBOSE, OVER-COMPLICATED AND OVER-COMMENTED
#BUT IT WORKS GOOD WITH THE CRAZIEST OF FUNCTIONS

def tokenizer (input): #Splits function into its constituent pieces

    inputstack = list(input)
    outputstack = []
    tempstack = []
    
    #checks that the input makes some sort of sense initially
    if isOp(inputstack[0]):
        if inputstack[0] == '-': #Must be a starting unary minus. Convert to a neg()
            inputstack[0] = 'neg()'
        elif inputstack[0] == '+': #Must be starting with unary plus. Remove this as it's redundant
            del inputstack[0]
        elif inputstack[0] == '(': #Starts with a bracket, which is valid
            pass
        else: #starts with some random operator, must be wrong
            sys.exit('Invalid first expression entered, try again')
            
    if inputstack.count('(') != inputstack.count(')'): #check for unequal amounts of brackets, means that shunting-yard can skip this
        sys.exit('Mismatched brackets, try again')

    #splits the expression
    #hopefully should use a switch-like structure
    
    tempstack.append(inputstack.pop(0)) #Seed the following loop with the first char of the input. Means I can avoid looping an if clause
    
    for i in inputstack:
        
        tempstack.append(i) #we now have 2 variables in there
        
        #we now go through all the possible combinations of numbers, vars and operators
        if isInt(tempstack[0]) and isInt(tempstack[1]): #int followed by int means they're one number. Join together, throw back into temp
            tempstack.append(tempstack.pop(0) + tempstack.pop(0))
        
        elif isInt(tempstack[0]) and isOp(tempstack[1]): #int followed by operator -> pop int into the output
            outputstack.append(tempstack.pop(0))
            if tempstack[0] == '(': #something like 1 + 3(x+1) was entered. Note tempstack[0] because int was popped
                outputstack.append('*')
        
        elif isInt(tempstack[0]) and isVar(tempstack[1]): #int followed by var -> e.g 3x
            outputstack.append(tempstack.pop(0))
            outputstack.append('*')
        
        elif isVar(tempstack[0]) and isOp(tempstack[1]): #either x+45, or x( -> pop off to output, add * if a bracket
            outputstack.append(tempstack.pop(0))
            if tempstack[0] == '(': #tempstack[0] as the x has already been popped off
                outputstack.append('*')
        
        elif isVar(tempstack[0]) and not isOp(tempstack[1]): #var then var, or var then num -> wrong cases, reject
            sys.exit('Invalid variable followed by number or variable')
        
        elif isOp(tempstack[0]) and not isOp(tempstack[1]): # something like -3 or +56, or +x, -x -> add to output
            outputstack.append(tempstack.pop(0))
            if outputstack[-1] == ')': #check the operator just popped off for special cases like (5/7)x
                outputstack.append('*')
        
        #this is going to be a complete clusterfuck
        elif isOp(tempstack[0]) and isOp(tempstack[1]): # Two operators following each other.
             
             samepatternops = ['^','*','/','+','-','('] #list of ops that have the same action/patterns carried out after them
             
             # Get rid of special cases first
             if '+' in tempstack and '-' in tempstack: # you have either +- or -+ as the operators
                 del tempstack[0:] #clear tempstack eithout deleting it
                 tempstack.append('-') #since +- and -+ both reduce to - this removes unary operators, woot!
                 
             elif tempstack[0] == tempstack[1]: # duplicated operator, e.g. ++, **, --
                 if '-' in tempstack: # you have --, which is a +
                     del tempstack[0:]
                     tempstack.append('+')
                 elif '(' in tempstack or ')' in tempstack: #you have (( or ))
                     outputstack.append(tempstack.pop(0))
                 else:
                     outputstack.pop(0) #assume human error and remove the duplicated operator
             
             elif tempstack[0] in samepatternops: #all these depend on the 2nd operator, not first, to decide which action to take
                 if tempstack[1] == '+': # something like 2^+3x, or 2*+3, or 2/+3 - unary plus. Remove unary op
                     tempstack.pop()
                 elif tempstack[1] == '-': #something like 2^-3x or 2*-3 or 2/-3 - unary minus = convert to neg
                     outputstack.append(tempstack.pop(0))
                     tempstack[0] = 'neg()' #note how its outputstack[0] now due to the first element being removed
                 elif tempstack[1] == '(': # 3^(67x), 3*(67x), 3/(67x), can add the op to the output
                     outputstack.append(tempstack.pop(0))
                 else:
                     a = 'Operator followed by invalid operator. Specifically ' + tempstack[0] + ' and ' + tempstack[1]
                     sys.exit(a)
         
             elif tempstack[0] == ')': #like )+ or )^
                 outputstack.append(tempstack.pop(0)) #can be followed by anything, so throw it onto the output
         
             elif tempstack[0] == '(' and tempstack[1] == ')':
                 outputstack.append(tempstack.pop(0)) #empty brackets, but this could work anyway
         
        else:
            sys.exit('Something really fucked up')
    
    outputstack.append(tempstack.pop(0)) #add in the remaining variable left in temp at the end
    
    return outputstack

def convertToRPN (input): #Shunting-yard algorithm. Don't bother trying to figure it out, go to wiki
    inputstack = tokenizer(input)
    outputstack = []
    operatorstack = []
    
    for i in inputstack:
        if not isOp(i): #means it's either a number or a variable
            outputstack.append(i)
        else:
            if i == '(':
                operatorstack.append(i)
            elif i == ')':
                while operatorstack[-1] != '(':
                    outputstack.append(operatorstack.pop(-1))
                operatorstack.pop(-1)
            elif not operatorstack:
                operatorstack.append(i)
            else:
                new = returnOpDetails(i) #Avoid looping over this for minor speed boost
                while operatorstack:
                    if operatorstack[-1] == '(': #if ( is on the top, don't bother comparing
                        operatorstack.append(i)
                        break
                    else:
                        old = returnOpDetails(operatorstack[-1])
                    
                    if new[1] == 'l' and new[0] <= old[0]:
                        outputstack.append(operatorstack.pop(-1))
                        if not operatorstack: #if that's the last one in the operator stack, add new one
                            operatorstack.append(i)
                            break
                    elif new[1] == 'r' and new[0] < old[0]:
                        outputstack.append(operatorstack.pop(-1))
                        if not operatorstack: #same as above
                            operatorstack.append(i)
                            break
                    else: #all good, add new one
                        operatorstack.append(i)
                        break
    
    while operatorstack:
        outputstack.append(operatorstack.pop(-1))

    return outputstack

def convertFromRPN (input, low, upp): #Should convert postfix notation back into infix. Recursive function??
    postfix = input[:]
    infix = []
    
    if isOp(postfix[upp]):
        
        headop = returnOpDetails(postfix[upp]) #returns operator details
        
        if headop[2] == 2: #means it's a binary operator
            
            #See notes above the derive() function for explanation
            firstinfix = convertFromRPN(postfix,low,upp-2-grasp(postfix,upp-1)) #find the infix form of the first head
            secondinfix = convertFromRPN(postfix,upp-1-grasp(postfix,upp-1),upp-1) #find the infix form of the second head
            fi,si = firstinfix, secondinfix
            
            if isOp(postfix[upp-2-grasp(postfix,upp-1)]):
                firstop = returnOpDetails(postfix[upp-2-grasp(postfix,upp-1)])
                
                if headop[0] > firstop[0]:
                    infix.append('(')
                    infix.extend(fi)
                    infix.append(')')
                else:
                    infix.extend(fi)
            else:
                infix.extend(fi)
            
            infix.append(postfix[upp])
                
            if isOp(postfix[upp-1]):
                secondop = returnOpDetails(postfix[upp-1])
            
                if (headop[0] > secondop[0]) or secondop[1] == 'r':
                    infix.append('(')
                    infix.extend(si)
                    infix.append(')')
                else:
                    infix.extend(si)
            else:
                infix.extend(si)

        elif headop[2] == 1: #means it's a unary operator
            
            firstinfix = convertFromRPN(postfix,low,upp-1) #find the infix form of the only head
            fi = firstinfix
            
            infix.append(postfix[upp])
            infix.append('(')
            infix.extend(fi)
            infix.append(')')
    else:
        infix.extend(postfix[low:upp+1])
    
    return infix
########################AWESOMENESS#################################
# The following pretty much follows: yujor.fon.rs/pdfs/Vol11No1-5.pdf

#The following returns the grasp of input[index]
#This is the number elements before it that form operands with input[index]
#I think this pretty much means arity
#NOTE TO SELF: OPERATORS CAN BE OPERANDS TO ANOTHER OPERATOR

#If input[index] is a variable or constant, it's essentially a 0-ary operator (an operator with no operands)
#Hence grasp would be 0

#Counter version: OM's idea. Not broken like the old recursive one.
def grasp (input, index=1000):
    graspcounter = 0 #keeps track of the grasp
    poscounter = 0 #keeps a track of the position
    
    reversed = input[:index+1] #takes everything before (and including) the expression at index
    reversed.reverse() #since lists are easier to read left to right
    
    for i in reversed:
        if isOp(i):
            graspcounter += returnOpDetails(i)[2] # returns the grasp of each, allowing for unary operators
        if poscounter == graspcounter:
            return graspcounter

        poscounter += 1 #add 1 to the position from start

# Following function works out the left grasp bound, i.e. the left-most operand affected by an operator

def leftGraspBound (input,index):
    return index - grasp(input, index)

#Derive function
#From Lemma 1.1 in the above-mentioned paper for a binary operator postfix[i]:
#op_1 = postfix[i-1]
#op_2 = postfix[i-2]

#grasp| First Head         || Second Head
#index| upp-2-grasp[upp-1] || upp-1
#from | low                || upp-1-grasp[upp-1]
#to   | upp-2-grasp[upp-1] || upp-1

#For a unary operator:
#op_1 = postfix[i-1]
#index at upp-1
#grasp from low to upp-1

def derive(function, low, upp):
    postfix = function[:] #use same notation as the paper
    derivat = [] #where the final derivative will be stored
    
    if isOp(postfix[upp]):
        
        nary = returnOpDetails(postfix[upp])[2] #returns grasp and hence whether operator is binary or unary
        
        if nary == 2: #means it's a binary operator
            
            #See above table for the following to make sense
            firsthead = postfix[low:upp-1-grasp(postfix,upp-1)] #due to python's method of list splicing, upp-1 rather than upp-2 is used -> u
            firstderivative = derive(postfix,low,upp-2-grasp(postfix,upp-1)) #note how here we go back to the notation in the chart -> u'
            fh,fd = firsthead, firstderivative #become i'm that lazy
        
            secondhead = postfix[upp-1-grasp(postfix,upp-1):upp] #same as above, upp rather than upp-1 for the upper bound -> v
            secondderivative = derive(postfix,upp-1-grasp(postfix,upp-1),upp-1) #note how here we go back to the notation in the chart -> v'
            sh,sd = secondhead,secondderivative

        elif nary == 1: #means it's a unary operator
            
            firsthead = postfix[low:upp] #same as in binary, list splicing means upp instead of upp-1 is used
            firstderivative = derive(postfix,low,upp-1) #same as binary, go back to proper notation
            fh, fd = firsthead, firstderivative

        if postfix[upp] == "-" or postfix[upp] == "+": #simplest situation, we have uv+/-, we turn it to u'v'+/-
            
            if fd == ['0'] and sd == ['0']: #both null
                derivat.append('0') #add a null to final
            elif fd != ['0'] and sd == ['0']: #second derivative in null, we can just forget about it
                derivat.extend(fd) #all we need is the first derivative then
            elif fd == ['0'] and sd != ['0']: #first derivative is null, take note of unary minus
                derivat.extend(sd) #so we can just add in the second derivative
                if postfix[upp] == '-': #means that we have -v'
                    derivat.append('neg()')
            else:
                derivat.extend(fd) #add first derivative to final -> u'
                derivat.extend(sd) #add second derivative to final -> u'v'
                derivat.append(postfix[upp]) #add op at the end -> u'v'+/-
        
        elif postfix[upp] == "*" or postfix[upp] == "/": #here we use the product rule to differentiate -> u'v + uv', or the quotient rule -> (u'v - v'u)/v^2
            
            #next block deals with u'v
            if fd == ['0'] or sh == ['0']: #one of u'v is equal to 0 -> u'v == 0
                pass #forget it exists, and later add a unary operator if needed
            elif fd == ['1']: # u' is 1 so we have 1v* == v
                derivat.extend(sh)
            elif sh == ['1']: # v is 1 so we have 1u'* == u'
                derivat.extend(fd)
            else:
                derivat.extend(fd) #add u' to final
                derivat.extend(sh) #add v to final. now it has u'v in it
                derivat.append("*") #add operator to the final. final now has u'v* in it
            
            #next block deals with v'u
            if fh == ['0'] or sd == ['0']: #one of uv' is null -> v'u == 0
                pass #we can just ignore it even exists, and then later avoid adding an operator
            elif fh == ['1']: # u is 1 so we have 1v'* == v'
                derivat.extend(sd)
            elif sd == ['1']: # v' is 1 so we have 1u* == u
                derivat.extend(fh)
            else:
                derivat.extend(sd) # u'v*v'
                derivat.extend(fh) # u'v*v'u
                derivat.append("*") # u'v*v'u*
            
            #this block then does the last part of both rules
            if postfix[upp] == "*": #product rule
                if fd != ['0'] and fh != ['0'] and sd != ['0'] and sh != ['0']: #Only add in an operator if we haven't already skipped a zero somewhere
                    derivat.append("+") # u'v*v'u*+
            else: #quotient rule
                if fd != ['0'] and sh != ['0'] and fh != ['0'] and sd != ['0']: #Same as above, only add if nothing has equalled 0 so far
                    derivat.append("-") # u'v*v'u*-
                elif (fd == ['0'] or sh == ['0']) and (fh != ['0'] and sd != ['0']): #if u'v is 0 but v'u isn't, add a unary negative for v'u
                    derivat.append("neg()") #v'u*neg()
                
                if sh == ['1']: #if sh, and hence v, == 1, then you're dividing by 1, so it can be skipped
                    pass
                elif (fd == ['0'] or sh == ['0']) and (fh == ['0'] or sd == ['0']): #we have u'v and v'u both as zero, so we are dividing 0 by something
                    derivat.append('0')
                else:
                    derivat.extend(sh) #u'v*v'u*-v
                    derivat.append("2") # u'v*v'u*-v2
                    derivat.append("^") # u'v*v'u*-v2^
                    derivat.append("/") # u'v*v'u*-v2^/

        elif postfix[upp] == "^": #use the chain rule. (f(x))^n = nf'(x)(f(x))^(n-1) where f(x) is u (and so fh) and n is v (and so sh)
            if varname not in sh: #checks that we don't have something to the power of x -> not yet implemented
                if sh != ['0'] and fh != ['0'] and fd != ['0']: #make sure that none of the things being multiplied are equal to 0
                    
                    if sh == ['1'] and fd == ['1']: #both n and f'(x) are 1, so ignore
                        pass
                    elif sh == ['1']: # n is equal to 1, we can ignore it
                        derivat.extend(fd)
                    elif fd == ['1']: # f'(x) is equal to 1, we can ignore it
                        derivat.extend(sh)
                    else:
                        derivat.extend(sh) #send the second head to the the final -> now it contains n
                        derivat.extend(fd) # nf'(x)
                        derivat.append("*") #nf'(x)*

                    exponent = sh[:] #just a copy which is later changed
                    
                    #TODO call an RPN evaluator for the power in case it's in the form 2 3 *
                    if exponent[-1] == 'neg()': #if we have a negative power such as ^-1 or ^-2, it's in the form [....,neg()]
                        exponent[0] = str(int(exponent[0]) + 1) #to take away one from the power in this case, can just add 1 without changing the neg()
                    else:
                        exponent = [str(int(exponent[0]) - 1)] #positive power, so we take away one.
                    
                    if exponent[0] == '0': #anything to the power of 0 is 1, so we can ignored it
                        pass
                    elif exponent[0] == '1': #anything to the ^1 is itself, so we just add in f(x)
                        derivat.extend(fh)
                    else:
                        derivat.extend(fh) #nf'(x)*f(x) usually, or as it may be, nf(x), f'(x)f(x) or just f(x)
                        derivat.extend(exponent) #nf'(x)*f(x)(n-1)
                        derivat.append("^") #nf'(x)*f(x)(n-1)^
                    
                    if exponent[0] != '0' or (sh != ['1'] and fd != ['1']): #Check that some forms of nf'(x) or f(x)(n-1)^ exist
                        derivat.append("*") #nf'(x)*f(x)(n-1)^*
                else:
                    derivat.append('0')
            else:
                print 'Exponents of x are currently not supported'
        
        elif postfix[upp] == "neg()":#simple f(x)neg() goes to f'(x)neg()
            if fd == ['0']: #f'(x) is 0, so we can forget about the neg()
                derivat.append('0')
            else:
                    derivat.extend(fd)
                    derivat.append('neg()')
        else:
            sys.exit('fail one')
        
    elif isInt(postfix[upp]):
        derivat.append('0') #all numbers derive to 0
    
    elif isVar(postfix[upp]):
        derivat.append('1') # a variable on it's own differentiates to var^0, which is 1
    
    else:
        sys.exit('fail two')
    
    return derivat
    
    
# Take the input

function = cleanInput(raw_input('please enter your equation here:\n'))
variablename = setMainVar(cleanInput(raw_input("please enter that you're differentiating with respect to:\n")))


##########################TESTCASES#################################

testcases = ['1+1', '-2+x', '6+78-847', '1+x', '748x^2', '5/(374+45x)', '(1+x)/(1-x)', '7x^10 - (54/34x)', '1+3(x+2)', '2x*(-2)', 'x^6 + 98x^2 + (5/7)x^4', '((x+x^(-1))^2 +9 )^3', '(x/5^x)*(2^((x^(-1))/8^x))', '2^((-45) + 2x)', '(x^6)^(x^(-1)) + 23^x']

#for i in testcases:
    #print "this is testcase number " + str(testcases.index(i))
    #print i
    #print tokenizer(cleanInput(i))
    #print convertToRPN(cleanInput(i))
    #print grasp(convertToRPN(cleanInput(i)))
    #try:
        #print grasp(convertToRPN(cleanInput(i)), convertToRPN(cleanInput(i)).index('neg()'))
    #except ValueError:
        #pass
    #print "\n"

start = time.time()
for i in testcases:
    print "this is testcase number " + str(testcases.index(i))
    print i
    a = convertToRPN(cleanInput(i))
    print ' '.join(k for k in a)
    derivative = derive(a, 0, -1)
    print ' '.join(j for j in derivative)
    if testcases.index(i) not in [12,13,14]: #testcases 12,13,14 die due to being incomplete
        print ''.join(l for l in convertFromRPN(derivative, 0, -1))
    print "\n"
print time.time()-start