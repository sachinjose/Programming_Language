from strings_with_arrows import *

########################################################
##	CONSTANTS
########################################################

DIGITS = '0123456789'

########################################################
##	ERROR
########################################################

##class to handle the errors 

class Error:
	def __init__(self, pos_start, pos_end, error_name, details):
		self.pos_start = pos_start
		self.pos_end = pos_end
		self.error_name = error_name
		self.details = details

	def as_string(self):
		result = f'{self.error_name}:{self.details}\n' ##display error and Details
		result += f'File {self.pos_start.fn}, Line{self.pos_start.ln+1}'
		return result

class IllegalCharError(Error): ##sub class of error invoked when a lexer comes across a character it doesnt support
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start,pos_end,'Illegal Character',details)

class InvalidSyntaxError(Error): ##sub class of error invoked when a parser comes across an invalid syntax
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start,pos_end,'Invalid Syntax',details)

class RTError(Error): ##sub class of error invoked when a parser comes across an invalid syntax
	def __init__(self, pos_start, pos_end, details,context):
		super().__init__(pos_start,pos_end,'Run Time Error',details)
		self.context = context


	def as_string(self):
		result = self.generate_traceback() ##to show the contexts
		result += f'{self.error_name}: {self.details}'
		result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
		return result

	def generate_traceback(self):
		result = ''
		pos = self.pos_start
		ctx = self.context
		while ctx:
			result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
			pos = ctx.parent_entry_pos
			ctx = ctx.parent
		return 'Traceback (most recent call last):\n' + result

########################################################
##	POSITION
########################################################

class Position:
	def __init__(self, idx, ln, col, fn, ftxt):
		self.idx = idx ##index
		self.ln = ln ##line
		self.col = col ##column
		self.fn = fn ##file name
		self.ftxt = ftxt ##file text

	def advance(self, current_char=None):
		self.idx += 1
		self.col += 1

		if current_char == '\n': ##if the current character is equal to a new line 
			self.ln += 1
			self.col += 0

		return self

	def copy(self): ##create a copy of the position
		return Position(self.idx,self.ln,self.col,self.fn,self.ftxt)



########################################################
##	TOKENS
########################################################

##Constants for the different token types TT stands for Token Type

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_POW = 'POW'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF = 'EOF'


class Token:
	def __init__(self, type_, value = None, pos_start = None, pos_end = None):
		self.type = type_
		self.value = value

		if pos_start:
			self.pos_start = pos_start.copy()
			self.pos_end = pos_start.copy()
			self.pos_end.advance()

		if pos_end:
			self.pos_end = pos_end.copy()

	def __repr__(self): #Returns the Token 
		if self.value:
			return f'{self.type}:{self.value}'
		return f'{self.type}'


########################################################
##	LEXER
########################################################


class Lexer:
	def __init__(self, fn, text):
		self.fn = fn
		self.text = text
		self.pos = Position(-1, 0, -1,fn,text) ##Current Position its -1 and column  as the advance method will immediately increment it 
		self.current_char = None ##Current Character
		self.advance()

	def advance(self): #advance to the next character in the text
		self.pos.advance(self.current_char)
		if self.pos.idx < len(self.text):
			self.current_char = self.text[self.pos.idx]
		else:
			self.current_char = None

	def make_tokens(self):
		tokens = [] ##empty list of tokens to be returned 

		while self.current_char != None:
			if self.current_char in ' \t':#if the character is a space or a tab advance 
				self.advance()
			elif self.current_char in DIGITS:
				tokens.append(self.make_number()) ##since a number token can have more than one digit we call the make_number function
			elif self.current_char == '+':
				tokens.append(Token(TT_PLUS, pos_start = self.pos))
				self.advance()
			elif self.current_char == '-':
				tokens.append(Token(TT_MINUS, pos_start = self.pos))
				self.advance()
			elif self.current_char == '*':
				tokens.append(Token(TT_MUL, pos_start = self.pos))
				self.advance()
			elif self.current_char == '/':
				tokens.append(Token(TT_DIV, pos_start = self.pos))
				self.advance()
			elif self.current_char == '^':
				tokens.append(Token(TT_POW, pos_start = self.pos))
				self.advance()
			elif self.current_char == '(':
				tokens.append(Token(TT_LPAREN, pos_start = self.pos))
				self.advance()
			elif self.current_char == ')':
				tokens.append(Token(TT_RPAREN, pos_start = self.pos))
				self.advance()
			else:
				##return error because Illegal character
				pos_start = self.pos.copy()
				char = self.current_char
				self.advance()
				return [],IllegalCharError(pos_start,self.pos,"'" + char + "'")		

		tokens.append(Token(TT_EOF, pos_start = self.pos))		

		return tokens,None

	def make_number(self):
		num_str = '' ##the string of numbers containing multiple digits
		dot_count = 0 ##if there are no dots in the number its an integer but if there are dots in the number then it is a float 
		pos_start = self.pos.copy()

		while self.current_char!=None and self.current_char in DIGITS + '.' : ##checks if the current character is a digit or a dot 
			if self.current_char == '.':
				if dot_count == 1:
					break ## as we can't have more than one decimal in the number
				dot_count+= 1
				num_str += '.'

			else :
				num_str += self.current_char
			self.advance()

		if dot_count == 0:
			return Token(TT_INT,int(num_str),pos_start, pos_end = self.pos)
		else:
			return Token(TT_FLOAT, float(num_str),pos_start, pos_end = self.pos)

########################################################
##	BUILDING GRAMMAR TREE
########################################################

########################################################
##	NODES
########################################################

class NumberNode:
	def __init__(self, tok): ##number node takes in the corresponding number token 
		self.tok = tok
		self.pos_start = tok.pos_start
		self.pos_end = tok.pos_end

	def __repr__(self):
		return f'{self.tok}'

class BinOpNode: ##Node for binary operations
	def __init__(self, left_node,op_tok,right_node):
		self.left_node = left_node
		self.right_node = right_node
		self.op_tok = op_tok

		self.pos_start = left_node.pos_start
		self.pos_end = right_node.pos_end

	def __repr__(self):
		return f'({self.left_node},{self.op_tok},{self.right_node})'

class UnaryOpNode:
	def __init__(self,op_tok, node):
		self.op_tok = op_tok
		self.node = node

		self.pos_start = op_tok.pos_start
		self.pos_end = node.pos_end

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'


########################################################
##	PARSE RESULT
########################################################

class ParseResult:
	def __init__(self):
		self.error = None
		self.node = None

	def register(self, res): ##take in  a parse result or a node 
		if isinstance(res, ParseResult) : ##if result is parse result
			if res.error:
				self.error = error
			return res.node ##extract the node and return it 

		return res ##if it isnt a parse result we can just return the result 


	def success(self, node):
		self.node = node
		return self

	def failure(self,error):
		self.error = error
		return self

########################################################
##	PARSER
########################################################

class Parser:
	def __init__(self,tokens): ##initialise token and token index 
		self.tokens = tokens
		self.tok_idx = -1
		self.advance()

	def advance(self): ##move parser by 1
		self.tok_idx += 1
		if self.tok_idx < len(self.tokens):
			self.current_tok = self.tokens[self.tok_idx]
		return self.current_tok

	#########################################################

	def parse(self):	
		res = self.expr() ##result after parsing expression
		if not res.error and self.current_tok.type != TT_EOF: ##still havennt reached the EOF even though we have finished it means we have a syntax error 
			return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected '+', '-' , '*' or '/' "))
		return res
	#########################################################

	def factor(self):
		res = ParseResult()
		tok = self.current_tok

		if tok.type in (TT_INT,TT_FLOAT):
			res.register(self.advance())
			return res.success(NumberNode(tok)) 

		elif tok.type == TT_LPAREN:
			res.register(self.advance())
			expr = res.register(self.expr())
			if res.error:
				return res
			if self.current_tok.type == TT_RPAREN:
				res.register(self.advance())
				return res.success(expr)
			else:
				return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')' "))
		return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, "Expected int, float or '+', '-', or '(' ")) ## if the token type is not INT or FLOAT


	def power(self):
		return self.bin_op(self.atom,(TT_POW,),self.factor)

	def factor(self):
		res = ParseResult()
		tok = self.current_tok

		if tok.type in (TT_PLUS, TT_MINUS):
			res.register(self.advance())
			factor = res.register(self.factor())
			if res.error:
				return res
			else:
				return res.success(UnaryOpNode(tok,factor))

		return self.power()
		

	def term(self):
		return self.bin_op(self.factor, (TT_MUL,TT_DIV))

	def expr(self):
		return self.bin_op(self.term,(TT_PLUS,TT_MINUS))

	def bin_op(self, func_a, ops, func_b=None):
		if func_b == None:
			func_b = func_a

		res = ParseResult()
		left = res.register(func_a()) ## if there is an error in the func it will be registered to the res obj 
		if res.error:
			return res
		while self.current_tok.type in ops:
			op_tok = self.current_tok
			res.register(self.advance())
			right = res.register(func_b())
			if res.error:
				return res
			left = BinOpNode(left,op_tok,right)
		return res.success(left)

########################################################
##	RUNTIME RESULT
########################################################

class RTResult:
	def __init__(self):
		self.value = None
		self.error = None

	def register(self,res):
		if res.error:
			self.error = res.error

		return res.value

	def success(self, value):
		self.value = value
		return self

	def failure(self, error):
		self.error = error
		return self

########################################################
##	Value
########################################################

##for storing numbers and operating on them with other numbers. 

class Number:
	def __init__(self,value):
		self.value = value
		self.set_pos()
		self.set_context()


	def set_pos(self, pos_start = None, pos_end = None): ## if we face an error we need to know where the error is in 
		self.pos_start = pos_start
		self.pos_end = pos_end
		return self

	def set_context(self, context=None):##Context for error handling 
		self.context = context
		return self

	def added_to(self,other):
		if isinstance(other, Number): ##check if the value that we are operating on is a number
			return Number(self.value + other.value).set_context(self.context), None

	def subbed_by(self,other):
		if isinstance(other, Number): ##check if the value that we are operating on is a number
			return Number(self.value - other.value).set_context(self.context), None

	def multed_by(self,other):
		if isinstance(other, Number): ##check if the value that we are operating on is a number
			return Number(self.value * other.value).set_context(self.context), None

	def dived_by(self,other):
		if isinstance(other, Number): ##check if the value that we are operating on is a number
			if other.value == 0:
				return None,RTError(other.pos_start,other.pos_end, 'Division by Zero',self.context)
			return Number(self.value / other.value).set_context(self.context), None

	def powed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value ** other.value).set_context(self.context), None

	def __repr__(self):
		return str(self.value)

#######################################
# CONTEXT
#######################################

##for context of the errors to trace back the errors to the parent functions that causes it, To give more context to the runtime errors 
##
class Context:
	def __init__(self, display_name, parent=None, parent_entry_pos=None ): 
		self.display_name = display_name
		self.parent = parent
		self.parent_entry_pos = parent_entry_pos

########################################################
##	INTERPRETER
########################################################

class Interpreter:
	def visit(self, node, context):##for visiting each node ## we want a different visit for different node types
		method_name = f'visit_{type(node).__name__}'
		## the method_name will be different based on the type of node that we are visiting 
		## visit_BinaryOpNode
		## visit_NumberNode
		method = getattr(self, method_name, self.no_visit_method) ##get the function names method_name
		return method(node,context)

	def no_visit_method(self, node, context):
		raise Exception(f'No visit_{type(node).__name__} method defined')

	#######################################################################

	def visit_NumberNode(self,node, context): ##visit number node 
		return RTResult().success(Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))

	def visit_BinOpNode(self,node,context): #visit binary operation node 
		res = RTResult()
		left = res.register(self.visit(node.left_node,context))
		if res.error:
			return res
		right = res.register(self.visit(node.right_node,context))
		if res.error:
			return res

		if node.op_tok.type == TT_PLUS:
			result,error = left.added_to(right)
		elif node.op_tok.type == TT_MINUS:
			result,error = left.subbed_by(right)
		elif node.op_tok.type == TT_DIV :
			result,error = left.dived_by(right)
		elif node.op_tok.type == TT_MUL :
			result,error = left.multed_by(right)
		elif node.op_tok.type == TT_POW:
			result, error = left.powed_by(right)

		if error:
			return res.failure(error)
		return res.success(result.set_pos(node.pos_start, node.pos_end))

	def visit_UnaryOpNode(self,node,context):
		res = RTResult()
		number = res.register(self.visit(node.node,context)) 

		if res.error:
			return res

		error = None

		if node.op_tok.type == TT_MINUS:
			number,error= number.multed_by(Number(-1))

		if res.error:
			return res.failure(error)
		else:
			return res.success(number.set_pos(node.pos_start, node.pos_end))
########################################################
##	RUN
########################################################

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
	result = interpreter.visit(ast.node, context)

	return result.value,result.error 



















