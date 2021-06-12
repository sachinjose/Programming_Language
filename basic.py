########################################################
##	IMPORTS
########################################################
from strings_with_arrows import *
import string

########################################################
##	CONSTANTS
########################################################

DIGITS = '0123456789'
LETTERS = string.ascii_letters ##string of all ascii letters 
LETTERS_DIGITS = LETTERS+DIGITS ##characterse allowed for variable names 


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
		result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
		return result

class IllegalCharError(Error): ##sub class of error invoked when a lexer comes across a character it doesnt support
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start,pos_end,'Illegal Character',details)

class ExpectedCharError(Error): ##sub class of error invoked when a parser comes across an invalid syntax
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start,pos_end,'Expected Character',details)

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
TT_IDENTIFIER = 'IDENTIFIER'
TT_EQ = 'EQ'
TT_KEYWORD = 'KEYWORD'
TT_EE = 'EE' ##double Equal
TT_NE = 'NE' ##not equal
TT_LT = 'LT' ##Less than
TT_GT = 'GT' ## Greater than 
TT_LTE = 'LTE' ##Less than or equal to 
TT_GTE = 'GTE' ##Greater then or equal to 
TT_COMMA = 'COMMA'
TT_ARROW = 'ARROW'


KEYWORDS = ['VAR', 'OR','AND','NOT','IF','THEN','ELIF','ELSE', 'FOR', 'TO','STEP','FUN','WHILE',] ##reserved keywords for language

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

	def matches(self,type_,value):
		return self.type == type_ and self.value == value

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
			elif self.current_char in LETTERS: ##for letters
				tokens.append(self.make_identifier())##create the variables
			elif self.current_char == '+':
				tokens.append(Token(TT_PLUS, pos_start = self.pos))
				self.advance()
			elif self.current_char == '-': ##minus and arrow token 
				tokens.append(self.make_minus_or_arrow())
			elif self.current_char == '*':
				tokens.append(Token(TT_MUL, pos_start = self.pos))
				self.advance()
			elif self.current_char == '/':
				tokens.append(Token(TT_DIV, pos_start = self.pos))
				self.advance()
			elif self.current_char == '=':
				tokens.append(self.make_equals()) ##makes = character if there is 1 equal character and == if two equal characters
			elif self.current_char == '<':
				tokens.append(self.make_less_than()) ##makes > character if there is 1 less than character and <= if the next character is like that 
			elif self.current_char == '>':
				tokens.append(self.make_greater_than()) ##makes < character if there is 1 equal character and >= if the next characters is like that
			elif self.current_char == '^':
				tokens.append(Token(TT_POW, pos_start = self.pos))
				self.advance()
			elif self.current_char == '!':
				tok,error = self.make_not_equals()##check if the next token after this is a = for != else it will return a not equals token
				if error:
					return [],error
				tokens.append(tok)
				self.advance()
			elif self.current_char == '(':
				tokens.append(Token(TT_LPAREN, pos_start = self.pos))
				self.advance()
			elif self.current_char == ',':
				tokens.append(Token(TT_COMMA, pos_start = self.pos))
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
	
	def make_identifier(self):
		id_str = '' ##the string of numbers containing variable name
		pos_start = self.pos.copy() ##copy the current position 

		while self.current_char!=None and self.current_char in LETTERS_DIGITS + '_' :
			id_str += self.current_char
			self.advance()

		if id_str in KEYWORDS:	##check if it is a keyword or a identifier
			tok_type = TT_KEYWORD
		else:
			tok_type = TT_IDENTIFIER

		return Token(tok_type,id_str,pos_start,self.pos)

	def make_minus_or_arrow(self):
		tok_type = TT_MINUS
		pos_start = self.pos.copy()

		self.advance()

		if self.current_char == '>':
			self.advance()
			tok_type = TT_ARROW

		return Token(tok_type,pos_start,pos_end = self.pos)



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

	def make_not_equals(self):
		pos_start = self.pos.copy()
		self.advance()

		if self.current_char.tok_type == '=':
			self.advance()
			return Token(TT_NE, pos_start,pos_end = self.pos), None

		self.advance()
		return None, ExpectedCharError(pos_start,self.pos,"Expected character '=' after ! ")

	def make_equals(self):
		tok_type = TT_EQ
		pos_start = self.pos.copy()
		self.advance()

		if self.current_char == '=':
			self.advance()
			tok_type = TT_EE

		return Token(tok_type,pos_start = pos_start, pos_end = self.pos)

	def make_less_than(self):
		tok_type = TT_LT
		pos_start = self.pos.copy()
		self.advance()

		if self.current_char == '=':
			self.advance()
			tok_type = TT_LTE

		return Token(tok_type,pos_start = pos_start, pos_end = self.pos)

	def make_greater_than(self):
		tok_type = TT_GT
		pos_start = self.pos.copy()
		self.advance()

		if self.current_char == '=':
			self.advance()
			tok_type = TT_GTE

		return Token(tok_type,pos_start = pos_start, pos_end = self.pos)		

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

class VarAccessNode:
	def __init__(self,var_name_tok):
		self.var_name_tok = var_name_tok
		self.pos_start = self.var_name_tok.pos_start 
		self.pos_end = self.var_name_tok.pos_end

class VarAssignNode:
	def __init__(self, var_name_tok, value_node):
		self.var_name_tok = var_name_tok
		self.value_node = value_node
		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.var_name_tok.pos_end

class IfNode:
	def __init__(self, cases, else_case):
		self.cases = cases
		self.else_case = else_case
		self.pos_start = self.cases[0][0].pos_start ##position of the first case
		if self.else_case:
			self.pos_end = (self.else_case).pos_end ##position of the else casae if it exists
		else:
			self.pos_end = (self.cases[len(self.cases) - 1][0]).pos_end ##position of the last elif case

class ForNode:
	def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node):
		self.var_name_tok = var_name_tok ##name of the variable in the for statement 
		self.start_value_node = start_value_node ##value the loop will start off at 
		self.end_value_node = end_value_node ##value it will go up to 
		self.step_value_node = step_value_node ##value of the increments , one is provided 
		self.body_node = body_node ##this is what evaulated on every iteration 
		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.var_name_tok.pos_end

class WhileNode:
	def __init__(self, condition_node, body_node):
		self.condition_node = condition_node ##condition that is to be evaluated 
		self.body_node = body_node ##this is what evaulated on every iteration 
		self.pos_start = self.condition_node.pos_start
		self.pos_end = self.condition_node.pos_end

class FuncDefNode:
	def __init__(self, var_name_tok, arg_name_toks, body_node):
		self.var_name_tok = var_name_tok ##name of the function. None if the function is anonymous
		self.arg_name_toks = arg_name_toks ##name of the argumenets for a function 
		self.body_node = body_node ##body tht is to evaulated when the function is called 

		if self.var_name_tok:##if function isnit anonoymous
			self.pos_start = self.var_name_tok.pos_start
		elif len(self.arg_name_toks) > 0: ##if there are arguemts set pos start to the first arguments postition 
			self.pos_start = self.arg_name_toks[0].pos_start
		else:
			self.pos_start = self.body_node.pos_start

		self.pos_end = self.body_node.pos_end

class CallNode:
	def __init__(self, node_to_call, arg_nodes):
		self.node_to_call = node_to_call
		self.arg_nodes = arg_nodes
		self.pos_start = self.node_to_call.pos_start

		if len(self.arg_nodes) > 0:
			self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
		else:
			self.pos_end = self.node_to_call.pos_end


########################################################
##	PARSE RESULT
########################################################

class ParseResult:
	def __init__(self):
		self.error = None
		self.node = None
		self.advance_count = 0 ##to check if the error needs to be overwritten, how many times we advacned

	def register_advancements(self):
		self.advance_count+=1

	def register(self,res):##take in  a parse result or a node 
		self.advance_count += res.advance_count
		if res.error:
			self.error = res.error
		return res.node ##extract the node and return it 


	def success(self, node):
		self.node = node
		return self

	def failure(self,error):
		if not self.error or self.advance_count == 0 :
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

	def advance(self, ): ##move parser by 1
		self.tok_idx += 1
		if self.tok_idx < len(self.tokens):
			self.current_tok = self.tokens[self.tok_idx]
		return self.current_tok

	#########################################################

	def parse(self):	
		res = self.expr() ##result after parsing expression
		if not res.error and self.current_tok.type != TT_EOF: ##still havennt reached the EOF even though we have finished it means we have a syntax error 
			return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected '+', '-' , '*' '/' or '^' "))
		return res
	#########################################################

	def atom(self):
		res = ParseResult()
		tok = self.current_tok

		if tok.type in (TT_INT,TT_FLOAT):
			res.register_advancements()
			self.advance()
			return res.success(NumberNode(tok)) 

		elif tok.type == TT_IDENTIFIER:
			res.register_advancements()
			self.advance()
			return res.success(VarAccessNode(tok))

		elif tok.type == TT_LPAREN:
			res.register_advancements()
			self.advance()
			expr = res.register(self.expr())
			if res.error:
				return res
			if self.current_tok.type == TT_RPAREN:
				res.register_advancements()
				self.advance()
				return res.success(expr)
			else:
				return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')' "))

		elif tok.matches(TT_KEYWORD, 'IF'):
			if_expr = res.register(self.if_expr())
			if res.error:
				return res
			return res.success(if_expr)

		elif tok.matches(TT_KEYWORD, 'FOR'):
			for_expr = res.register(self.for_expr())
			if res.error:
				return res
			return res.success(for_expr)

		elif tok.matches(TT_KEYWORD, 'WHILE'):
			while_expr = res.register(self.while_expr())
			if res.error:
				return res
			return res.success(while_expr)

		elif tok.matches(TT_KEYWORD, 'FUN'):
			func_def = res.register(self.func_def())
			if res.error:
				return res
			return res.success(func_def)

		return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, "Expected int, float, Identifier or '+', '-', or '(' , 'IF', 'FOR', 'WHILE', 'FUN'")) ## if the token type is not INT or FLOAT

	###################################

	def if_expr(self):
		res = ParseResult()
		cases = [] ##list of tuples of condition and expressions which will be evaluated if the condition is true
		else_case = None

		if not self.current_tok.matches(TT_KEYWORD, 'IF'): ##if we cant find the if keyword return error 
			return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,f"Expected 'IF'"))

		res.register_advancements() ##move forward when we find the if keyword
		self.advance()

		condition = res.register(self.expr())
		if res.error: return res

		if not self.current_tok.matches(TT_KEYWORD, 'THEN'):
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'THEN'"
			))

		res.register_advancements()
		self.advance()

		expr = res.register(self.expr())
		
		if res.error: 
			return res
		
		cases.append((condition, expr)) ###look for an expression which is a condition and append it to the conditon expression

		while self.current_tok.matches(TT_KEYWORD, 'ELIF'): ## if the next keyword is elif then we advance to the next token 
			res.register_advancements()
			self.advance()

			condition = res.register(self.expr())

			if res.error: return res

			if not self.current_tok.matches(TT_KEYWORD, 'THEN'): ##look for a then keyword and return if we can't find it 
				return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,f"Expected 'THEN'"))

			res.register_advancements()
			self.advance()

			expr = res.register(self.expr()) ##expressoin is registered

			if res.error: 
				return res
			
			cases.append((condition, expr)) 

		if self.current_tok.matches(TT_KEYWORD, 'ELSE'):
			res.register_advancements()
			self.advance()

			else_case = res.register(self.expr())
			if res.error: 
				return res

		return res.success(IfNode(cases, else_case))

	def for_expr(self):
		res = ParseResult()

		if not self.current_tok.matches(TT_KEYWORD, 'FOR'):
			return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, f"Expected 'FOR'"))

		res.register_advancements()
		self.advance()

		if self.current_tok.type != TT_IDENTIFIER:
			return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,f"Expected identifier"))

		var_name = self.current_tok
		res.register_advancements()
		self.advance()

		if self.current_tok.type != TT_EQ:
			return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,f"Expected '='"))
		
		res.register_advancements()
		self.advance()

		start_value = res.register(self.expr())
		if res.error: 
			return res

		if not self.current_tok.matches(TT_KEYWORD, 'TO'):
			return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,f"Expected 'TO'"))
		
		res.register_advancements()
		self.advance()

		end_value = res.register(self.expr())

		if res.error: 
			return res

		if self.current_tok.matches(TT_KEYWORD, 'STEP'):

			res.register_advancements()
			self.advance()

			step_value = res.register(self.expr())

			if res.error: 
				return res

		else:

			step_value = None ## as step is optional 

		if not self.current_tok.matches(TT_KEYWORD, 'THEN'):
			return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,f"Expected 'THEN'"))

		res.register_advancements()
		self.advance()

		body = res.register(self.expr())
		if res.error: 
			return res

		return res.success(ForNode(var_name, start_value, end_value, step_value, body))

	def while_expr(self):
		res = ParseResult()

		if not self.current_tok.matches(TT_KEYWORD, 'WHILE'):
			return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,f"Expected 'WHILE'"))

		res.register_advancements()
		self.advance()

		condition = res.register(self.expr())
		if res.error: 
			return res

		if not self.current_tok.matches(TT_KEYWORD, 'THEN'):
			return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,f"Expected 'THEN'"))

		res.register_advancements()
		self.advance()

		body = res.register(self.expr())
		if res.error: 
			return res

		return res.success(WhileNode(condition, body))
	
	def power(self):
		return self.bin_op(self.call,(TT_POW,),self.factor)

	def call(self):
		res = ParseResult()
		atom = res.register(self.atom())
		if res.error: 
			return res

		if self.current_tok.type == TT_LPAREN:
			res.register_advancements()
			self.advance()
			arg_nodes = []

			if self.current_tok.type == TT_RPAREN:
				res.register_advancements()
				self.advance()
			else:
				arg_nodes.append(res.register(self.expr()))
				if res.error:
					return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,"Expected ')', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(' or 'NOT'"))

				while self.current_tok.type == TT_COMMA:
					res.register_advancements()
					self.advance()

					arg_nodes.append(res.register(self.expr()))
					if res.error: 
						return res

				if self.current_tok.type != TT_RPAREN:
					return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,f"Expected ',' or ')'"))

				res.register_advancements()
				self.advance()

			return res.success(CallNode(atom, arg_nodes))
		return res.success(atom)

	def factor(self):

		res = ParseResult()
		tok = self.current_tok

		if tok.type in (TT_PLUS, TT_MINUS):

			res.register_advancements()
			self.advance()

			factor = res.register(self.factor())

			if res.error:
				return res
			
			else:
				return res.success(UnaryOpNode(tok,factor))

		return self.power()
		

	def term(self):
		return self.bin_op(self.factor, (TT_MUL,TT_DIV))

	def arith_expr(self):
		return self.bin_op(self.term, (TT_PLUS,TT_MINUS))

	def comp_expr(self):
		res = ParseResult()

		if self.current_tok.matches(TT_NE,'NE'):
			op_tok = self.current_tok
			res.register_advancements()
			self.advance()

			node = res.register(self.comp_expr())

			if res.error:
				return res

			return res.success(UnaryOpNode(op_tok,node))

		node = res.register(self.bin_op(self.arith_expr,(TT_EE,TT_NE,TT_LT,TT_GT,TT_LTE,TT_GTE)))

		if res.error:
			return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected int, float, Identifier or '+', '-', or 'NOT' "))

		return res.success(node)

	def expr(self):
		res = ParseResult()
		if self.current_tok.matches(TT_KEYWORD,'VAR'):
			res.register_advancements()
			self.advance()

			if self.current_tok.type != TT_IDENTIFIER:
				return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,"Expected identifier"))

			var_name = self.current_tok

			res.register_advancements()
			self.advance()

			if self.current_tok.type != TT_EQ:
				return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,"Expected '=' "))

			res.register_advancements()
			self.advance()
			expr = res.register(self.expr())
			if res.error:
				return res

			return res.success(VarAssignNode(var_name,expr))


		node = res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD,"AND"),(TT_KEYWORD,"OR"))))

		if res.error:
			return res.failure(InvalidSyntaxError(self.current_tok.pos_start,self.current_tok.pos_end,"Expected VAR, 'IF', 'FOR', 'WHILE', 'FUN',int, float, Identifier or '+', '-', or '(' ")) ##overwrite error with term 
		else:
			return res.success(node)

	def bin_op(self, func_a, ops, func_b=None):
		if func_b == None:
			func_b = func_a

		res = ParseResult()
		left = res.register(func_a()) ## if there is an error in the func it will be registered to the res obj 
		if res.error:
			return res
		while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
			op_tok = self.current_tok
			res.register_advancements()
			self.advance()
			right = res.register(func_b())
			if res.error:
				return res
			left = BinOpNode(left,op_tok,right)
		return res.success(left)

	def func_def(self):
		res = ParseResult()

		if not self.current_tok.matches(TT_KEYWORD, 'FUN'):
			return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,f"Expected 'FUN'"))

		res.register_advancements()
		self.advance()


		if self.current_tok.type == TT_IDENTIFIER:

			var_name_tok = self.current_tok
			res.register_advancements()
			self.advance()
			
			if self.current_tok.type != TT_LPAREN:
				return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,f"Expected '('"))
			
		else:
			var_name_tok = None
			if self.current_tok.type != TT_LPAREN:
				return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,f"Expected identifier or '('"))
		
		res.register_advancements()
		self.advance()
		arg_name_toks = []

		if self.current_tok.type == TT_IDENTIFIER:##checking for arguments
			arg_name_toks.append(self.current_tok)
			res.register_advancements()
			self.advance()
			
			while self.current_tok.type == TT_COMMA:##check for multiple areguments 
				res.register_advancements()
				self.advance()

				if self.current_tok.type != TT_IDENTIFIER:
					return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,f"Expected identifier"))

				arg_name_toks.append(self.current_tok)
				res.register_advancements()
				self.advance()
			
			if self.current_tok.type != TT_RPAREN:
				return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,f"Expected ',' or ')'"))

		else:
			if self.current_tok.type != TT_RPAREN:
				return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,f"Expected identifier or ')'"))

		res.register_advancements()
		self.advance()

		if self.current_tok.type != TT_ARROW: ##check arrow else error 
			return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,	f"Expected '->'"))

		res.register_advancements()
		self.advance()
		node_to_return = res.register(self.expr()) ##expression to be evaulatued for function
		if res.error: 
			return res

		return res.success(FuncDefNode(var_name_tok,arg_name_toks,node_to_return))




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

class Value:
	def __init__(self):
		self.set_pos()
		self.set_context()

	def set_pos(self, pos_start = None, pos_end = None): ## if we face an error we need to know where the error is in 
		self.pos_start = pos_start
		self.pos_end = pos_end
		return self

	def set_context(self, context=None):##Context for error handling 
		self.context = context
		return self

	def added_to(self, other):
		return None, self.illegal_operation(other)

	def subbed_by(self, other):
		return None, self.illegal_operation(other)

	def multed_by(self, other):
		return None, self.illegal_operation(other)

	def dived_by(self, other):
		return None, self.illegal_operation(other)

	def powed_by(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_eq(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_ne(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_lt(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_gt(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_lte(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_gte(self, other):
		return None, self.illegal_operation(other)

	def anded_by(self, other):
		return None, self.illegal_operation(other)

	def ored_by(self, other):
		return None, self.illegal_operation(other)

	def notted(self):
		return None, self.illegal_operation(other)

	def execute(self, args):
		return RTResult().failure(self.illegal_operation())

	def copy(self):
		raise Exception('No copy method defined')

	def is_true(self):
		return False

	def illegal_operation(self, other=None):
		if not other: 
			other = self
		return RTError(self.pos_start, other.pos_end,'Illegal operation',self.context)

class Number(Value):
	def __init__(self,value):
		self.value = value
		self.set_pos()
		self.set_context()

	def added_to(self,other):
		if isinstance(other, Number): ##check if the value that we are operating on is a number
			return Number(self.value + other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def subbed_by(self,other):
		if isinstance(other, Number): ##check if the value that we are operating on is a number
			return Number(self.value - other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def multed_by(self,other):
		if isinstance(other, Number): ##check if the value that we are operating on is a number
			return Number(self.value * other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def dived_by(self,other):
		if isinstance(other, Number): ##check if the value that we are operating on is a number
			if other.value == 0:
				return None,
			return Number(self.value / other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def powed_by(self, other):
		if isinstance(other, Number): ##return poer 
			return Number(self.value ** other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_eq(self, other):
		if isinstance(other, Number): ## comparison operator ==
			return Number(int(self.value == other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_ne(self, other):
		if isinstance(other, Number): ## comparison for !=
			return Number(int(self.value != other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_lt(self, other):
		if isinstance(other, Number): ##compairon for <
			return Number(int(self.value < other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_gt(self, other):
		if isinstance(other, Number): ##comparion for >
			return Number(int(self.value > other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_lte(self, other):
		if isinstance(other, Number): ##comparison for less than or equal to <=
			return Number(int(self.value <= other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def get_comparison_gte(self, other):
		if isinstance(other, Number): ##comparison for greater than or equal to >=
			return Number(int(self.value >= other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def anded_by(self, other):
		if isinstance(other, Number): ##comparison for and
			return Number(int(self.value and other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def ored_by(self, other):
		if isinstance(other, Number): ##comparison for or 
			return Number(int(self.value or other.value)).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def notted(self): ##comparison for not function
		if self.value == 0:
			return Number(1).set_context(self.context), None
		else :
			return Number(0).set_context(self.context), None

	def is_true(self):
		return self.value != 0

	def copy(self):
		copy = Number(self.value)
		copy.set_pos(self.set_pos,self.pos_end)
		copy.set_context(self.context)
		return copy

	def __repr__(self):
		return str(self.value)

class Function(Value):
	def __init__(self, name, body_node, arg_names):
		super().__init__()
		self.name = name or "<anonymous>" ##dunction van have a name of an anonymous fn 
		self.body_node = body_node
		self.arg_names = arg_names

	def execute(self, args): ##this will be called whenever the function is executed. 
		res = RTResult()
		interpreter = Interpreter()
		new_context = Context(self.name, self.context, self.pos_start)
		new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)

		if len(args) > len(self.arg_names):
			return res.failure(RTError(self.pos_start, self.pos_end,f"{len(args) - len(self.arg_names)} too many args passed into '{self.name}'",self.context))
		
		if len(args) < len(self.arg_names):
			return res.failure(RTError(self.pos_start, self.pos_end,f"{len(self.arg_names) - len(args)} too few args passed into '{self.name}'",self.context))

		for i in range(len(args)):
			arg_name = self.arg_names[i]
			arg_value = args[i]
			arg_value.set_context(new_context) ##for every argument we need to update its context to the arguments context
			new_context.symbol_table.set(arg_name, arg_value)

		value = res.register(interpreter.visit(self.body_node, new_context))
		if res.error: 
			return res
		return res.success(value)

	def copy(self):
		copy = Function(self.name, self.body_node, self.arg_names)
		copy.set_context(self.context)
		copy.set_pos(self.pos_start, self.pos_end)
		return copy

	def __repr__(self): ##to see when its printed in the terminal 
		return f"<function {self.name}>"


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
		##to access the symbol table within the interpreter so that we can add and retrieve variables
		self.symbol_table = None

########################################################
##	SYMBOL TABLE
########################################################

class SymbolTable: ##the symbol table keeps track of functions 
	def __init__(self, parent=None):
		self.symbols = {}
		self.parent = parent ##to keep track of global variables. 

	def get(self, name):
		value = self.symbols.get(name,None)
		if value == None and self.parent : ##check in parent symbol table
			return self.parent.get(name)
		return value

	def set(self,name,value):
		self.symbols[name] = value

	def remove(self, name):
		del self.symbols[name]


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

	def visit_VarAccessNode(self,node, context):
		res = RTResult()
		var_name = node.var_name_tok.value
		value = context.symbol_table.get(var_name)

		if not value:
			return res.failure(RTError(node.pos_start,node.pos_end, f'{var_name} is not defined', context))

		value = value.copy().set_pos(node.pos_start,node.pos_end)
		return res.success(value)

	def visit_VarAssignNode(self,node, context):
		res = RTResult()
		var_name = node.var_name_tok.value
		value = res.register(self.visit(node.value_node, context))
		if res.error:
			return 
		context.symbol_table.set(var_name,value)
		return res.success(value)

	def visit_BinOpNode(self,node,context): #visit binary operation node 
		res = RTResult()
		left = res.register(self.visit(node.left_node,context))
		if res.error:
			return res
		right = res.register(self.visit(node.right_node,context))
		if res.error:
			return res

		##Operations based on the below nodes
		if node.op_tok.type == TT_PLUS:
			result, error = left.added_to(right)
		elif node.op_tok.type == TT_MINUS:
			result, error = left.subbed_by(right)
		elif node.op_tok.type == TT_MUL:
			result, error = left.multed_by(right)
		elif node.op_tok.type == TT_DIV:
			result, error = left.dived_by(right)
		elif node.op_tok.type == TT_POW:
			result, error = left.powed_by(right)
		elif node.op_tok.type == TT_EE:
			result, error = left.get_comparison_eq(right)
		elif node.op_tok.type == TT_NE:
			result, error = left.get_comparison_ne(right)
		elif node.op_tok.type == TT_LT:
			result, error = left.get_comparison_lt(right)
		elif node.op_tok.type == TT_GT:
			result, error = left.get_comparison_gt(right)
		elif node.op_tok.type == TT_LTE:
			result, error = left.get_comparison_lte(right)
		elif node.op_tok.type == TT_GTE:
			result, error = left.get_comparison_gte(right)
		elif node.op_tok.matches(TT_KEYWORD, 'AND'):
			result, error = left.anded_by(right)
		elif node.op_tok.matches(TT_KEYWORD, 'OR'):
			result, error = left.ored_by(right)

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
			number, error = number.multed_by(Number(-1))

		elif node.op_tok.matches(TT_KEYWORD, 'NOT'):
			number, error = number.notted()

		if res.error:
			return res.failure(error)
		else:
			return res.success(number.set_pos(node.pos_start, node.pos_end))

	def visit_IfNode(self, node, context):
		res = RTResult()

		for condition, expr in node.cases: ##iterate throught the cases 
			condition_value = res.register(self.visit(condition, context))
			if res.error: 
				return res

			if condition_value.is_true(): ##condition evaluatest to be true. Evaluate the expression now 
				expr_value = res.register(self.visit(expr, context))
				if res.error: 
					return res
				return res.success(expr_value)

		if node.else_case:
			else_value = res.register(self.visit(node.else_case, context))
			if res.error: 
				return res
			return res.success(else_value)

		return res.success(None)

	def visit_ForNode(self, node, context):
		res = RTResult()
		start_value = res.register(self.visit(node.start_value_node, context))
		
		if res.error: 
			return res

		end_value = res.register(self.visit(node.end_value_node, context))
		
		if res.error: 
			return res

		if node.step_value_node:
			step_value = res.register(self.visit(node.step_value_node, context))
			if res.error: 
				return res

		else:
			step_value = Number(1)

		i = start_value.value

		if step_value.value >= 0: ## if step value is positive ewe need to keep going till i < end value
			condition = lambda: i < end_value.value
		else:	##else going till i is positive 
			condition = lambda: i > end_value.value
		
		while condition():
			context.symbol_table.set(node.var_name_tok.value, Number(i)) ##set value of variable to variable name I 
			i += step_value.value

			res.register(self.visit(node.body_node, context))
			if res.error: 
				return res

		return res.success(None)

	def visit_WhileNode(self, node, context):
		res = RTResult()

		while True:
			condition = res.register(self.visit(node.condition_node, context))
			if res.error: return res

			if not condition.is_true(): break

			res.register(self.visit(node.body_node, context))
			if res.error: return res

		return res.success(None)

	def visit_FuncDefNode(self, node, context):
		res = RTResult()

		if node.var_name_tok:
			func_name = node.var_name_tok.value
		else:
			func_name = None

		body_node = node.body_node
		arg_names = [arg_name.value for arg_name in node.arg_name_toks] ##go therought each argument name in the argument name token amd we just get the value of each argument name 

		func_value = Function(func_name, body_node, arg_names).set_context(context).set_pos(node.pos_start, node.pos_end)
		
		if node.var_name_tok: ##if function has a name is to add it to the symbol table 
			context.symbol_table.set(func_name, func_value)

		return res.success(func_value)

	def visit_CallNode(self, node, context):
		res = RTResult()
		args = []

		value_to_call = res.register(self.visit(node.node_to_call, context))
		if res.error: 
			return res
	
		value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end) ##create a copy of the value we're calling 

		for arg_node in node.arg_nodes:
			args.append(res.register(self.visit(arg_node, context))) ##visit every arg_node and append it 
			if res.error: 
				return res

		return_value = res.register(value_to_call.execute(args)) ##execute the arguments
		if res.error: 
			return res
		return res.success(return_value)


########################################################
##	RUN
########################################################

global_symbol_table = SymbolTable()
global_symbol_table.set("NULL",Number(0))
global_symbol_table.set("TRUE",Number(1))
global_symbol_table.set("FALSE",Number(0))

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



















