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