from fractions import Fraction
import re

# A class for dealing with numbers
# All integers, decimals, and fractions create an instance of this class
# At the moment it just copies the fraction built-in class, no methods of its own
# TODO: rewrite the power method to not return a float if it can't find a rational
class num(Fraction):
    def __init__(self, number):
        super(num, self).__init__()

# A class for dealing with variables
# Pretty much just sets information, gives option to set a global var
# TODO: add some sort of method for implicit differentiation
class var:
    def __init__(self, variable):
        self.value = variable
    
    def __repr__(self):
        return 'var: ' + str(self.value)
    
    def setGlobalVar(self):
        global varname
        varname = self.value

# Class for operators
# Takes the operator, assigns details
class op:
    
    optable = {'sin':[5,'r',1,False],'cos':[5,'r',1,False],'tan':[5,'r',1,False],'^':[4,'r',2,False], 'neg':[3,'r',1,False], '*':[3, 'l',2,True], '/':[3,'l',2,False], '+':[2,'l',2,True], '-':[2,'l',2,False], '(':[None,None,None,None], ')':[None,None,None,None]}
 
    def __init__(self, operator):
        self.setOpDetails(operator)
    
    def __repr__(self):
        return 'op: ' + str(self.name)
    
    def setOpDetails(self,operator):
        
        #TODO find some sort of way to do this using map() or zip() or something
        self.name = operator
        self.precedence = self.optable[operator][0]
        self.associativity = self.optable[operator][1]
        self.grasp = self.optable[operator][2]
        self.commutativity = self.optable[operator][3]

# Takes a string, and tries to tell you what class it should belong to.
# Essentially performs the role of the old isOp, isInt and isVar stuff.
def stringIdentifier(string):
    #TODO: change this to regex so that we can add fractions
    try:
        temp = int(string)
        return 'num'
    except ValueError:
        pass
    
    oplist = ['sin','cos','tan', '^', 'neg', '*', '/', '+', '-', '(', ')']
    if string in oplist:
        return 'op'
    
    return 'var'

# A class for whole equations
# Takes a string as input, on creation of an instance tokenizes that string
# Holds both infix and rpn notations of the equation
class equation:
    def __init__(self, equation,form=0): #0 is infix, 1 is postfix/rpn
        if form == 0:
            self.infix = self.tokenize(equation)
            self.rpn = self.convertToRPN(self.infix)
        elif form == 1:
            self.rpn = equation #assume all rpn is already tokenized and in a list
            self.infix = self.convertFromRPN(self.rpn)
        
        self.generateInstances()

    #TODO: see if finditer rather than findall could reduce the amount of blanks found. Or find some better regex.
    def tokenize(self, equation):
        equation = self.addOperators(equation) #adds any implicit multiplications
        out = []
        print "equation:",equation
        findop = re.compile(r"(\W?)([()]?)(\d+|[a-zA-Z]+)([()]?)(\W?)") #create groups at operators
        
        a = re.findall(findop,equation)
        for i in a:
            for j in list(i): #NOTE: do I even need to convert to list here?
                if j: #get rid of all the empty values
                    out.append(j)
        print out
        return out
        
    def addOperators(self,equation):
        
        #mult1 = re.compile(r"(.*[\w])(?<!sin|cos|tan)(\(.+\).*)") # something like a(b), but keep in mind trig
        #mult2 = re.compile(r"(.*\(.+\))([\w].*)") # something like (a)b
        #mult3 = re.compile(r"(.*\(.+\))(\(.+\).*)") # (a)(b)
        #mult4 = re.compile(r"(.*[0-9]+)([a-zA-Z]+.*)") # 13a
        #neg = re.compile(r"(.+?[^\w)]+)-(.*)") # ^-2, (-x)
        
        if equation[0] == '-': #remove a starting unary minus
            equation = 'neg' + equation[1:]
        
        reglist = {r"(.*[\w])(?<!sin|cos|tan)(\(.+\).*)":'*', r"(.*\(.+\))([\w].*)":'*', r"(.*\(.+\))(\(.+\).*)":'*', r"(.*[0-9]+)([a-zA-Z]+.*)":'*', r"(.+?[^\w)]+)-(.*)":'neg'}
        
        for i,j in reglist.items():
            a = re.search(i,equation)
            if a:
                return self.addOperators(a.group(1)) + j + self.addOperators(a.group(2))
        
        return equation
    
    def generateInstances(self):
        temp = []
        funcmap = {'num':lambda x:num(x),'op':lambda x:op(x),'var':lambda x:var(x)}
        
        for i in self.infix:
            identity = stringIdentifier(i)
            temp.append(funcmap[identity](i))
        self.infix = temp
        
        #del temp[:]
        
        #for i in self.rpn:
            #identity = stringIdentifier(i)
            #temp.append(funcmap[identity](i))
        #self.rpn = temp
        
        print self.infix

    def convertToRPN(self,equation):
        pass
        


if __name__ == "__main__":
    
    testcases = ['1+1', '-2+x', '6+78-847', '1+x', '748x^2', '5/(374+45x)', '(1+x)/(1-x)', '7x^10-(54/34x)', '1+3(x+2)', '2x*(-2)', 'x^6+98x^2+(5/7)x^4', '((x+x^(-1))^2+9)^3', '(x/5^x)*(2^((x^(-1))/8^x))', '2^((-45)+2x)', '(x^6)^(x^(-1))+23^x', 'x^2^3', '1+(22+x)(7/5)+2(x+x^2)-x(6x+5)', 'cos(5x)']
    
    for i in testcases:
        print "initial", i
        j = equation(i)