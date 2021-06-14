# Programming_Language
 Created a Programming Language using Python

1. Created a Lexer to generate Tokens
2. Created a Parser to parse the Tokens by building a grammer tree based on grammar rules from grammar.txt 
3. Created an Interpreter to parse the Abstract Syntax Tree
4. Created a Symbol Tree to store and edit variables

VARIABLES

Declare a variable using the VAR keyword eg: VAR a = 10

IF statements work as follows. IF statements are expressions by default.

IF <condition> THEN 
	<expression>
	<expression>
ELIF <condition>THEN 
	<expression>
	<expression>
ELSE
	<expression>


FOR statements work as follows. It also takes in a STEP parameter

FOR <var_name> = <start_value> TO <end_value> THEN <expression>
FOR <var_name> = <start_value> TO <end_value> STEP <step_value> THEN <expression>
 
 eg FOR i=0 to 10 THEN result = result*i
 
 
WHILE statements work as follows 

WHILE <condition> THEN <expr>


FUNCTIONS are declared as follows

FUN <function_name> ( <arguments> ) -> <expression>

 eg FUN add(a,b) -> a+b is a function to add a and b 

FUN <function_name> ( <arguments> )
	<expression>
	<expression>

LISTS

Lists can be declared using a [] operator 
[]
[1,2,3,4]

[1,2,3,4,5] + 6 => [1,2,3,4,5,6]
[1,2,3] * [4,5,6] => [1,2,3,4,5,6]
[1,2,3]/0 => 1

NEW LINE is represented by a semi colon ;

BUILT IN FUNCTIONS 

PRINT("HELLO WORLD")
PRINT --> Print values from a list 
PRINT_RET --> Instead of printing it on the screen it will return the value that is printed 
INPUT --> For String Inputs
INPUT_INT --> For Integer Inputs
CLEAR --> To clear the screen 
IS_NUMBER --> To check if it is a number
IS_STRING --> To check if it is a string
IS_LIST --> to check if an object is a list
IS_FUNCTION --> To check if an object is a function 
APPEND -->Add Element to a list
POP -->Pop will remove an element from a list 
EXTEND --> Extend will concatenat lists together





