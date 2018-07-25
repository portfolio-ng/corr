# Meta processing for programming languages

Meta processing of source files utilising language specific ASTs.
Powerful analytics tracking variable changes and subordinate function calls.

Toplevel functions are functions that are declared independantly in global space as it stands corr only really cares about toplevel functions.

### Implemented ASTs
#### js
* Coverage: 
  * ArrayExpression
  * SequenceExpression
  * Literal
  * Identifier
  * ArrayExpression
  * ObjectExpression
  * MemberExpression
  * Literal
  * Identifier
  * SequenceExpression
  * ArrayExpression
  * ArrayPattern
  * ObjectExpression
  * ObjectPattern 
  * MemberExpression
  * CallExpression
  * UpdateExpression
  * AssignmentExpression
  * BinaryExpression
  * LogicalExpression
  * UnaryExpression
  * NewExpression
  * FunctionExpression
  * ConditionalExpression
* Yet To Be Added:
  * BlockStatement
  * BreakStatement
  * CatchClause
  * ContinueStatement
  * DebuggerStatement
  * DoWhileStatement
  * EmptyStatement
  * ExpressionStatement
  * ForInStatement
  * ForStatement
  * FunctionDeclaration
  * FunctionExpression
  * IfStatement
  * LabeledStatement
  * Program
  * Property
  * ReturnStatement
  * SwitchCase
  * SwitchStatement
  * ThisExpression
  * ThrowStatement
  * TryStatement
  * VariableDeclaration
  * VariableDeclarator
  * WhileStatement
  * WithStatement

### Example Output
#### js function 
```javascript
function fzbz(fizz,buzz,stop) {
  for (var i=1; i <= stop; i++)
  {
    let bf=fizz*buzz
    if (i % bf == 0)
      console.log("FizzBuzz");
    else if (i % buzz == 0)
      console.log("Buzz");
    else if (i % fizz == 0)
      console.log("Fizz");
    else
      console.log(i);
    }
  return "..01x17"
}
```
#### Meta expression of function in JSON
```javascript
[
  {
    "meta": {},
  {
    "call": {
      "allpmut": [],
      "js": [
        "log",
        "log",
        "log",
        "log"
      ],
      "tree": {},
      "user": []
    },
    "flen": 15,
    "footer": "}\n",
    "funcname": "fzbz",
    "funcnum": 1,
    "header": "function fzbz(fizz,buzz,stop) {\n",
    "lines": [
      "function fzbz(fizz,buzz,stop) {\n",
      "  for (var i=1; i <= stop; i++)\n",
      "  {\n",
      "    let bf=fizz*buzz\n",
      "    if (i % bf == 0)\n",
      "      console.log(\"FizzBuzz\");\n",
      "    else if (i % buzz == 0)\n",
      "      console.log(\"Buzz\");\n",
      "    else if (i % fizz == 0)\n",
      "      console.log(\"Fizz\");\n",
      "    else\n",
      "      console.log(i);\n",
      "    }\n",
      "  return \"..01x17\"\n",
      "}\n"
    ],
    "lsten": [
      1,
      15
    ],
    "pcnt": 0,
    "ptyp": "FunctionDeclaration",
    "tcnt": 0,
    "thewhy": "TODO :: this function requires terse explanation",
    "vars": {
      "asgn": [],
      "decl": [
        {
          "kind": "let",
          "name": "bf",
          "val": {
            "binleft": "fizz",
            "binop": "*",
            "binright": "buzz"
          }
        },
        {
          "kind": "let",
          "name": "bf",
          "val": {
            "binleft": "fizz",
            "binop": "*",
            "binright": "buzz"
          }
        },
        {
          "kind": "let",
          "name": "bf",
          "val": {
            "binleft": "fizz",
            "binop": "*",
            "binright": "buzz"
          }
        },
        {
          "kind": "var",
          "name": "i",
          "val": 1.0
        },
        {
          "kind": "var",
          "name": "i",
          "val": 1.0
        },
        {
          "kind": "var",
          "name": "i",
          "val": 1.0
        }
      ],
      "pass": [
        "fizz",
        "buzz",
        "stop"
      ],
      "pmut": [],
      "retd": [
        "..01x17"
      ]
    }
  }
]

```

#### Meta Schema
* fobj["funcname"]="" : function name, invocation string
* fobj["tcnt"]=0      : \["parsed"\]\[1\]\["body"\]\[toplevel index number
* fobj["ptyp"]=""     : \["parsed"\]\[0\]\[ptyp string
* fobj["pcnt"]=0      : \["parsed"\]\[0\]\[ptyp\]\[index number
* fobj["funcnum"]=0   : tested[toplevel function index number
* fobj["thewhy"]=""   : explanation of what the function does
* fobj["lines"]=[]    : raw source of function split into array of individual lines
* fobj["flen"]=0      : number of lines in function
* fobj["lsten"]=[]    : line start and end [start,end]
* fobj["header"]=""   : raw source function header
* fobj["footer"]=""   : raw source function footer
* fobj["vars"]={}     : variables used in the function
* fobj["vars"]["pass"]=[{}, ..\]    : variables passed to the function, function f(ae) {}
  * \[\{
  * ANY : pass variables are stored as they appear in the source: f(ae,ea){} ]["pass]["ae","ea"]
  * \}, .. \]
* fobj["vars"]["asgn"]=[]           : variables assigned  ae=ae+17
* fobj["vars"]["pmut"]=[{}, ..]     : variables possibly mutated, reassignment of passed variables
  * [{
  * "name":""  : name of variable
  * "val" :ANY : variable value
  * }, .. ]
* fobj["vars"]["decl"]=[{}, ..\]     : variables declared, var ae=17
  * \[\{
  * "kind":""  : type of declaration var,let,et al
  * "name":""  : name of variable
  * "val" :ANY : variable value
  * \}, .. \]
* fobj["vars"]["retd"]=[]    : variables returned from the function, return ae
* fobj["call"]={}            : executed code within function: calls and constructs; new'call'function expressions
* fobj["call"]["user"]=[]    : user defined functions
* fobj["call"]["js"]=[]      : js built ins
* fobj["call"]["tree"]={}    : sub function tree
* fobj["call"]["allpmut"]=[] : all pmut in subfunctions

##### Schema types
* ""   : STR : string
* 0    : INT : integer
* 0.0  : FLT : float
* {}   : OBJ : dict
* []   : LST : list
* [{}] : list of dicts


#### Uses pyesprima : https://github.com/int3/pyesprima
