########################################################
##	IMPORTS
########################################################
from strings_with_arrows import *
import string
import os
import math
import constants
from error import *
from position import *
from lexer import *
from nodes import *
from rtresult import *
from valuenode import *
from context import *
from symboltable import *
from interpreter import *

########################################################
##	RUN
########################################################

global_symbol_table = SymbolTable()
global_symbol_table.set("NULL", Number.null)
global_symbol_table.set("FALSE", Number.false)
global_symbol_table.set("TRUE", Number.true)
global_symbol_table.set("MATH_PI", Number.math_PI)
global_symbol_table.set("PRINT", BuiltInFunction.print)
global_symbol_table.set("PRINT_RET", BuiltInFunction.print_ret)
global_symbol_table.set("INPUT", BuiltInFunction.input)
global_symbol_table.set("INPUT_INT", BuiltInFunction.input_int)
global_symbol_table.set("CLEAR", BuiltInFunction.clear)
global_symbol_table.set("CLS", BuiltInFunction.clear)
global_symbol_table.set("IS_NUM", BuiltInFunction.is_number)
global_symbol_table.set("IS_STR", BuiltInFunction.is_string)
global_symbol_table.set("IS_LIST", BuiltInFunction.is_list)
global_symbol_table.set("IS_FUN", BuiltInFunction.is_function)
global_symbol_table.set("APPEND", BuiltInFunction.append)
global_symbol_table.set("POP", BuiltInFunction.pop)
global_symbol_table.set("EXTEND", BuiltInFunction.extend)
global_symbol_table.set("LEN", BuiltInFunction.len)
global_symbol_table.set("RUN", BuiltInFunction.run)

def run(fn, text):

	##Generate tokens using Lexer 
	lexer = Lexer(fn, text)
	tokens,error = lexer.make_tokens()
	if error : 
		return None,error

	##Generate Abstract Syntax Tree using Parser
	parser = Parser(tokens)
	ast = parser.parse()
	if ast.error:
		return None, ast.error


	##Run the Program 
	interpreter = Interpreter()
	context = Context('<program>')
	context.symbol_table = global_symbol_table
	result = interpreter.visit(ast.node, context)

	return result.value,result.error 



















