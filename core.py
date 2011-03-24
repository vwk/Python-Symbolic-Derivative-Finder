import sys

def cleanInput(input): #standardises input
    
    return input.replace(' ', '').replace('**','^').lower()

def setMainVar(input): #Allows for any variable, not just x to be used.
                       #Can later allow for multiple variables? #24-03-11 15:22PM WTF did I mean here?
    global varname
    varname = input

def isOp (input):
    oplist = ['^', '*', '/', '+', '-', '(', ')']
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
    
    optable = {'^':[4,'r',2], '*':[3, 'l',2], '/':[3,'l',2], '+':[2,'l',2], '-':[2,'l',2]}
    
    return optable[operator]

#REFERENCE IMPLEMENTATION
#OVERLY VERBOSE, OVER-COMPLICATED AND OVER-COMMENTED
#BUT IT WORKS GOOD WITH THE CRAZIEST OF FUNCTIONS

def tokenizer (input): #Splits function into its constituent pieces

    inputstack = list(input) #wow this actually does a lot of the hard work for you
    outputstack = []
    tempstack = []
    
    #checks that the input makes some sort of sense initially
    if isOp(inputstack[0]):
        if inputstack[0] == '-': #Must be a starting unary minus. Add in 0+ at the start. HACKY but fun
            inputstack.insert(0, '+')
            inputstack.insert(0, '0')
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
                 elif tempstack[1] == '-': #something like 2^-3x or 2*-3 or 2/-3 - unary minus = ask to re-enter with brackets
                     if tempstack[0] == '(':
                         outputstack.append(tempstack.pop(0))
                         outputstack.append('0') # make the unary minus into binary
                     else:
                         sys.exit('Please re-enter unary negative in brackets')
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
        elif isOp(i):
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
    
########################AWESOMENESS#################################
# The following pretty much follows: yujor.fon.rs/pdfs/Vol11No1-5.pdf

#The following returns the grasp of input[index]
#This is the number elements before it that form operands with input[index]
#I think this pretty much means arity
#NOTE TO SELF: OPERATORS CAN BE OPERANDS TO ANOTHER OPERATOR

#If input[index] is a variable or constant, it's essentially a 0-ary operator (an operator with no operands)
#Hence grasp would be 0

#Counter version: OM's idea. Not broken like the old recursive one.
def grasp (input, index=100):
    graspcounter = 0 #keeps track of the grasp
    poscounter = 0 #keeps a track of the position
    
    reversed = input[:index+1] #takes everything before (and including) the expression at index
    reversed.reverse() #since lists are easier to read left to right
    
    for i in reversed:
        if isOp(i):
            graspcounter += 2 # binary operators
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

def derive(function, low, upp):
    postfix = function[:] #use same notation as the paper
    derivat = [] #where the final derivative will be stored
    
    if isOp(postfix[upp]):
        
        #See above table for the following to make sense
        firsthead = postfix[low:upp-1-grasp(postfix,upp-1)] #due to python's method of list splicing, upp-1 rather than upp-2 is used -> u
        firstderivative = derive(postfix,low,upp-2-grasp(postfix,upp-1)) #note how here we go back to the notation in the chart -> u'
        fh,fd = firsthead, firstderivative #become i'm that lazy
        
        secondhead = postfix[upp-1-grasp(postfix,upp-1):upp] #same as above, upp rather than upp-1 for the upper bound -> v
        secondderivative = derive(postfix,upp-1-grasp(postfix,upp-1),upp-1) #note how here we go back to the notation in the chart -> v'
        sh,sd = secondhead,secondderivative

        if postfix[upp] == "-" or postfix[upp] == "+": #simplest situation, we have uv+/-, we turn it to u'v'+/-
            
            if fd == ['0'] and sd == ['0']: #both null
                derivat.append('0') #add a null to final
            elif fd != ['0'] and sd == ['0']: #second derivative in null, we can just forget about it
                derivat.extend(fd) #all we need is the first derivative then
            elif fd == ['0'] and sd != ['0'] and postfix[upp] == "+": #first derivative is null, no fear of unary minus
                derivat.extend(sd) #so we can just add in the second derivative
            else:
                derivat.extend(fd) #add first derivative to final -> u'
                derivat.extend(sd) #add second derivative to final -> u'v'
                derivat.append(postfix[upp]) #add op at the end -> u'v'+/-
        
        elif postfix[upp] == "*" or postfix[upp] == "/": #here we use the product rule to differentiate -> u'v + uv', or the quotient rule -> (u'v - v'u)/v^2
            derivat.extend(fd) #send the first head to be derived, add to final. Now final has u' in it
            derivat.extend(sh) #add the second head to the final. final now has u'v in it
            derivat.append("*") #add operator to the final. final now has u'v* in it
            
            derivat.extend(sd) # u'v*v'
            derivat.extend(fh) # u'v*v'u
            derivat.append("*") # u'v*v'u*
            
            if postfix[upp] == "*": #product rule
                derivat.append("+") # u'v*v'u*+
            else: #quotient rule
                derivat.append("-") # u'v*v'u*-
                
                derivat.extend(sh) #u'v*v'u*-v
                derivat.append("2") # u'v*v'u*-v2
                derivat.append("^") # u'v*v'u*-v2^
                derivat.append("/") # u'v*v'u*-v2^/
        
        elif postfix[upp] == "^": #use the chain rule. (f(x))^n = nf'(x)(f(x))^(n-1) where f(x) is u and n is v
            if varname not in sh: #checks that we don't have something to the power of x -> not yet implemented
                derivat.extend(sh) #send the second to the the final -> now it contains n
                derivat.extend(fd) # nf'(x)
                derivat.append("*") #nf'(x)*
                
                derivat.extend(fh) #nf'(x)*f(x)
                
                exponent = sh[:] #just a copy which is later changed
                
                #HACK HACK HACK in order to deal with negative powers (since i've been avoiding unary minus)
                #Best thing would be to call an RPN evaluator here to deal with it
                if isOp(exponent[-1]):
                    exponent = 0 - int(exponent[1])
                else:
                    exponent = int(exponent[0])
                    
                derivat.append(str(exponent-1)) #nf'(x)*f(x)(n-1)
                derivat.append("^") #nf'(x)*f(x)(n-1)^
                
                derivat.append("*") #nf'(x)*f(x)(n-1)^*
            else:
                print 'Exponents of x are currently not supported'
        
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

function = cleanInput(raw_input('please enter your equation here with x as the subject:\n'))
variablename = setMainVar(cleanInput(raw_input("please enter that you're differentiating with respect to:\n")))


##########################TESTCASES#################################

testcases = ['1+1', '-2+x', '6+78-847', '1+x', '748x^2', '5/(374+45x)', '(1+x)/(1-x)', '7x^10 - (54/34x)', '1+3(x+2)', '2x*(-2)', '((x+x^(-1))^2 +9 )^3', '(x/5^x)*(2^((x^(-1))/8^x))', '2^((-45) + 2x)', '(x^6)^(x^(-1)) + 23^x']


for i in testcases:
    print "this is testcase number " + str(testcases.index(i))
    print i
    a = convertToRPN(cleanInput(i))
    print ' '.join(k for k in a)
    derivative = derive(a, 0, -1)
    print ' '.join(j for j in derivative)
    print "\n"