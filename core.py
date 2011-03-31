from __future__ import division
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

def returnOpDetails(operator): #returns list, [0] is precedence, [1] is associativity, [2] is grasp, [3] is commutativity
    
    optable = {'^':[4,'r',2,False], 'neg()':[3,'r',1,False], '*':[3, 'l',2,True], '/':[3,'l',2,False], '+':[2,'l',2,True], '-':[2,'l',2,False]}
    
    return optable[operator]

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

def convertFromRPN (input, low=0, upp=-1): #Should convert postfix notation back into infix.
    postfix = input[:]
    infix = []
    
    if isOp(postfix[upp]):
        
        headop = returnOpDetails(postfix[upp]) #returns operator details for the rightmost operator
        
        if headop[2] == 2: #means it's a binary operator
            
            #See notes above the derive() function for explanation
            firstinfix = convertFromRPN(postfix,low,upp-2-grasp(postfix,upp-1)) #find the infix form of the first head
            secondinfix = convertFromRPN(postfix,upp-1-grasp(postfix,upp-1),upp-1) #find the infix form of the second head
            fi,si = firstinfix, secondinfix
            
            if isOp(postfix[upp-2-grasp(postfix,upp-1)]): #checks whether the rightmost character of the first head is an operator
                firstop = returnOpDetails(postfix[upp-2-grasp(postfix,upp-1)])
                
                if headop[0] > firstop[0]: #if the precedence of the current operator being worked on is larger than that of one the first head, then we need brackets.
                    infix.append('(')      #for example, we have * as headop and + as firstop
                    infix.extend(fi)
                    infix.append(')')
                else:
                    infix.extend(fi)
            else: #rightmost head is just a number, so no brackets needed
                infix.extend(fi)
            
            infix.append(postfix[upp]) # so we have the first infix in there, add in the operator
                
            if isOp(postfix[upp-1]):
                secondop = returnOpDetails(postfix[upp-1])
            
                if headop[0] > secondop[0]: #same as above pretty much
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
            
            infix.append(postfix[upp]) #since it's unary, operator goes first.
            
            if len(fi) > 1: #only add in brackets if there is a use for them. something like 3 24 x * + neg() which goes to neg()(24x+1)
                infix.append('(')
                infix.extend(fi)
                infix.append(')')
            else: #we have something like 1 neg(), which should just go to neg()1 rather than neg()(1)
                infix.extend(fi)
    else:
        infix.extend(postfix[low:upp+1])
    
    return infix
    
def mapRPN(input,low=0,upp=-1,depth=0): #this should create a "map" of the rpn to help my understanding
    postfix = input[:]
    output = []
    
    if isOp(postfix[upp]):
        
        nary = returnOpDetails(postfix[upp])[2] #returns grasp and hence whether operator is binary or unary
        
        opnames = {'+':'addition','-':'subtraction','*':'multiplication','/':'division','^':'exponiation','neg()':'negation'}
        
        if nary == 2: #means it's a binary operator
            
            #See above table above the derive() function for this to make sense.
            firsthead = postfix[low:upp-1-grasp(postfix,upp-1)] #due to python's method of list splicing, upp-1 rather than upp-2 is used
            firstmap = mapRPN(postfix,low,upp-2-grasp(postfix,upp-1),depth+1) #note how here we go back to the notation in the chart
            fh,fm = firsthead, firstmap
        
            secondhead = postfix[upp-1-grasp(postfix,upp-1):upp] #same as above, upp rather than upp-1 for the upper bound
            secondmap = mapRPN(postfix,upp-1-grasp(postfix,upp-1),upp-1,depth+1) #note how here we go back to the notation in the chart
            sh,sm = secondhead, secondmap
            
            recurlist = []
            recurlist.append(str(depth)+":"+opnames[postfix[upp]]+":"+str(fh)+"and"+str(sh))
            recurlist.append(fm)
            recurlist.append(sm)
            output.extend(recurlist)

        elif nary == 1: #means it's a unary operator
            
            firsthead = postfix[low:upp] #same as in binary, list splicing means upp instead of upp-1 is used
            firstmap = mapRPN(postfix,low,upp-1,depth+1) #same as binary, go back to proper notation
            fh, fm = firsthead, firstmap
            
            recurlist = []
            recurlist.append(str(depth)+":"+opnames[postfix[upp]]+":"+str(fh))
            recurlist.append(fm)
            output.extend(recurlist)
    
    else:
        output.append(str(depth)+":number:"+str(postfix[low:upp+1][0]))
        
    return output

def shiftVariableRPN(input, low=0, upp=-1): #takes the RPN and attempts to shift variables as far up and then as far right as possible
    postfix = input[:]
    output = []
    
    if not isOp(postfix[upp]): #no ops, return input
        output.extend(postfix[low:upp+1])
    else: #we have an op, and so head

        headop = returnOpDetails(postfix[upp]) #returns op details for the last operator in the postfix
        
        if headop[2] == 2: #means it's a binary operator

            firstshift = fs = shiftVariableRPN(postfix,low,upp-2-grasp(postfix,upp-1)) #shift all the variables up to that point to the right, return head
            secondshift = ss = shiftVariableRPN(postfix,upp-1-grasp(postfix,upp-1),upp-1) #ditto as above, return head
            #print "before:",fs,ss

            if varname in fs and varname not in ss and headop[3]: #we have a var in the first head, not the second, and function is commutative
                fs,ss = ss,fs #so we switch the heads around
            
            firstop = fo = fs[-1] if isOp(fs[-1]) else '' #operator at the top of head 1.
            secondop = so = ss[-1] if isOp(ss[-1]) else '' #operator at the top of head 2
            
            #print "after:",fs,ss
            #print postfix[upp],fo,so
            if postfix[upp] == "*" and (fo == "*" or so == "*"): #two multiplications, so we can promote variable up or to the right
                
                if fo == "*" and so == "*": #multiplications in both heads, find right heads, check for vars, take var to the right (or we have two integers, take them right)
                    
                    firstshiftleft, firstshiftright = fsl,fsr = fs[0:-2-grasp(fs,-2)],fs[-2-grasp(fs,-2):-1] #hard coded left and right heads of the right head
                    secondshiftleft, secondshiftright = ssl, ssr = ss[0:-2-grasp(ss,-2)],ss[-2-grasp(ss,-2):-1] #hard coded left and right heads of the left head
                    #print "fsl: ",fsl,"fsr: ",fsr,"ssl: ",ssl,"ssr: ",ssr
                    
                    if varname not in fsl and varname not in ssl:
                        fsr,ssl = ssl,fsr
                    
                    fs = fsl+fsr+['*']
                    ss = ssl+ssr+['*']
                
                elif fo == "*" and not secondop: #find right head of fs, switch with left head ss if there's a variable there
                    
                    firstshiftleft, firstshiftright = fsl,fsr = fs[0:-2-grasp(fs,-2)],fs[-2-grasp(fs,-2):-1] #hard coded left and right heads of the right head
                    #print "fsl: ",fsl,"fsr: ",fsr,"ss: ",ss
                    if varname in fsr:
                        fsr,ss = ss,fsr
                    
                    fs = fsl+fsr+['*']
                    
                elif so == "*" and not firstop: #find right head of ss, switch with fs
                    
                    secondshiftleft, secondshiftright = ssl, ssr = ss[0:-2-grasp(ss,-2)],ss[-2-grasp(ss,-2):-1] #hard coded left and right heads of the left head
                    #print "ssl:",ssl,"ssr: ",ssr,"fs:",fs
                    if varname in ssr:
                        ssr,fs = fs,ssr
                    
                    ss = ssl+ssr+['*']
            
                if varname in fs and varname not in ss and headop[3]: #repeat this with the new stuff
                    fs,ss = ss,fs

            output.extend(fs)
            output.extend(ss)
            output.append(postfix[upp]) #add the operator at the end
            
        elif headop[2] == 1: #means it's a unary operator
            firsthead = fh = postfix[low:upp] #same as in binary, list splicing means upp instead of upp-1 is used
            
            output.extend(fh)
            output.append(postfix[upp])

    return output
    
def evaluateRPN(input, fractions=True): #take numbers or fractions and give a result. DOES NOT TAKE VARIABLES
    original = input[:]
    output = []

    for i in original:
        if not isOp(i): #must be a number
            output.append(i)
        else: #must be an operator
            opdetails = returnOpDetails(i)
 
            #this is all called later. note how x and y are reverse to take into account not commutative operators. example:
            # 2 3 ^ in the original. this is 2^3 in infix. output contains 2 3. output.pop() gives us 3 and then 2, so x = 3 and y = 2. so we do y**x
            functionmap = {'+':lambda x,y: y+x, '-':lambda x,y: y-x, '*':lambda x,y: y*x, '/':lambda x,y: y/x, '^':lambda x,y: y**x, 'neg()':lambda x: -x}
            
            #every input is modelled as two fractions: x/a and y/z. z and a are by default 1, allowing for normal numbers to be passed through
            functionmapdiv = {'+':lambda x,y,z=1,a=1: [str(x*z+y*a)]+[str(z*a)]+['/'], '-':lambda x,y,z=1,a=1: [str(x*z-y*a)]+[str(z*a)]+['/'], '*':lambda x,y,z=1,a=1: [str(x*y)]+[str(z*a)]+['/'], '/':lambda x,y,z=1,a=1 :[str(x*z)]+[str(a*y)]+['/'], '^':lambda x,y,z=1,a=1: [str(int(x**(y/z)))]+[str(int(a**(y/z)))]+['/'],'neg()':lambda x,a=1: [str(-x)]+[str(a)]+['/']}

            #the floats are there because sometimes you get decimals points passed through, and you need to go str->float->int
            if opdetails[2] == 2: #binary operator
                
                if not fractions or (fractions and (i != '/' and '/' not in output)): #either we don't care about fractions, or we do but we don't have any and the current op isn't one
                    value = functionmap[i](float(output.pop()),float(output.pop())) #this is the operation in functionmap performed on the top two chars popped off the output
                    value = int(value) if int(value) == value else value #avoid passing floats if possible
                    output.append(str(value)) #add the value back in as a string 
                else:
                    # We have 4 possible inputs coming in (bottom of output stack is left, top is right):
                    #1 (int)(int)(op) in which case we just do the normal operations
                    #2 (div)(int)(op) in which case we need to split the div into two (int)
                    #3 (int)(div)(op) in which case we need to split the div into two (int)
                    #4 (div)(div)(op) in which case both need to be split and we get 4 (int) altogether
                    
                    var1 = output.pop()
                    if var1 == '/': #check for possibility 3 or 4
                        var1,var2 = output.pop(),output.pop() #3 and 4 mean that the first two ints are the next two things on the stack
                        
                        var3 = output.pop()
                        if var3 == '/': #check for possibility 4
                            var3,var4 = output.pop(),output.pop() # 4 means the next two ints are at the top of the stack
                            value = functionmapdiv[i](int(var4),int(var2),int(var1),int(var3)) #the two fractions we had were var2/var1 and var4/var3
                        else: #possibility 3
                            value = functionmapdiv[i](int(var3),int(var2),int(var1)) #fraction is var2/var1 and int is var3

                    else:
                        var2 = output.pop()
                        if var2 == '/': #check for possibility 2
                            var2,var3 = output.pop(),output.pop()
                            value = functionmapdiv[i](int(var3),int(var1),a=int(var2)) #fraction is var3/var2 and int is var1
                        else: #possibility 1
                            value = functionmapdiv[i](int(var2),int(var1)) #ints are var1 and var2

                    output.extend(value)
                    
            elif opdetails[2] == 1: #unary operator
                
                if not fractions or (fractions and (i != '/' and '/' not in output)): #either we don't care about fractions, or we do but we don't have any and the current op isn't one
                    value = functionmap[i](float(output.pop()))
                    value = int(value) if int(value) == value else value #avoid passing floats if possible
                    output.append(str(value)) #add the value back in as a single string
                else:
                    #only 2 possibilities:
                    #1 (int)(op) in which case we just do normal operations
                    #2 (div)(op) in which case we split into two
                    
                    var1 = output.pop()
                    if var1 == '/': #check for possibility 2
                        var1,var2 = output.pop(),output.pop()
                        value = functionmapdiv[i](int(var2),int(var1)) #fraction is var2/var1
                    else:
                        value = functiomapdiv[i](int(var1)) #int is var1
                    
                    output.extend(value)
    
    return output

def simplifyRPN(input, low=0, upp=-1): #takes RPN with numbers and variables and simplifies
    postfix = input[:]
    output = []
    
    if varname not in postfix: #no vars at all, we can just do the evalRPN function
        output.extend(evaluateRPN(postfix))
    elif not isOp(postfix[upp]): #we have a variable, but no operators, so we just return the input
        output.extend(postfix[low:upp+1])
    else: #we have a var and an operator -> function, which we can then split into heads

        headop = returnOpDetails(postfix[upp]) #returns op details for the last operator in the postfix
        
        if headop[2] == 2: #means it's a binary operator
            
            #See notes above the derive() function for explanation
            firsthead = fh = postfix[low:upp-1-grasp(postfix,upp-1)] #due to python's method of list splicing, upp-1 rather than upp-2 is used
            secondhead = sh = postfix[upp-1-grasp(postfix,upp-1):upp] #same as above, upp rather than upp-1 for the upper bound

            if varname in fh and varname not in sh: #we have a var in the first head, not the second
                firstsimp = fs = simplifyRPN(postfix,low,upp-2-grasp(postfix,upp-1)) #run recursively to see if any parts before simplify
                secondsimp = ss = evaluateRPN(sh) #doesn't have a variable so we can just use normal rpn evaluation

            elif varname not in fh and varname in sh: #we have a var in the second head, not the first
                firstsimp = fs = evaluateRPN(fh) #doesn't have a variable so we can just use normal rpn evaludation
                secondsimp = ss = simplifyRPN(postfix,upp-1-grasp(postfix,upp-1),upp-1) #run recursively to see if any bits before simplify
            
            else: #vars in both, no easy shortcuts to take
                firstsimp = fs = simplifyRPN(postfix,low,upp-2-grasp(postfix,upp-1))
                secondsimp = ss = simplifyRPN(postfix,upp-1-grasp(postfix,upp-1),upp-1)
            
            output.extend(fs)
            output.extend(ss)
            output.append(postfix[upp]) #add the operator at the end
            
        elif headop[2] == 1: #means it's a unary operator
            firsthead = fh = postfix[low:upp] #same as in binary, list splicing means upp instead of upp-1 is used
            
            firstsimp = fs = simplifyRPN(postfix,low,upp-1) #see if it can somehow be simplified internally

            output.extend(fs)
            output.append(postfix[upp])
    
    return output


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
    
    index = len(input)-1 if abs(index) > len(input) else index #if you ask for an index outside of the len of the input, it sets index to be the last char of input
    
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

def derive(function, low=0, upp=-1):
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

                    exponent = evaluateRPN(sh[:]) #should simplify any powers into a single number
                    exponent[0] = str(int(float(exponent[0])-1)) if int(float(exponent[0])-1) == float(exponent[0])-1 else str(float(exponent[0])-1) #take one from the power
                    # ^ since some powers may be divided, it's hard to predicted whether we have an int or float there
                    
                    if exponent[0][0] == '-': #it's a negative number -> unary minus
                        exponent[0] = exponent[0][1:] #remove the unary minus, and keep it all a list
                        exponent.append('neg()') #add in unary minus at the end
                    
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

testcases = ['1+1', '-2+x', '6+78-847', '1+x', '748x^2', '5/(374+45x)', '(1+x)/(1-x)', '7x^10 - (54/34x)', '1+3(x+2)', '2x*(-2)', 'x^6 + 98x^2 + (5/7)x^4', '((x+x^(-1))^2 +9 )^3', '(x/5^x)*(2^((x^(-1))/8^x))', '2^((-45) + 2x)', '(x^6)^(x^(-1)) + 23^x', 'x^2^3^4']

#testcases = ['5+7','(5/7)+9','9+(5/7)','(6/9)-(5/7)','(1/3)*(8/16)','(1/7)/(4/5)','(1/7)^4']

#for i in testcases:
    
    #rpn = convertToRPN(cleanInput(i))
    #print i
    #print ' '.join(k for k in evaluateRPN(rpn))

start = time.time()
for i in testcases:
    print "this is testcase number " + str(testcases.index(i))
    print i
    a = convertToRPN(cleanInput(i))
    #print ' '.join(k for k in a)
    derivative = derive(a)
    print "derivative in rpn: ",' '.join(j for j in derivative)
    #try:
        #mapped = mapRPN(derivative,0,-1)
        #print mapped
    #except:
        #pass
    if testcases.index(i) not in [0,1,2,3,8,12,13,14]: #testcases 12,13,14 die due to being incomplete
        print "rpn simplified: ",' '.join(h for h in simplifyRPN(derivative))
        print ''.join(d for d in convertFromRPN(simplifyRPN(derivative)))
        print ''.join(r for r in convertFromRPN(simplifyRPN(shiftVariableRPN(shiftVariableRPN(derivative)))))
    print "\n"
print time.time()-start
