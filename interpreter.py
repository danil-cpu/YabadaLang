from node_visitor import NodeVisitor
from symbol import *
from AST import ReturnNode, AttributeNode, CompareNode
from error import *
from lexer import Lexer
from type import *
from parser_new import Parser
from semantic_analyzer import SemanticAnalyzer, global_fields
from enum import Enum
from string import Template
import time

class CallStack(list):
	def push(self, ar):
		self.append(ar)

	def peek(self):
		return self[-1]

	def __str__(self) -> str:
		s = '\n'.join(repr(ar) for ar in reversed(self))
		s = f'CALL STACK\n{s}\n\n'
		return s

	__repr__ = __str__

class ActivationRecord(dict):
	def __init__(self, name, type, nesting_level):
		self.name = name
		self.type = type
		self.nesting_level = nesting_level

	def __str__(self) -> str:
		lines = [
			f'{self.nesting_level}: {self.type.value} {self.name}'
		]
		for name, value in self.items():
			lines.append(f'\t{name:<20}: {value}')
		s = '\n'.join(lines)
		return s

	__repr__ = __str__

class ARType(Enum):
	MODULE = 'MODULE'
	FUNCTION = 'FUNCTION'
	CLASS = 'CLASS'

class Interpreter(NodeVisitor):
	def __init__(self, tree):
		self.tree = tree
		self.call_stack = CallStack()

	def visit_UnarOperationNode(self, node):
		name = node.operator.name
		if name == tokenTypes.MINUS.name:
			return -self.visit(node.operand)
		elif name == tokenTypes.PLUS.name:
			return +self.visit(node.operand)
		if name == tokenTypes.PRINT.name:
			print(self.visit(node.operand))

	def visit_BinOperationNode(self, node):
		operator = node.operator.type
		if operator.name == tokenTypes.MINUS.name:
			return self.visit(node.leftNode) - self.visit(node.rightNode)
		elif operator.name == tokenTypes.PLUS.name:
			return self.visit(node.leftNode) + self.visit(node.rightNode)
		elif operator.name == tokenTypes.MUL.name:
			return self.visit(node.leftNode) * self.visit(node.rightNode)

	def visit_ConstantNode(self, node):
		val = node.value
		if val.isdigit() or val[1:].isdigit():
			return int(val)
		if "'" in val:
			return val.replace("'", '')
		if val in ('True','False'):
			return val == 'True'

	def visit_NameNode(self, node):
		ar = self.call_stack.peek()
		value = ar.get(node.id)
		if value is None:
			if node.id in global_fields:
				value = global_fields[node.id]
		return value

	def visit_FunctionNode(self, node):
		pass

	def visit_CompareNode(self, node):
		operator = node.operator.type
		if isinstance(node.rightNode, CompareNode): # 1<2<3 equals: 1<2 and 2<3
			return self.visit(
				LogicalOperationNode(
					leftNode=node.rightNode.leftNode,
					operator=tokenTypes.AND,
					rightNode=CompareNode(
						leftNode=node.leftNode,
						operator=node.operator,
						rightNode=node.rightNode.rightNode
					)
				)
			)
		if operator.name == tokenTypes.GT.name: # > (greater than)
			return self.visit(node.leftNode) > self.visit(node.rightNode)

		if operator.name == tokenTypes.LT.name: # < (less than)
			return self.visit(node.leftNode) < self.visit(node.rightNode)

		if operator.name == tokenTypes.LESS_OR_EQUALS.name: # <= (less or equals)
			return self.visit(node.leftNode) <= self.visit(node.rightNode)

		if operator.name == tokenTypes.GREATER_OR_EQUALS.name: # >= (greater or equals)
			return self.visit(node.leftNode) >= self.visit(node.rightNode)

		if operator.name == tokenTypes.EQUALS.name: # == (equals)
			return self.visit(node.leftNode) == self.visit(node.rightNode)

	def visit_AssignNode(self, node):
		value = self.visit(node.value)
		ar = self.call_stack.peek()
		for i in node.targets:
			ar[i.id] = value
			i.symbol.__value__ = value

	def visit_ExprNode(self, node):
		return self.visit(node.value)

	def visit_CallNode(self, node):
		name = self.visit(node.func)
		symbol = node.symbol
		print(self.call_stack)
		ar = ActivationRecord(
			name=node.func.id,
			type=ARType.FUNCTION,
			nesting_level=symbol.scope_level + 1
		)
		formal_args = symbol.args
		actual_args = node.args
		for param_symbol, argument_node in zip(formal_args, actual_args):
			ar[param_symbol.__name__] = self.visit(argument_node.value)
		self.call_stack.push(ar)

		for i in symbol.body:
			if isinstance(i, ReturnNode):
				return self.visit(i.value)
			self.visit(i)

		# self.call_stack.pop()

	def visit_StatementsNode(self, node):
		ar = ActivationRecord(
			name='Main',
			type=ARType.MODULE,
			nesting_level=1
		)
		self.call_stack.push(ar)
		for i in node.codeStrings:
			self.visit(i)
			
		# self.call_stack.pop()

	def visit_AttributeNode(self, node):
		attr_path = list()
		while True:
			if isinstance(node, AttributeNode):
				attr_path.append(node.attr)
				node=node.value
			else:
				result = node
				break

		
		symbol = node.symbol
		return str(self.visit(result))
		# l = obj.locals
		# for i in attr_path[::-1]:
		# 	if isinstance(l[i], ClassNode):
		# 		l=l[i].locals
		# 	else:
		# 		return l[i]
		# print(type(node))
		pass

	def visit_IfStatementsNode(self, node):
		if self.visit(node.test):
			for i in node.body:
				self.visit(i)
		else:
			for i in node.orelse:
				self.visit(i)


	def visit_ClassNode(self, node):
		# print(dict(node.symbol))
		print(dict(self.call_stack[-1]))

	def interpret(self):
		tree = self.tree
		if tree is None:
			return str()
		return self.visit(tree)




__code__ = """
print: '*****Welcome to YabadaLang!*****';
num = 7;
if (num < 6){
	print: 'num < 6';
} else {
	print: 'num is '+num.toString;	
};
print: num;
"""

start = time.time()
lexer = Lexer(__code__)
lexer.lexAnalysis()
parser = Parser(lexer.tokenList)
rootNode = parser.parseCode()
semantic_analyzer = SemanticAnalyzer()
try:
	semantic_analyzer.visit(rootNode)
except SemanticError as e:
	print(e.message)
	exit()

interpreter = Interpreter(rootNode)
interpreter.interpret()
# print(interpreter.call_stack)
print(f'[Finished in {round(time.time()-start, 4)} sec]')
input('Press enter to continue..')