from node_visitor import NodeVisitor
from error import *
from symbol import *

import math

global_fields = {'PI': math.pi, 'HALF_PI': math.pi/2, 'QUARTER_PI': math.pi/4, 'TAU': math.tau, 'TWO_PI': math.pi*2, 'E': math.e}

class SemanticAnalyzer(NodeVisitor):
	def __init__(self):
		self.current_scope = None

	def error(self, error_code, token):
		raise SemanticError(
			error_code=error_code,
			token=token,
			message=f'{error_code.value} -> {token}'
		)

	def visit_UnarOperationNode(self, node):
		self.visit(node.operand)

	def visit_BinOperationNode(self, node):
		self.visit(node.leftNode)
		self.visit(node.rightNode)

	def visit_AttributeNode(self, node):
		pass

	def visit_ClassNode(self, node):
		class_symbol = ClassSymbol(node.name)
		self.current_scope.insert(class_symbol)

		class_scope = SymbolTable(
			scope_name=node.name,
			scope_level=self.current_scope.scope_level+1,
			enclosing_scope=self.current_scope
		)
		class_symbol.body = node.body
		self.current_scope = class_scope

		for i in node.body:
			self.visit(i)

		node.symbol = class_scope
		self.current_scope = self.current_scope.enclosing_scope

	def visit_NameNode(self, node):
		if node.ctx == 'Save':
			symbol = NameSymbol(node.id)
			node.symbol = symbol
			self.current_scope.insert(symbol)
			if node.id in global_fields:
				print(f'Warning: Built-in function {node.id} has been overridden.')
		if node.id in global_fields:
			return
		symbol = self.current_scope.lookup(node.id)
		if symbol is None:
			self.error(error_code=ErrorCode.ID_NOT_FOUND, token=node.id)

	def visit_FunctionNode(self, node):
		func_symbol = FunctionSymbol(node.name)
		self.current_scope.insert(func_symbol)

		function_scope = SymbolTable(
			scope_name=node.name,
			scope_level=self.current_scope.scope_level + 1,
			enclosing_scope=self.current_scope
		)
		self.current_scope = function_scope
		for param in node.args:
			var_symbol = NameSymbol(param.value.value)
			self.current_scope.insert(var_symbol)
			func_symbol.args.append(var_symbol)
		for i in node.body:
			self.visit(i)
		self.current_scope = self.current_scope.enclosing_scope
		func_symbol.body = node.body

	def visit_ConstantNode(self, node):
		pass

	def visit_AssignNode(self, node):
		self.visit(node.value)
		for i in node.targets:
			self.visit(i)

	def visit_ExprNode(self, node):
		return self.visit(node.value)

	def visit_AttributeNode(self, node):
		pass

	def visit_CompareNode(self, node):
		self.visit(node.leftNode)
		self.visit(node.rightNode)

	def visit_IfStatementsNode(self, node):
		self.visit(node.test)



	def visit_CallNode(self, node):
		name = node.func.id
		for param_node in node.args:
			self.visit(param_node.value)
		symbol = self.current_scope.lookup(name)
		node.symbol = symbol

	def visit_ReturnNode(self, node):
		self.visit(node.value)

	def visit_StatementsNode(self, node):
		global_scope = SymbolTable(
			scope_name = 'global',
			scope_level = 1,
			enclosing_scope = self.current_scope
		)
		global_scope._init_builtins()
		self.current_scope = global_scope
		for i in node.codeStrings:
			self.visit(i)
		# self.current_scope = self.current_scope.enclosing_scope