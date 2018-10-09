import os
import re
import time
from PyQt4 import QtCore, QtGui

#for GUI
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
        
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Translator(object):

    def div(self,line):#DONE but with bug , trebuie sa verific daca nu am ghilimele gen "[3/2]"
        firstCol=-1
        lit = False
        i=0
        while i < len(line):
            if line[i]=="[":
                if i!=0: #ca sa nu dea boundary exception
                    if line[i-1].isalpha()==True or line[i-1]=="]": #verificam daca e litera
                        lit = True
                    else: 
                        lit = False
                        firstCol=i
            elif line[i]=="]" and firstCol!=-1:
                if lit==False:
                    lastCol=i+1 #to go until the bracket
                    stringToReplace = line[firstCol:lastCol]
                    if stringToReplace.find("/")!=-1:
                        line = line.replace(stringToReplace,"(int)("+stringToReplace[1:(len(stringToReplace)-1)]+")")
                        line = self.div(line)
                        break
                else: 
                    lit = False
            i+=1
        return line

    def getInput(self,path):
        file = open(path,"r")
        string = str(file.read())
        lines = string.splitlines()
        length = len(lines)
        linesToRemove = []

        for i in range(length):
            lines[i] = lines[i].replace("\t","")
            lines[i] = lines[i].lstrip()  
            if lines[i][:2].find("//")!=-1:
                length-=1
                linesToRemove.append(i)
            else :
                if lines[i].find("[")!=-1: lines[i]=self.div(lines[i])# pentru impartirea intreaga 
                lines[i]=lines[i].replace("<>","!=")
                lines[i]=lines[i].replace(" si "," && ")
                lines[i]=lines[i].replace(" sau "," || ")
                lines[i]=lines[i].replace("=","==")
                lines[i]=lines[i].replace("!==","!=")
                lines[i]=lines[i].replace("<==","<=")
                lines[i]=lines[i].replace(">==",">=")
                lines[i]=lines[i].replace("<-","=")
        for i in linesToRemove:
            lines.remove(lines[i])
        file.close()
        return lines

    def getVars(self,line,modRemove=False):
        linie = line 
        linie=linie.replace("<-"," ")
        linie=re.sub(r"int|-|!|=|&|,|>|<"," ",linie)
        linie=linie.replace("("," ")
        if modRemove == False:
            linie=linie.replace("%"," % ")
        else :
            linie=linie.replace("%"," ")
        linie=linie.replace(")"," ")
        linie=linie.replace("|"," ")
        linie=linie.replace("*"," ")
        linie=linie.replace("+"," ")
        linie=linie.replace("\n"," ")
        variables = linie.split()
        wordsToRemove = []
        x=0
        for var in variables:
            for c in var:
                if c in ['1','2','3','4','5','6','7','8','9','0']:
                    x+=1
            if(x==len(var)):
                wordsToRemove.append(var)
            x=0
        for var in wordsToRemove:
            variables.remove(var)
        return variables

    def pentru(self,line):# voi reveni pentru asignarea multiplelor valori precum pentru i,f <- 1,2,n,23,-2
    #  pentru i <- 1,n,-2 executa
    # in caz de tablou o sa pun int la for
        pas = "1"
        ok = True
        linie = line.replace(" ","")
        if linie.count(",")>1:
            index = linie.find("executa")
            aux = linie[:index]
            for i in range((index-1),0,-1):
                if aux[i]==',':
                    pas=aux[i+1:index]
                    ok = False
                    break
        vars = self.getVars(linie,modRemove=True)
        index = linie.find(",")
        pt="for("+ linie[:index]+";"
        linie=linie[index+1:]
        if ok!=True:
            index = linie.find(",")
            var = linie[:index]
            if pas[0]=="-":pt+=vars[0]+">="+var+";"+vars[0]+"+="+pas+"){\n"
            else :pt+=vars[0]+"<="+var+";"+vars[0]+"+="+pas+"){\n"
        else :
            index = linie.find("executa")
            var = linie[:index]
            pt+=vars[0]+"<="+var+";"+vars[0]+"+="+pas+"){\n"
        return pt

    def repetaPanacand(self,line):
        if line.find("repeta")!=-1:
            return "do{\n"
        elif line.find("panacand")!=-1:
            panacand = "}while("
            aux=line[8:]
            if aux.find("==")!=-1:
                aux=aux.replace("==","!=")
            elif aux.find("!=")!=-1:
                aux=aux.replace("!=","==")
            if aux.find(">=")!=-1:
                aux=aux.replace(">=","<")
            elif aux.find("<=")!=-1:
                aux=aux.replace("<=",">")
            elif aux.find(">")!=-1:
                aux=aux.replace(">","<=")
            elif aux.find("<")!=-1:
                aux=aux.replace("<",">=")
            if aux.find("||")!=-1:
                aux=aux.replace("||","&&")
            elif aux.find("&&")!=-1:
                aux=aux.replace("&&","||")
            panacand+=(aux+");\n")
            return panacand

    def declareAll(self,lines):#Done #mai trebuie doar char si tablou
        floatVars="\tfloat "
        intVars="\tint "
        allVars=[]
        for line in lines:
            prLine=line+" "
            vf = prLine.find("scrie")
            if vf != -1:
                if prLine[vf-1]!=" " or prLine[vf+5]!=" ":  
                    allVars+=self.getVars(line)
            else: 
                allVars+=self.getVars(line)
        inters = []

        for i in range(len(allVars)):
            if allVars[i]=="%":
                inters.append(allVars[i-1])    
                inters.append(allVars[i])    
                inters.append(allVars[i+1])    
        inters=set(inters)

        allVars=set(allVars)
        for c in inters:
            allVars.remove(c)
        if("%" in inters):
            inters.remove("%")

        for c in inters:
            intVars+=c+","
        intVars=intVars[:-1]+";\n"

        for var in allVars:
            if var not in ["citeste","executa","scrie","pentru", "cattimp","panacand","repeta","atunci","altfel","daca","sfd","sfc","sfp","%"]:
                floatVars+=(var+",")
        floatVars=floatVars[:-1]+";\n"
        if floatVars=="\tfloat;\n":
            floatVars=""
        if intVars=="\tint;\n":
            intVars=""
        return floatVars+intVars

    def tabs(self,num):
        tab = ""
        i=0
        while i< num:
            tab+="\t"
            i+=1
        return tab

    def translate(self,inPath, outPath):
        out = open(outPath,'w')
        lines = self.getInput(inPath)    
        tab = 1
        trans="#include<iostream>\n\nusing namespace std;\n\nint main(){\n\n"+self.declareAll(lines)
        linieLibera = False
        repetaBracket = 0
        dacaBracket = 0
        cattimpBracket = 0
        pentruBracket = 0
        vfBracketWord = []
        for line in lines:
            words = line.split()
            asignTab=True
            for word in words:
                if word == "citeste":#Done
                    cit = line[8:]
                    cit=cit.replace(',',">>")
                    trans+=(self.tabs(tab)+"cin>>"+cit+";\n")
                    break
                elif word == "scrie":#Done
                    scrie = line[6:]
                    scrie=scrie.replace(",","<<")
                    trans+=(self.tabs(tab)+"cout<<"+scrie+";\n")
                    break
                elif word == "pentru":#Done
                    pt = line[6:]
                    pentruBracket+=1
                    trans+=(self.tabs(tab)+self.pentru(pt))
                    tab+=1
                    vfBracketWord.append(word)
                    break
                elif word == "cattimp":#Done
                    ct =self.tabs(tab)+"while("+line[8:-8]+"){\n"
                    trans+=ct
                    cattimpBracket+=1
                    tab+=1
                    vfBracketWord.append(word)
                    break
                elif word == "repeta":#Done
                    do =self.tabs(tab)+self.repetaPanacand(line)
                    repetaBracket += 1
                    trans+=do
                    tab+=1
                    vfBracketWord.append(word)
                    break
                elif word == "panacand" and repetaBracket != 0 and vfBracketWord[len(vfBracketWord)-1]=="repeta":#Done
                    tab-=1
                    do = self.tabs(tab)+self.repetaPanacand(line)
                    repetaBracket-=1
                    trans+=do
                    del vfBracketWord[len(vfBracketWord)-1]
                    break
                elif word == "daca":#Done
                    daca =self.tabs(tab)+ "if("+line[5:-7]+"){\n"
                    dacaBracket+=1
                    tab+=1
                    trans+=daca
                    vfBracketWord.append(word)
                    break
                elif word == "altfel":#Done
                    tab-=1
                    aux = line[7:]
                    altfel = ""
                    altfel = self.tabs(tab)+"}\n"+self.tabs(tab)+"else"
                    if aux.find("daca ") != -1:
                        tab+=1
                        daca = "{\n"+self.tabs(tab)+"if("+aux[5:-7]+"){\n"
                        tab+=1
                        dacaBracket+=1
                        vfBracketWord.append("daca")
                        altfel+=daca
                    else: 
                        altfel+="{\n"
                        tab+=1
                        for i in range(len(aux)):
                            if aux[i]!=" " and aux[i]!="\n":
                                altfel+=aux[i]
                    trans+=altfel
                    break
                elif word =="sfd" and dacaBracket >0 and vfBracketWord[len(vfBracketWord)-1]=="daca":#Done
                    tab-=1
                    trans+=(self.tabs(tab)+"}\n")
                    dacaBracket-=1
                    del vfBracketWord[len(vfBracketWord)-1]
                    break
                elif word =="sfp" and pentruBracket>0 and vfBracketWord[len(vfBracketWord)-1]=="pentru":#Done
                    tab-=1
                    trans+=(self.tabs(tab)+"}\n")
                    pentruBracket-=1
                    del vfBracketWord[len(vfBracketWord)-1]
                    break
                elif word =="sfc" and cattimpBracket>0 and vfBracketWord[len(vfBracketWord)-1]=="cattimp":#Done
                    tab-=1
                    trans+=(self.tabs(tab)+"}\n")
                    cattimpBracket-=1
                    del vfBracketWord[len(vfBracketWord)-1]
                    break
                else: #Done
                    if word not in ["sfd","sfc","sfp","panacand"]:
                        if asignTab==True:
                            trans+=(self.tabs(tab)+word)
                            asignTab=False
                        else :
                            trans+=(word)
                    linieLibera = True
            if linieLibera == True:
                trans+=";\n"
                linieLibera=False
        trans+="\n\treturn 0;\n}"
        out.write(trans)
        out.close()

    def compilePat(self,path):
        os.system("g++ -Wall "+path+" -o main")

class GUI(object):
    def setupUi(self, GUI):
        GUI.setObjectName(_fromUtf8("Translator"))
        GUI.setFixedSize(812, 548)
        self.translatorObj = Translator()
        self.buttonBox = QtGui.QDialogButtonBox(GUI)
        self.buttonBox.setGeometry(QtCore.QRect(10, 600, 461, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.pseudo_2 = QtGui.QLabel(GUI)
        self.pseudo_2.setGeometry(QtCore.QRect(130, 10, 121, 21))
        self.pseudo_2.setAlignment(QtCore.Qt.AlignCenter)
        self.pseudo_2.setObjectName(_fromUtf8("pseudo_2"))
        self.main_2 = QtGui.QLabel(GUI)
        self.main_2.setGeometry(QtCore.QRect(540, 10, 141, 21))
        self.main_2.setAlignment(QtCore.Qt.AlignCenter)
        self.main_2.setObjectName(_fromUtf8("main_2"))
        self.translate = QtGui.QPushButton(GUI)
        self.translate.setGeometry(QtCore.QRect(270, 490, 271, 51))
        self.translate.setObjectName(_fromUtf8("translate"))
        self.toTranslate = QtGui.QTextEdit(GUI)
        self.toTranslate.setGeometry(QtCore.QRect(10, 40, 391, 441))
        self.toTranslate.setObjectName(_fromUtf8("toTranslate"))
        self.translated = QtGui.QTextEdit(GUI)
        self.translated.setGeometry(QtCore.QRect(410, 40, 391, 441))
        self.translated.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.translated.setObjectName(_fromUtf8("translated"))

        self.retranslateUi(GUI)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), GUI.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), GUI.reject)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), GUI.reject)
        QtCore.QObject.connect(self.translate, QtCore.SIGNAL(_fromUtf8("clicked()")), self.buttonAction)
        QtCore.QObject.connect(self.translate, QtCore.SIGNAL(_fromUtf8("clicked()")), self.setLabelText)
        QtCore.QMetaObject.connectSlotsByName(GUI)

    def retranslateUi(self, GUI):
        GUI.setWindowTitle(_translate("Translator", "Translator 2.0", None))
        self.pseudo_2.setText(_translate("Translator", "Pseudocode", None))
        self.main_2.setText(_translate("Translator", "C++", None))
        self.translate.setText(_translate("Translator", "Translate", None))

    def buttonAction(self):
        file = open("pseudo.txt","w")
        string=str(self.toTranslate.toPlainText())
        file.write(string)
        file.close()
        self.translatorObj.translate("pseudo.txt","main.cpp")
        self.translatorObj.compilePat("main.cpp")
    
    def setLabelText(self):
        file = open("main.cpp","r")
        string = str(file.read())
        string=string.replace("\t","  ")#taburile sunt prea mari aici
        file.close()
        self.translated.setText(string)
        os.system("x-terminal-emulator -e 'bash -c ./main \nread -p \"\nPress enter to continue...\"; '")
        
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    trans = QtGui.QDialog()
    ui = GUI()
    ui.setupUi(trans)
    trans.show()
    sys.exit(app.exec_())