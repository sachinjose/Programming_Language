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
##	NODES
########################################################

class NumberNode:
	def __init__(self, tok): ##number node takes in the corresponding number token 
		self.tok = tok
		self.pos_start = tok.pos_start
		self.pos_end = tok.pos_end

	def __repr__(self):
		return f'{self.tok}'

class StringNode:
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

class ListNode:
  def __init__(self, element_nodes, pos_start, pos_end):
    self.element_nodes = element_nodes
    self.pos_start = pos_start
    self.pos_end = pos_end

class IfNode:
	def __init__(self, cases, else_case):
		self.cases = cases
		self.else_case = else_case

		self.pos_start = self.cases[0][0].pos_start##position of the first case
		self.pos_end = (self.else_case or self.cases[len(self.cases) - 1])[0].pos_end ##position of the else casae if it exists

class ForNode:
	def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node, should_return_null):
		self.var_name_tok = var_name_tok ##name of the variable in the for statement 
		self.start_value_node = start_value_node ##value the loop will start off at 
		self.end_value_node = end_value_node ##value it will go up to 
		self.step_value_node = step_value_node ##value of the increments , one is provided 
		self.body_node = body_node ##this is what evaulated on every iteration 
		self.should_return_null = should_return_null
		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.var_name_tok.pos_end

class WhileNode:
	def __init__(self, condition_node, body_node, should_return_null):
		self.condition_node = condition_node ##condition that is to be evaluated 
		self.body_node = body_node ##this is what evaulated on every iteration 
		self.pos_start = self.condition_node.pos_start
		self.pos_end = self.condition_node.pos_end
		self.should_return_null = should_return_null

class FuncDefNode:
	def __init__(self, var_name_tok, arg_name_toks, body_node,should_auto_return):
		self.var_name_tok = var_name_tok ##name of the function. None if the function is anonymous
		self.arg_name_toks = arg_name_toks ##name of the argumenets for a function 
		self.body_node = body_node ##body tht is to evaulated when the function is called 
		self.should_auto_return = should_auto_return ##if there isnt a return statemetn 

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

class ReturnNode:
	def __init__(self, node_to_return, pos_start, pos_end):
		self.node_to_return = node_to_return
		self.pos_start = pos_start
		self.pos_end = pos_end

class ContinueNode:
	def __init__(self, pos_start, pos_end):
		self.pos_start = pos_start
		self.pos_end = pos_end

class BreakNode:
	def __init__(self, pos_start, pos_end):
		self.pos_start = pos_start
		self.pos_end = pos_end