#!/usr/bin/env python3
#correlate correspondence along javascript functions

import re
import json
import sys

import pyesprima3
from getfrom import *


def al(ar):
  #based on the length of the first element
  # add to any elements until all elements are the same length as the first
  ml=len(str(ar[0]))
  sar=""
  for i in ar:
    si=" "*(ml-len(str(i)))+str(i)
    sar=sar+" "+str(si)
  return sar

def ttf(jo):
  import json
  print(json.dumps(jo,sort_keys=True,indent=2))

def roll(jo):
  for i in jo:
    print(i)

def rolln(jo):
  for ni,i in enumerate(jo):
    print(ni,i)




#have default behaviour run the parser overriding existing file, then allow for flags to use existing, etc.
def parser(testd):
  inp=testd[0]["meta"]["args"][2] #len of sys.argv is 0, FILE.js is 1, FILE.json is 2
  filen=inp.split(".js")[0]
  filen=filen.split("/")[len(filen.split("/"))-1]
  filen="./parsed."+str(filen)+".json"
  print("..parsing",filen)
  if len(sys.argv)==3:
    call(["./pyesprima3.py",sys.argv[1],">>",filen])
  testd[0]["parsed"]=json.loads(open(filen,"r").read()) #open file and read contents load json to dict
  return testd


def checkcommandline(testd):
  if len(sys.argv) > 1:
    #building the test obj's meta data.. storing passed arguments
    testd.append({})
    testd[0]["meta"]={}
    testd[0]["meta"]["args"]=[]
    testd[0]["meta"]["args"].append(len(sys.argv)-1)
    for arrg in sys.argv:
      testd[0]["meta"]["args"].append(arrg)
    testd=parser(testd)
    cnt=1
    while cnt<len(sys.argv):
     testd[0]["meta"]["args"].append(sys.argv[cnt])
     cnt+=1
    testd[0]["projtotest"]=sys.argv[1]
  else:
    print("  ..requires command line input\n    ./build.py ARG1 [ARG2]\n")
    print("    ARG1 :: .js file to create tests for")
    print("    ARG2 :: [optional], old test file to append new functions to unaltering existing tests")
    exit()
  if len(sys.argv) > 2 and sys.argv[2]!="-p": #yuck!
    oldtestfile = open(sys.argv[2],'r')
    oldread = oldtestfile.read()
    oldread = oldread.split('alltests =')
    if ( len(oldread) > 1 ) :
      try:
        oldtestjson = json.loads(oldread[1])
      except:
        print("  .. failing to load the tests file")
        print("     make sure your json is formatted correctly")
        print("     and begins with 'alltests = JSON_OBJ'")
        exit()
      oldfobjmp = json.dumps(oldtestjson) # ensures formatting
      newread=""
      for line in oldfobjmp.split("\n"):
        line = line.strip() # removes leading and trailing whitespace
        newread=newread+line
      teststring=newread[:-1]+", "
    else:
      oldtestjson = 17 #implies oldtestjson is vacant
      teststring="["
  else:
    oldtestjson = 17 #implies oldtestjson is vacant
    teststring="["
  testd[0]["oldtestjson"]=oldtestjson
  testd[0]["teststring"]=teststring
  return testd


def fillobjREQinit():
  #0 int
  #0.0 float
  #"" string
  #[] array
  #{} object
  fobj={}
  fobj["funcname"]="" # function name, invocation string
  fobj["tcnt"]=0 # ["parsed"][1]["body"][toplevel index number
  fobj["ptyp"]="" # ["parsed"][0][ptyp string
  fobj["pcnt"]=0 # ["parsed"][0][ptyp][index number
  fobj["funcnum"]=0 # tested[toplevel function index number
  fobj["thewhy"]="" # explanation of what the function does
  fobj["lines"]=[] #raw source of function split into array of individual lines
  fobj["flen"]=0 #number of lines in function
  fobj["lsten"]=[] #line start and end [start,end]
  fobj["header"]="" # raw source function header
  fobj["footer"]="" # raw source function footer
  fobj["vars"]={} #variables used in the function
  fobj["vars"]["pass"]=[] # variables passed to the function, function f(ae) {}
                       #[{
                       #  ANY #pass variables are stored as they appear in the source: f(ae,ea){} ]["pass]["ae","ea"]
                       #},]
  fobj["vars"]["asgn"]=[] # variables assigned  ae=ae+17
  fobj["vars"]["pmut"]=[] # variables possibly mutated, reassignment of passed variables
                       #[{
                       #  "name":""  # name of variable
                       #  "val" :ANY # variable value
                       #},]
  fobj["vars"]["decl"]=[] # variables declared, var ae=17
                       #[{
                       #  "kind":""  # type of declaration var,let,et al
                       #  "name":""  # name of variable
                       #  "val" :ANY # variable value
                       #},]
  fobj["vars"]["retd"]=[] # variables returned from the function, return ae
  fobj["call"]={} # executed code within function: calls and constructs; new'call'function expressions
  fobj["call"]["user"]=[] # user defined functions
  fobj["call"]["js"]=[]   # js built ins
  fobj["call"]["tree"]={} # sub function tree
  fobj["call"]["allpmut"]=[] # all pmut in subfunctions
  #imagine, fobj["call"]["allpmut"]["REQ"]
  #imagine, fobj["call"]["allpmut"]["OPT"]
  return fobj


def fillobjREQlinework(pfunc,lines,fobj):
  fbeg=pfunc["loc"]["start"]["line"]
  fobj["header"]=lines[fbeg-1] # store header

  fend=pfunc["loc"]["end"]["line"]
  fobj["footer"]=lines[fend-1] # store header

  thewhy=fobj["footer"].split(',',1) #function explanation :: // func(), {{thewhy}}
  if len(thewhy)>1: # explanation present in footer
    thewhy=thewhy[1].strip() #explanation follows
  else: # function missing terse description
    thewhy="TODO :: this function requires terse explanation"
  fobj["thewhy"]=thewhy #stoddre in function
  #print(fobj["thewhy"])

  while fbeg<=fend:
    #fbeg-1 because fbeg and fend count starts at line 1 and lines is an array starting at 0
    fobj["lines"].append(lines[fbeg-1])
    fbeg+=1
  fobj["flen"]=len(fobj["lines"])
  fobj["lsten"]=[pfunc["loc"]["start"]["line"],pfunc["loc"]["end"]["line"]]
  return fobj


##TODO, grants preference to toplevel functions.. comfortable with that?
def fillobj(testd):
  projtotest = open(testd[0]["projtotest"],'r')
  lines = projtotest.readlines()
  prsobj=testd[0]["parsed"]
  for ipb,pfunc in enumerate(prsobj[1]["body"]):
    if pfunc["type"]=="FunctionDeclaration":

      fobj=fillobjREQinit()

      # toplevel func index store in meta,len(testd) due yet to be appended
      frange=pfunc["range"]
      for typ in ["FunctionDeclaration"]:
        for ifd,fd in enumerate(prsobj[0][typ]):
          if fd["range"]==frange:
            fd["toplevel"]=len(testd)
            fobj["tcnt"]=ipb
            fobj["pcnt"]=ifd
            fobj["ptyp"]=typ
      fobj["funcnum"]=len(testd)

      funcname=pfunc["id"]["name"]
      fobj["funcname"]=funcname # store funcname

      #skip=fillobjREQtestfuncexist(funcname,oldtestjson,testd)
      skip=-1#TODO
      if int(skip) == -1:
        fobj=fillobjREQlinework(pfunc,lines,fobj)
      else:
        fobj["precomposed"]=oldtestjson[skip]
        #print("  :"+str(len(testd))+">  ",funcname+"()","test already exists")
      testd.append(fobj)
    else:
      rolln(pfunc)
      fbeg=pfunc["loc"]["start"]["line"]
      fend=pfunc["loc"]["end"]["line"]
      #print("    globe:",pfunc["type"],fbeg,fend)
      if "globe" not in testd[0]:
        testd[0]["globe"]={}
        testd[0]["globe"]["lines"]=[]
      while fbeg<=fend:
        testd[0]["globe"]["lines"].append(lines[fbeg-1])
        fbeg+=1

  testd[0]["meta"]["numboffunc"]=len(testd)-1 # subtract meta
  return testd


def fillobjREQtestfuncexist(funcname,oldtestjson,testd):
  skip=-1 # defaults,-1, function vacant in ole test file
  icnt=0
  if oldtestjson == 17 :
      skip=-1 #if old test is vacant then all functions need to be evaluated
  else:
    for i in oldtestjson:
      try:
        if i["funcname"] == funcname:
          skip=icnt #skip if function already has a test in the oldtest file
          break
      except:
        skip=-1
      icnt+=1
  return skip


def TOOLtoform(toform,instruction):
  import json
  if instruction == "print" or instruction == "p":
    formd=json.dumps(toform,indent=2,sort_keys=True)
    #print(formd,"\n^^^^^^^^^^^^^^^\n")
    ret=0
  if instruction == "return" or instruction == "r":
    formd=json.dumps(toform,indent=2,sort_keys=True)
    ret=formd
  return ret


def fstpObj(stp,testd):
  # function stp obj, will grab the parse object found by stepping through stp
  stpobj={}
  stpobj=testd[0]["parsed"][1]
  for ea in stp:
    stpobj=stpobj[ea]
  return stpobj

#TODO, partial stp is weak.. need exact compare
## good place to start,
## but embedded function decls mean multiple return statements share partial stp


import os
def printUnfinishedComplaint(unf,pobj,grepable,stp):
  print("\n\n     .. stp :",json.dumps(stp,sort_keys=True,indent=2))
  print(" unfinished..")
  print("   yet unworked "+unf+" :",pobj,"; in "+str(grepable))
  print("     .. add support for new "+unf+" manually to corrjs.py source")
  os._exit(0)




def collateVarREQfoVarDecl(pvars,fstpd,testd):
  faArr=[]
  foArr=[]
  for iva,va in enumerate(pvars):
    lf=len(fstpd)
    vstpd=va["stp"]
    partial=vstpd[:lf]
    if partial==fstpd:  #TODO, partial stp is weak.. need exact compare
      faArr.append(iva)
      stppd=fstpObj(va["stp"],testd)
      stpup=fstpObj(va["stp"][:-2],testd)
      kind=stpup["kind"]
      # check for type identifier
      if str(stppd["init"])=="None":
        vdVal="null"
      else:
        vdVal=getAnyFrom(stppd["init"])
      foArr.append({"kind":kind,"name":stppd["id"]["name"],"val":vdVal})
  ret={"faArr":faArr,"foArr":foArr}
  return ret


def collateVarREQfoVarAsgn(pexpr,fstpd,testd):
  faArr=[]
  foArr=[]
  for iea,ea in enumerate(pexpr):
    lf=len(fstpd)
    estpd=ea["stp"]
    partial=estpd[:lf]
    if partial==fstpd: # TODO, partial stp is weak.. need exact compare
      stppd=fstpObj(ea["stp"],testd)
      faArr.append(iea)
      if stppd["expression"]["type"]=="AssignmentExpression":
        foArr.append(getAnyFrom(stppd["expression"]))
  ret={"faArr":faArr,"foArr":foArr}
  return ret


  # ["vars"]["retd"], return value
  # http://esprima.org/demo/parse.html?code=function%20ae()%20%7B%0Areturn%2017%2Cae%2C%5B%5D%2C%7B%7D%0A%7D%0A
    # instead of just grabbing the last ellement from blockArr assuming the ReturnStatement
    ## have to step through the entire block statement in case of developer error
    ## where code follows an initial ReturnStatement adding superfluous blocks
    # function ae() {
    #   return 17
    #   ea=34
    #   return 34
    # }
    ## parsing this function in esprima will give us a BlockStatement array of 3 elements
    ## but the js vm ignores anything after the first ReturnStatement
    # TODO,
    ## only applies to top level, buried returns are often intentional
    ## will have to come up with parsing intentional multiple return statements
    # as in the case of if () { return ae } else { return ea }
    ##
def collateVarREQfoVarRetd(fobj,fpobj,fstpd):
  if fpobj["body"]["type"] == "BlockStatement":
    blockArr=fpobj["body"]["body"]
    for ba in blockArr:
      if ba["type"] == "ReturnStatement":
        retval=getAnyFrom(ba["argument"])
        if type(retval)==list:
          fobj["vars"]["retd"]=retval
        else:
          fobj["vars"]["retd"].append(retval)
        break # first return statement exits the function
  else:
    printUnfinishedComplaint("type",fpobj["type"],"collateREQvar() vars.retd BlockStatement",fstpd)
  return fobj


def collateVarREQfoVarPass(fobj,fpobj):
  # ["vars"]["pass"], passed parameters
  # http://esprima.org/demo/parse.html?code=function%20ae(a%2Ce%2C%5Ba%2Ce%5D%2C%7B%7D)%20%7B%0A%7D%0A
  if len(fpobj["params"])>0: # len()==0 is empty param list
    for pa in fpobj["params"]:
      fobj["vars"]["pass"].append(getAnyFrom(pa))
  return fobj


def collateVarREQfoVarPmut(fobj,fstpd,testd):
  pArr=[]
  fovP=fobj["vars"]["pass"]

  #see playjs/multimmut for mutatable types..
  #imagine, how to check for type from preprocessor?
  #should account for CallExpressions of mutable types:
  #  ea(ae);
  #  ae should be a pmut if in pass
  #    same as callncons, but intersted in the arguments
  for poss in ["asgn","decl"]:
    fov=fobj["vars"][poss]
    newArr=[]
    if poss=="asgn":
      lfrt="name"
    else:
      lfrt="val"
    for item in fov:
      sa=str(item[lfrt]).split(".")[0]
      sa=sa.split("[")[0]
      if len(fovP) > 0:
        for fop in fovP:
          if sa==fop:
            if item[lfrt] not in pArr: # ensures dupes are left out
              pArr.append(item[lfrt])
          else:
            newArr.append(item)
      else:
        newArr=fov
    fobj["vars"][poss]=newArr

  fobj["vars"]["pmut"]=pArr
  return fobj


def collateREQvar(testd):
  prsmeta=testd[0]["parsed"][0]
  pfunc=prsmeta["FunctionDeclaration"]  # functions: function ae(){ }
  pvars=prsmeta["VariableDeclarator"]   # variables: var ae; let ea
  pexpr=prsmeta["ExpressionStatement"]  # assignments: ae=17
  for fa in pfunc:
    fa["var"]={}
    fstpd=fa["stp"]
    fpobj=fstpObj(fstpd,testd)
    for kys in fa.keys():
      if kys=="toplevel":
        fobj=testd[fa["toplevel"]]
        fobj=collateVarREQfoVarPass(fobj,fpobj)
        fobj=collateVarREQfoVarRetd(fobj,fpobj,fstpd)

        foVD=collateVarREQfoVarDecl(pvars,fstpd,testd)
        fa["var"]["VariableDeclarator"]=foVD["faArr"]
        fobj["vars"]["decl"]=foVD["foArr"]

        foVA=collateVarREQfoVarAsgn(pexpr,fstpd,testd)
        fa["var"]["ExpressionStatement"]=foVA["faArr"]
        fobj["vars"]["asgn"]=foVA["foArr"]

        fobj=collateVarREQfoVarPmut(fobj,fstpd,testd)
  return testd


###################################################################################
#evaluate the parse tree
#dig(testd)
def dig(testd):
  at=testd[0]
  at=at["parsed"][0]
  #at=at["CallExpression"]
  #at=at["FunctionExpression"]
  at=at["FunctionDeclaration"]

  #print(TOOLtoform(list(at.keys()),"r"))
  #for i in at.keys():
  #  print(i,type(at[i]),len(at[i]))

  for ind,i in enumerate(at):
    #print("\n\n=========================")
    #print(TOOLtoform(i,"r"))
    pass

  #for ind,i in enumerate(at):
  #  for afi,af in enumerate(testd):
  #    if afi>0:
  #      if af["pcnt"]==ind:
  #        print("\n\n=========================")
  #        print(af["pcnt"],ind,i["loc"]==at[af["pcnt"]]["loc"])
  #        print(TOOLtoform(i,"r"))
  #  #print(i["loc"]["start"]["line"])
####################################################################################


def collateSubfuncREQtopl(testd):
  topfunc={}
  for atfi,atf in enumerate(testd):
    if atfi>0:
      topfunc[atf["funcname"]]={"ind":atfi}
  testd[0]["meta"]["topfunc"]=topfunc
  return testd


def collateSubfuncREQcallncons(testd):
  #esprima issue?  [[Construct]] [[Call]], getValue() in the spec
  # new calls [[Construct]] executing the contents,
  # Call calls a function's [[Call]] to execture the contents
  pexd=testd[0]["parsed"][0]
  for tlfi,tlf in enumerate(testd):
    if tlfi>0:
      tlfs=tlf["lsten"][0]
      tlfe=tlf["lsten"][1]
      found=[]
      prel=[] #preliminary array collects both js and user funcs
      for c0n1f2 in ["CallExpression","NewExpression","FunctionExpression"]:
        for aexi,aex in enumerate(pexd[c0n1f2]):
          if tlfs<aex["loc"]["start"]["line"] and aex["loc"]["end"]["line"]<tlfe:
            paex=fstpObj(aex["stp"],testd)
            if c0n1f2=="FunctionExpression":
              if not paex["loc"] in found:
                prel.append(getAnyFrom(paex).split(".")[-1:][0])
                found.append(paex["loc"])
            else:
              if not paex["callee"]["loc"] in found:
                prel.append(getAnyFrom(paex["callee"]).split(".")[-1:][0])
                found.append(paex["callee"]["loc"])

      for ap in prel:
        #or ap=="function()" statement is idiomatic to returns from own getfrom.py..
        ### subject to change, keep an eye on this line
        if ap == "function()" or ap in testd[0]["meta"]["topfunc"]:
          tlf["call"]["user"].append(ap)
        else:
          tlf["call"]["js"].append(ap)
  return testd


def collateSubfuncREQftop(testd):
  topfunc=testd[0]["meta"]["topfunc"]
  for atfi,atf in enumerate(testd):
    if atfi>0:
      ftop=[]
      for st in atf["call"]["user"]:
        if st in testd[0]["meta"]["topfunc"]:
          ftop.append(st)
      topfunc[atf["funcname"]]["ftop"]=ftop
  return testd



def nextr(item,topf,testd,fulllist,apm):
  ok={}
  if item in topf:
    loop=topf[item]
    for item in loop["ftop"]:
      if item not in fulllist:
        fulllist.append(item)
        #ok[item]=nextr(item,topf,testd,fulllist)
        pm=testd[topf[item]["ind"]]["vars"]["pmut"]
        for ap in pm:
          if ap not in apm:
            apm.append(ap)
        nobj=nextr(item,topf,testd,fulllist,apm)
        ok[item]={"f":nobj["ftree"],"pmut":pm}
  robj={"ftree":ok,"apm":apm}
  return robj


def collateSubfuncREQtree(testd):
  topf=testd[0]["meta"]["topfunc"]
  for tlfi,tlf in enumerate(testd):
    if tlfi>0:
      fulllist=[]
      branch={}
      step=branch
      if tlf["funcname"] in topf:
        allpmut=[]
        for sf in topf[tlf["funcname"]]["ftop"]:
          #step[sf]=nextr(sf,topf,testd,fulllist)
          pm=tlf["vars"]["pmut"]
          for ap in pm:
            if ap not in allpmut:
              allpmut.append(ap)
          nobj=nextr(sf,topf,testd,fulllist,allpmut)
          allpmut=nobj["apm"]
          step[sf]={"f":nobj["ftree"],"pmut":pm}
      tlf["call"]["tree"]=branch
      tlf["call"]["allpmut"]=allpmut
      #print(tlf["funcname"])
      #print(json.dumps(tlf["call"]["allpmut"],sort_keys=True,indent=2))
      #print(TOOLtoform(branch,"r"))
  return testd


def collateREQsubfunc(testd):
  testd=collateSubfuncREQtopl(testd)
  testd=collateSubfuncREQcallncons(testd)
  testd=collateSubfuncREQftop(testd)
  testd=collateSubfuncREQtree(testd) #only follows toplevel functions down
  return testd


def collate(testd):

  testd=collateREQvar(testd)
  testd=collateREQsubfunc(testd)

  ### temp outs
  #for ai,a in enumerate(testd):
  #  if ai>0:
  #    print("========",a["funcname"])
  #    print(TOOLtoform(a["call"],"r"))
  ###
  #print(TOOLtoform(testd[0]["meta"]["topfunc"],"r"))
  return testd


#TODO, imagine,  discover the string of asignments that lead to ret or from ins
#     n=e; g=n; ae=g .. ae->e

def funcblocks(testd):
  fun=1 #0 is meta data
  lt=len(testd)
  while fun < lt:
    tb=2 # numb of spaces for tab

    sc=4 # numb of repeats for underscore
    fobj=testd[fun]
    print("func:",fun,":",fobj["funcname"]," "*tb*3,"pcnt:",fobj["pcnt"],"tcnt:",fobj["tcnt"])

    print(" "*tb+"|","thewhy",":",fobj["thewhy"])


    print(" "*tb+"|","header",":",fobj["header"][:-1])
    print(" "*tb+"|","footer",":",fobj["footer"][:-1])
    print(" "*tb+"|","vars",":")

    ### vars
    for subv in fobj["vars"]:
      print(" "*tb+"|"+" "*tb*3+"|"+"_"*sc,subv+":")
      for ea in fobj["vars"][subv]:
        if subv in ["asgn"]:
          print(" "*tb+"|"+" "*tb*8+"|_",ea["name"])
          if type(ea["val"])=="str":
              print(" "*tb+"|"+" "*tb*8+"|"," "*int(len(ea["name"])),ea["val"])
          else:
            for spl in json.dumps(ea["val"],sort_keys=True,indent=2).splitlines():
              print(" "*tb+"|"+" "*tb*8+"|"," "*int(len(ea["name"])),spl)
        elif subv=="pmut":
          print(" "*tb+"|"+" "*tb*8+"|_")
          print(" "*tb+"|"+" "*tb*8+"|"," "+ea)
        elif subv=="decl":
          print(" "*tb+"|"+" "*tb*8+"|"+"_"*sc,ea["kind"])
          print(" "*tb+"|"+" "*tb*8+"|",ea["name"])
          if type(ea["val"])=="str":
              print(" "*tb+"|"+" "*tb*8+"|"," "*int(len(ea["name"])),ea["val"])
          else: #pass,retd
            for spl in json.dumps(ea["val"],sort_keys=True,indent=2).splitlines():
              print(" "*tb+"|"+" "*tb*8+"|"," "*int(len(ea["name"])),spl)
        else:
          print(" "*tb+"|"+" "*tb*8+"|"+"_",ea)
    print(" "*tb+"|"+"_"*sc)
    ### vars

    ### lines
    print(" "*tb+"|"+"_"*sc,": "+str(fobj["flen"])+" lines :")
    for tln in fobj["lines"]:
      print(" "*tb+"|"+" "*tb,tln[:-1])
    print(" "*tb+"|"+"_"*sc)
    fun+=1
    ### lines

def writeToJS(testd):
      fo="tmp.js" #file out name
      print("  write to:",fo)
      testout=open(fo,"w")
      testd[0]["parsed"]=[] # clears the parse tree to shrink json size
      testout.write("corrd="+json.dumps(testd,sort_keys=True,indent=2))
      testout.close()

def writeToJSON(testd):
      fo="tmp.json" #file out name
      print("  write to:",fo)
      testout=open(fo,"w")
      testd[0]["parsed"]=[] # clears the parse tree to shrink json size
      testout.write(json.dumps(testd,sort_keys=True,indent=2))
      testout.close()

def corr(testd):
  testd=checkcommandline(testd) # check command arguments
  testd=fillobj(testd) # fill the test obj
  testd=collate(testd) # process the test obj
  return testd


def corrRun():
    arg=sys.argv[1]
    if arg == "-./":
      sys.argv.remove("-./")
      testd=[]
      testd=corr(testd)
      writeToJSON(testd)
      writeToJS(testd)
      #funcblocks(testd) # formatted stdout printing of functions

corrRun()

print("..01x17")
#./corrjs.py -./ ~/cinger/proj/playpy/depend/pyesprima/tester.js
