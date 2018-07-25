#!/usr/bin/env python3
#get an unpacked perspective on parsed objects


def TOOLtoform(toform,instruction):
  import json
  if instruction == "print" or instruction == "p":
    formd=json.dumps(toform,sort_keys=True,indent=2)
    ret=0
  if instruction == "return" or instruction == "r":
    formd=json.dumps(toform,sort_keys=True,indent=2)
    ret=formd
  return ret


#TODO partial stp is weak.. need exact compare
## good place to start,
## but embedded function decls mean multiple return statements share partial stp


def getArrayFromArrayExpression(prsd):
  # http://esprima.org/demo/parse.html?code=%5B'a'%2C'e'%5D%0A
  gafap=[]
  if prsd["type"] == "ArrayExpression":
    for elle in prsd["elements"]:
      if elle["type"] == "ArrayExpression":
        gafap.append(getArrayFromArrayExpression(elle["value"]))
      else:
        gafap.append(getStringFrom(elle["value"]))
  else:
    gafap=prsd
  return gafap


def getArrayFromSequenceExpression(prsd):
  # http://esprima.org/demo/parse.html?code=function%20ae()%7B%0Areturn%20a%2Ce%0A%7D
  gafse=[]
  if prsd["type"] == "SequenceExpression":
    for elle in prsd["expressions"]:
      gafse.append(getStringFrom(elle))
  return gafse



def getStringFromLiteral(prsd):
  if prsd["type"]== "Literal":
    gsfl=""
    gsfl=gsfl+str(prsd["value"])
  return gsfl


def getStringFromIdentifier(prsd):
  if prsd["type"]== "Identifier":
    gsfi=""
    gsfi=gsfi+prsd["name"]
  return gsfi


def getStringFromFunctionExpression(prsd):
  gsffe=getAnyFromFunctionExpression(prsd)
  return gsffe

def getStringFromArrayExpression(prsd):
  if prsd["type"]== "ArrayExpression":
    gsfae="["
    if len(prsd["elements"])>0:
      for eli,el in enumerate(prsd["elements"]):
        if eli>0:
          gsfae=gsfae+","
        gsfae=gsfae+getStringFrom(el)
    gsfae=gsfae+"]"
  return gsfae


#lazily returns string without quotes unable to evaluate
def getStringFromObjectExpression(prsd):
  gsfoe="{"
  if prsd["type"] == "ObjectExpression":
    props=prsd["properties"]
    if len(props)>0:
      for pri,pr in enumerate(props):
        if pri>0:
          gsfoe=gsfoe+","
        key=getStringFrom(pr["key"])
        val=getStringFrom(pr["value"])
        gsfoe=gsfoe+key+':'+val
    gsfoe=gsfoe+"}"
  return gsfoe


def getStringFromMemberExpression(prsd):
  gsfme=""
  if prsd["type"] == "MemberExpression":
    gsfme=gsfme+getStringFrom(prsd["object"])
    gsfme=gsfme+"."+getStringFrom(prsd["property"])
  return gsfme


def getStringFrom(prsd):
  try:
    ptype=prsd["type"]
    func="getStringFrom"+str(ptype)
    gs=globals()[func](prsd)
  except:
    func="??"
    printStrTypeComplaint(prsd,func)
  return gs


#getAnyFrom()

#prsd["value"] esprima treats ints as ints, pyesprima changes raw ints to value floats..
#  presumably because javascript only recognises floats?
#  complicates getAnyFromMemberExpression(), have to deal in raws
#ae=17
def getAnyFromLiteral(prsd):
  if prsd["type"]== "Literal":
    gafl=prsd["value"]
  return gafl


#ae=ea
def getAnyFromIdentifier(prsd):
  if prsd["type"]== "Identifier":
    gafi=prsd["name"]
  return gafi


#return ae,17
def getAnyFromSequenceExpression(prsd):
  # http://esprima.org/demo/parse.html?code=function%20ae()%7B%0Areturn%20a%2Ce%0A%7D
  gafse=[]
  if prsd["type"] == "SequenceExpression":
    for elle in prsd["expressions"]:
      gafse.append(getAnyFrom(elle))
  return gafse


#ae=[]
def getAnyFromArrayExpression(prsd):
  # http://esprima.org/demo/parse.html?code=%5B'a'%2C'e'%5D%0A
  gafap=[]
  if prsd["type"] == "ArrayExpression":
    for elle in prsd["elements"]:
      gafap.append(getAnyFrom(elle))
  return gafap


#?? function ae([]) {}
def getAnyFromArrayPattern(prsd):
  # http://esprima.org/demo/parse.html?code=%5B'a'%2C'e'%5D%0A
  gafap=[]
  if prsd["type"] == "ArrayPattern":
    for elle in prsd["elements"]:
      gafap.append(getAnyFrom(elle))
  return gafap


#ae={}
def getAnyFromObjectExpression(prsd):
  # http://esprima.org/demo/parse.html?code=a%3D%7B%22a%22%3A17%2C%22e%22%3A%5B%5D%7D%0A
  gafoe={}
  loop=gafoe
  if prsd["type"] == "ObjectExpression":
    for prop in prsd["properties"]:
      oKey=getAnyFrom(prop["key"])
      oVal=getAnyFrom(prop["value"])
  return gafoe


#?? function ae({}) {}
def getAnyFromObjectPattern(prsd):
  # http://esprima.org/demo/parse.html?code=function%20shit(%5Ba%2Cb%2Cv%5D%2C%7Bae%3A%7B%7D%7D)%7B%0A%7D%0A
  gafop={}
  if prsd["type"] == "ObjectPattern":
    for prop in prsd["properties"]:
      oKey=getAnyFrom(prop["key"])
      oVal=getAnyFrom(prop["value"])
  return gafop


#ae["ea"]
def getAnyFromMemberExpression(prsd):
  gafme=""
  if prsd["type"] == "MemberExpression":
    gafme=str(getAnyFrom(prsd["object"]))
    if prsd["property"]["type"]=="Literal":
      if len(prsd["property"]["raw"].split('"'))==1:
        intprop=int(getAnyFrom(prsd["property"]))
        gafme=gafme+"."+str(intprop)
      else:
        spr=str(getAnyFrom(prsd["property"]))
        try:
          ipr=int(spr)
          if ipr==int(spr):
            gafme=gafme+'."'+spr+'"'
        except:
          gafme=gafme+'.'+spr
    else:
      gafme=gafme+"."+str(getAnyFrom(prsd["property"]))
  return gafme

#ae(17)
def getAnyFromCallExpression(prsd):
  gafce={}
  gafce["args"]=[]
  if prsd["type"] == "CallExpression":
    gafce["call"]=getAnyFrom(prsd["callee"])
    for args in prsd["arguments"]:
      gafce["args"].append(getAnyFrom(args))
  return gafce


#ae++
def getAnyFromUpdateExpression(prsd):
  gafue={}
  if prsd["type"]=="UpdateExpression":
    gafue["name"]=getAnyFrom(prsd["argument"])
    gafue["update"]=prsd["operator"]
  return gafue


#ae=17
def getAnyFromAssignmentExpression(prsd):
  gafae={}
  if prsd["type"]=="AssignmentExpression":
    gafae["asgnop"]=prsd["operator"]
    gafae["name"]=getAnyFrom(prsd["left"])
    gafae["val"]=getAnyFrom(prsd["right"])
  return gafae


#a=e+1
def getAnyFromBinaryExpression(prsd):
  gafbe={}
  if prsd["type"]=="BinaryExpression":
    gafbe["binop"]=prsd["operator"]
    gafbe["binleft"]=getAnyFrom(prsd["left"])
    gafbe["binright"]=getAnyFrom(prsd["right"])
  return gafbe


#ae && ea
def getAnyFromLogicalExpression(prsd):
  gafle={}
  if prsd["type"]=="LogicalExpression":
    gafle["logop"]=prsd["operator"]
    gafle["logleft"]=getAnyFrom(prsd["left"])
    gafle["logright"]=getAnyFrom(prsd["right"])
  return gafle

#!ae
def getAnyFromUnaryExpression(prsd):
  gafue={}
  if prsd["type"]=="UnaryExpression":
    gafue["unaop"]=prsd["operator"]
    gafue["unaarg"]=getAnyFrom(prsd["argument"])
  return gafue

#new ae
def getAnyFromNewExpression(prsd):
  gafue={}
  argArr=[]
  if prsd["type"]=="NewExpression":
    gafue["newcall"]=getAnyFrom(prsd["callee"])
    for args in prsd["arguments"]:
      argArr.append(getAnyFrom(args))
  gafue["newargs"]=argArr
  return gafue


#function ae() {}
def getAnyFromFunctionExpression(prsd):
  if prsd["type"]== "FunctionExpression":
    if str(prsd["id"])=="None":
      gaffe="function("
    else:
      gaffe="function "+prsd["id"]["name"]+"("
    fep=""
    for pai,para in enumerate(prsd["params"]):
      if pai>0:
        fep=fep+","+getStringFrom(para)
      else:
        fep=getStringFrom(para)
    gaffe=gaffe+fep+")"
  return gaffe

def getAnyFromConditionalExpression(prsd):
  if prsd["type"] == "ConditionalExpression":
    gafce=""
    #print(TOOLtoform(prsd,"r"))
    #for i in prsd:
    #  print(i)
  print("..pending ConditionalExpression")
  print("http://esprima.org/demo/parse.html?code=ret%3Dni%3D%3D-0%20%3F%20ni%3D0%20%3A%20ni%0A")
  #exit()
  return gafce

#yet to be utilised parse types
#"BlockStatement"
#"BreakStatement"
#"CatchClause"
#"ContinueStatement"
#"DebuggerStatement"
#"DoWhileStatement"
#"EmptyStatement"
#"ExpressionStatement"
#"ForInStatement"
#"ForStatement"
#"FunctionDeclaration"
#"FunctionExpression"
#"IfStatement"
#"LabeledStatement"
#"Program"
#"Property"
#"ReturnStatement"
#"SwitchCase"
#"SwitchStatement"
#"ThisExpression"
#"ThrowStatement"
#"TryStatement"
#"VariableDeclaration"
#"VariableDeclarator"
#"WhileStatement"
#"WithStatement"



#will handle strings, object, arrays, whatever
def getAnyFrom(prsd):
  ptype=prsd["type"]
  func="getAnyFrom"+str(ptype)
  if func in globals():
    gaf=globals()[func](prsd)
  else:
    func=prsd["type"]
    from corrjs import printUnfinishedComplaint
    printUnfinishedComplaint("type",func,"getAnyFrom",prsd)
  return gaf



import os

def printStrTypeComplaint(pobj,grepable):
  print("   yet unworked str type :",pobj["type"],"; in "+str(grepable))
  print("     .. add support for new type manually to source")
  os._exit(0)


# from getfrom import *
