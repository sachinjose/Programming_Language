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
		result = f'{self.error_name}:{self.details}' ##display error and Details
		result += f'File {self.pos_start.fn}, Line{self.pos_start.ln+1}'
		return result

class IllegalCharError(Error): ##sub class of error invoked when a lexer comes across a character it doesnt support
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start,pos_end,'Illegal Character',details)

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

	def advance(self, current_char):
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
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'


class Token:
	def __init__(self, type_, value = None):
		self.type = type_
		self.value = value

	def __repr__(self): #Returns the Token 
		if self.value:
			return f'{self.value}:{self.type}'
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
				tokens.append(Token(TT_PLUS))
				self.advance()
			elif self.current_char == '-':
				tokens.append(Token(TT_MINUS))
				self.advance()
			elif self.current_char == '*':
				tokens.append(Token(TT_MUL))
				self.advance()
			elif self.current_char == '/':
				tokens.append(Token(TT_DIV))
				self.advance()
			elif self.current_char == '(':
				tokens.append(Token(TT_LPAREN))
				self.advance()
			elif self.current_char == ')':
				tokens.append(Token(TT_RPAREN))
				self.advance()
			else:
				##return error because Illegal character
				pos_start = self.pos.copy()
				char = self.current_char
				self.advance()
				return [],IllegalCharError(pos_start,self.pos,"'" + char + "'")				

		return tokens,None

	def make_number(self):
		num_str = '' ##the string of numbers containing multiple digits
		dot_count = 0 ##if there are no dots in the number its an integer but if there are dots in the number then it is a float 

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
			return Token(TT_INT,int(num_str))
		else:
			return Token(TT_FLOAT, float(num_str))

########################################################
##	RUN
########################################################

def run(fn, text):
	lexer = Lexer(fn, text)
	tokens,error = lexer.make_tokens()

	return tokens,error 



















