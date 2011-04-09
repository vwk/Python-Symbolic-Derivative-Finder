import sys
from core import *
from PyQt4 import QtGui,  QtCore

class MainWindow (QtGui.QMainWindow):
    
    def __init__(self):
        super(MainWindow,self).__init__()
        
        self.initUI()
    
    def initUI(self):

        self.setWindowTitle('Python Symbolic Derivative Finder')
        self.statusBar().showMessage('Ready')
        
        exit = QtGui.QAction('Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit')
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
        
        menubar = self.menuBar()
        file = menubar.addMenu('&File')
        file.addAction(exit)
        
        central = middleWidget()
        self.setCentralWidget(central)
        

class middleWidget (QtGui.QWidget):
    
    def __init__(self):
        super(middleWidget,self).__init__()
        
        self.initUI()
    
    def initUI(self):
        
        self.resize(400,300)
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        
        eqlabel = QtGui.QLabel('Equation:')
        self.equation = QtGui.QLineEdit()
        
        convertbutton = QtGui.QPushButton('Derive')
        
        outputlabel = QtGui.QLabel('Derivative:')
        self.output = QtGui.QTextEdit()
        
        grid.addWidget(eqlabel,1,0)
        grid.addWidget(self.equation,1,1)
        grid.addWidget(convertbutton,2,0,1,2)
        grid.addWidget(outputlabel,3,0)
        grid.addWidget(self.output,3,1,1,2)
        
        self.setLayout(grid)
        self.connect(convertbutton, QtCore.SIGNAL('clicked()'), self.calculate)
    
    def calculate(self):
        
        inputted = str(self.equation.text())
        main.statusBar().showMessage('Working!',6000)
        
        setMainVar('x')
        
        self.function = cleanInput(inputted)
        self.derivative = derive(convertToRPN(self.function))
        
        if len(self.derivative) > 1:
            
            while shiftVariableRPN(self.derivative) != self.derivative:
                self.derivative = shiftVariableRPN(self.derivative)
            self.simple = simplifyRPN(self.derivative)
            if len(self.simple) != 1:
                self.simple = convertFromRPN(self.simple)
            self.simple = ''.join(i for i in (self.simple))
            self.output.insertPlainText(self.simple)
            
        else:
            self.derivative = ''.join(i for i in self.derivative)
            self.output.insertPlainText(self.derivative)

app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())
