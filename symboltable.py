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