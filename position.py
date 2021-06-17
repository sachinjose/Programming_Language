########################################################
##	IMPORTS
########################################################
from strings_with_arrows import *
import string
import os
import math
import constants
from error import *

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