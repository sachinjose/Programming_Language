from strings_with_arrows import *
import string
import os
import math
import constants
from error import *
from position import *

########################################################
##	LEXER
########################################################

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
TT_LSQUARE = 'LSQUARE'
TT_RSQUARE = 'RSQUARE'
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
TT_STRING = 'STRING'
TT_NEWLINE		= 'NEWLINE'

KEYWORDS = ['VAR', 'OR','AND','NOT','IF','THEN','ELIF','ELSE', 'FOR', 'TO','STEP','FUN','WHILE','RETURN','CONTINUE','BREAK'] ##reserved keywords for language

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
			if self.current_char in ' \t':#if the character is a space or a tab advance we ignore 
				self.advance()
			if self.current_char in '#': #its a comment so we ignore
				self.advance()
			elif self.current_char in ';\n': ##new line character
				tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
				self.advance()
			elif self.current_char in constants.DIGITS:
				tokens.append(self.make_number()) ##since a number token can have more than one digit we call the make_number function
			elif self.current_char in constants.LETTERS: ##for letters
				tokens.append(self.make_identifier())##create the variables
			elif self.current_char == '+':
				tokens.append(Token(TT_PLUS, pos_start = self.pos))
				self.advance()
			elif self.current_char == '"':
				tokens.append(self.make_string())
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
			elif self.current_char == ')':
				tokens.append(Token(TT_RPAREN, pos_start = self.pos))
				self.advance()
			elif self.current_char == '[':
				tokens.append(Token(TT_LSQUARE, pos_start=self.pos))
				self.advance()
			elif self.current_char == ']':
				tokens.append(Token(TT_RSQUARE, pos_start=self.pos))
				self.advance()
			elif self.current_char == ',':
				tokens.append(Token(TT_COMMA, pos_start = self.pos))
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

		while self.current_char!=None and self.current_char in constants.LETTERS_DIGITS + '_' :
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

	def make_string(self):
		string = ''
		pos_start = self.pos.copy()
		escape_character = False
		self.advance()

		escape_characters = { 'n': '\n','t': '\t'}##escapecharacter dictionary

		while self.current_char != None and (self.current_char != '"' or escape_character):
			if escape_character:##if we get an escape charater
				string += escape_characters.get(self.current_char, self.current_char) ##we'll add the escape character
				escape_character = False
			else:
				if self.current_char == '\\':
					escape_character = True
				else:
					string += self.current_char
			self.advance()
		self.advance()

		return Token(TT_STRING, string, pos_start, self.pos)

	def make_number(self):
		num_str = '' ##the string of numbers containing multiple digits
		dot_count = 0 ##if there are no dots in the number its an integer but if there are dots in the number then it is a float 
		pos_start = self.pos.copy()

		while self.current_char!=None and self.current_char in constants.DIGITS + '.' : ##checks if the current character is a digit or a dot 
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


	def skip_comment(self):
		self.advance()

		while self.current_char != '\n':
			self.advance()

		self.advance()
