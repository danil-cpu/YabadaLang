from AST import *
from token_ya import Token
from lexer import Lexer
from type import TokenType, tokenTypes
from symbol import *

from typing import Union
from copy import deepcopy
import math

class Parser(object):
	def __init__(self, tokens):

		self.tokens = tokens
		self.pos = 0
		self.scope = dict()

	def find(self, types, token) -> bool:
		for type in types:
			if type.name == token.type.name:
				return True
		return False 

	def match(self, *types) -> Union[Token, None]:
		if self.pos < len(self.tokens):
			current_token = self.tokens[self.pos]
			if self.find(types, current_token):
				self.pos += 1
				return current_token
		return None

	def require(self, *types) -> Token:
		token = self.match(*types)
		if token is None:
			raise Exception(f'На позиции {self.pos+1} ожидается -> {types[0].name}')
		return token

	def parseBody(self) -> ExpressionNode:
		self.require(tokenTypes.LFPAR)
		body = list()

		while self.match(tokenTypes.RFPAR) is None:
			body.append(self.parseExpression())
			self.pos += 1
		return body

	def parseParamsFunction(self, call=False):
		self.require(tokenTypes.LPAR)
		_id = self.match(tokenTypes.ID) if not call else self.relexpr()
		params = []
		while _id is not None:
			params.append(ParamNode(_id))
			if self.match(tokenTypes.COMMA) is not None:
				_id = self.match(tokenTypes.ID) if not call else self.relexpr()
			else:
				break
		self.require(tokenTypes.RPAR)
		return params

	def parseConstantOrName(self) -> ExpressionNode:
		constant = self.match(tokenTypes.STRING_CONST, tokenTypes.INTEGER_CONST, tokenTypes.BOOLEAN_CONST)
		if constant is not None:
			return ConstantNode(value=constant.value)
		name = self.match(tokenTypes.ID)
		if name is not None:
			if self.find([tokenTypes.LPAR], self.tokens[self.pos]):
				args = self.parseParamsFunction(call=True)
				return ExprNode(value=CallNode(func=NameNode(id=name.value, ctx=None), args=args))
			return NameNode(id=name.value, ctx=None)

	def parseIfStatements(self) -> ExpressionNode:
		self.require(tokenTypes.IF)
		self.require(tokenTypes.LPAR)
		test = self.relexpr()
		self.require(tokenTypes.RPAR)
		body = self.parseBody()
		orelse = list()
		if self.match(tokenTypes.ELSE) is not None:
			orelse=self.parseBody()
		return IfStatementsNode(test=test, orelse=orelse, body=body)


	def parseFunction(self) -> ExpressionNode:
		func = self.require(tokenTypes.ID)
		args = self.parseParamsFunction()
		body = self.parseBody()
		return FunctionNode(func.value, args, body)

	def parseClass(self) -> ExpressionNode:
		cls = self.require(tokenTypes.ID)
		body = self.parseBody()
		return ClassNode(name=cls.value, body=body)

	def parseCode(self) -> ExpressionNode:
		root = StatementsNode()
		while self.pos < len(self.tokens):
			codeStringNode = self.parseExpression()
			self.require(tokenTypes.SEMICOLON)
			root.addNode(codeStringNode)
		return root

	def relexpr(self) -> ExpressionNode:
		node = self.expr()
		operator = self.match(tokenTypes.GT, tokenTypes.LT, tokenTypes.LESS_OR_EQUALS, tokenTypes.GREATER_OR_EQUALS, tokenTypes.EQUALS)
		if operator is not None:
			node = CompareNode(leftNode=node, operator=operator, rightNode=self.relexpr())
		return node

	def expr(self, node=None) -> ExpressionNode:
		node = self.term()
		operator = self.match(tokenTypes.PLUS, tokenTypes.MINUS, tokenTypes.AND, tokenTypes.OR)
		while operator is not None:
			if operator.type in (tokenTypes.AND, tokenTypes.OR):
				node = LogicalOperationNode(leftNode=node, operator=operator.type, rightNode=self.term())
			else:
				node = BinOperationNode(leftNode=node, operator=operator, rightNode=self.term())
			operator = self.match(tokenTypes.PLUS, tokenTypes.MINUS, tokenTypes.AND, tokenTypes.OR)
		return node

	def term(self) -> ExpressionNode:
		node = self.factor()
		operator = self.match(tokenTypes.MUL, tokenTypes.DIV_FLOAT)
		while operator is not None:
			if operator.type in (tokenTypes.MUL, tokenTypes.DIV_FLOAT):
				node = BinOperationNode(leftNode=node, operator=operator, rightNode=self.factor())
			operator = self.match(tokenTypes.MUL, tokenTypes.DIV_FLOAT)
		return node

	def factor(self) -> ExpressionNode:
		if self.match(tokenTypes.PLUS) is not None:
			return UnarOperationNode(tokenTypes.PLUS, self.factor())
		if self.match(tokenTypes.MINUS) is not None:
			return UnarOperationNode(tokenTypes.MINUS, self.factor())

		constant = self.match(tokenTypes.INTEGER_CONST, tokenTypes.STRING_CONST, tokenTypes.BOOLEAN_CONST)
		if constant is not None:
			node = ConstantNode(value=constant.value)
			return node

		if self.match(tokenTypes.LPAR) is not None:
			node = self.expr()
			self.require(tokenTypes.RPAR)
			return node

		id = self.parseAttribute()
		if id is not None:
			if self.find([tokenTypes.LPAR], self.tokens[self.pos]):
				args = self.parseParamsFunction(call=True)
				return ExprNode(value=CallNode(func=NameNode(id=id.value, ctx=None), args=args))

			return id

	def parsAttr(self, ids) -> ExpressionNode:
		attr = None
		for n, i in enumerate(ids):
			if isinstance(i, (NameNode, ConstantNode)):
				if n+1 < len(ids):
					attr = AttributeNode(i, ids[n+1].value)
					ids.remove(ids[n+1])
					continue
			attr = AttributeNode(attr, i.value)
		return attr

	def parseAttribute(self) -> ExpressionNode:
		ids = [self.parseConstantOrName()]

		while self.match(tokenTypes.DOT) is not None:
			id = self.match(tokenTypes.ID)
			if id is not None:
				ids.append(id)
		if len(ids) < 2:
			return ids[0]
		attrs = self.parsAttr(ids)
		return attrs
		
	
	"""
	func ID(PARAMS){BLOCK};
	class ID{BLOCK};
	ID(PARAMS);
	ID.ATTR.ATTR..;
	ID -> get Name
	"""

	def parseExpression(self) -> ExpressionNode:
		attr = self.parseAttribute()
		if attr is None:
			if self.match(tokenTypes.FUNCTION) is not None:
				return self.parseFunction()

			if self.match(tokenTypes.CLASS) is not None:
				return self.parseClass()

			if self.match(tokenTypes.PRINT) is not None:
				return UnarOperationNode(tokenTypes.PRINT, self.relexpr())

			if self.match(tokenTypes.RETURN) is not None:
				return ReturnNode(self.relexpr())

			if self.find([tokenTypes.IF], self.tokens[self.pos]):
				return self.parseIfStatements()

		assignOperator = self.match(tokenTypes.ASSIGN)
		if assignOperator is not None:
			attr.ctx='Save'
			return AssignNode(targets=[attr], value=self.relexpr())
		if self.find([tokenTypes.LPAR], self.tokens[self.pos]):
			args = self.parseParamsFunction(call=True)
			print(args)
			return ExprNode(value=CallNode(func=attr, args=args))

		return attr
		raise SyntaxError('Syntax is invalid.')

	def run(self, node: ExpressionNode):
		if isinstance(node, ConstantNode): # Получаем значение константы и преобразуем тип в python тип.
			val = node.value
			if val.isdigit() or val[1:].isdigit():
				return int(val)
			if "'" in val:
				return val.replace("'", '')
			if val in ('True','False'):
				return val == 'True'

		if isinstance(node, UnarOperationNode): # Когда мы видим унарную операцию.
			name = node.operator.name
			if name == tokenTypes.MINUS.name:
				return -self.run(node.operand)
			elif name == tokenTypes.PLUS.name:
				return +self.run(node.operand)
			if name == tokenTypes.PRINT.name:
				print(self.run(node.operand))

		# if isinstance(node, LogicalOperationNode):
		# 	operator = node.operator
		# 	if operator.name == tokenTypes.AND.name:
		# 		return self.run(node.leftNode) and self.run(node.rightNode)
		# 	else:
		# 		return self.run(node.leftNode) or self.run(node.rightNode)

		# if isinstance(node, CompareNode):
		# 	operator = node.operator.type
		# 	if isinstance(node.rightNode, CompareNode): # 1<2<3 equals: 1<2 and 2<3
		# 		return self.run(
		# 			LogicalOperationNode(
		# 				leftNode=node.rightNode.leftNode,
		# 				operator=tokenTypes.AND,
		# 				rightNode=CompareNode(
		# 					leftNode=node.leftNode,
		# 					operator=node.operator,
		# 					rightNode=node.rightNode.rightNode
		# 				)
		# 			)
		# 		)
		# 	if operator.name == tokenTypes.GT.name: # > (greater than)
		# 		return self.run(node.leftNode) > self.run(node.rightNode)

		# 	if operator.name == tokenTypes.LT.name: # < (less than)
		# 		return self.run(node.leftNode) < self.run(node.rightNode)

		# 	if operator.name == tokenTypes.LESS_OR_EQUALS.name: # <= (less or equals)
		# 		return self.run(node.leftNode) <= self.run(node.rightNode)

		# 	if operator.name == tokenTypes.GREATER_OR_EQUALS.name: # >= (greater or equals)
		# 		return self.run(node.leftNode) >= self.run(node.rightNode)

		# 	if operator.name == tokenTypes.EQUALS.name: # == (equals)
		# 		return self.run(node.leftNode) == self.run(node.rightNode)

		# if isinstance(node, BinOperationNode): # Когда мы видим бинарную операцию.
		# 	operator = node.operator.type
		# 	if operator.name == tokenTypes.MINUS.name:
		# 		return self.run(node.leftNode) - self.run(node.rightNode)
		# 	elif operator.name == tokenTypes.PLUS.name:
		# 		return self.run(node.leftNode) + self.run(node.rightNode)
		# 	elif operator.name == tokenTypes.MUL.name:
		# 		return self.run(node.leftNode) * self.run(node.rightNode)

		# if isinstance(node, ClassNode):
		# 	self.fields['global'][node.name] = dict(__call__=node)
		# 	self.scope[node.name] = node
		# 	pars = Parser(list())
		# 	node.locals = pars.scope
		# 	for i in node.body:
		# 		if isinstance(i, FunctionNode):
		# 			self.fields['global'][node.name][i.name] = i
		# 			node.locals[i.name] = i
		# 		if isinstance(i, ClassNode):
		# 			node.locals[i.name] = pars.run(i)
		# 		if isinstance(i, AssignNode):
		# 			self.fields['global'][node.name][i.targets[0].id] = self.run(i.value)
		# 			pars.run(i)
		# 	return node

		# if isinstance(node, FunctionNode):
		# 	self.scope[node.name] = node

		# if isinstance(node, AssignNode): # Когда мы видим операцию присваивания.
		# 	value = self.run(node.value)
		# 	for i in node.targets:
		# 		if isinstance(i, AttributeNode): # Когда мы видим, что обьект является аттрибутом.
		# 			attr_path = list()
		# 			while True:
		# 				if isinstance(i, AttributeNode):
		# 					attr_path.append(i.attr)
		# 					i=i.value
		# 				else:
		# 					obj = self.scope[i.id]
		# 					break

		# 			l = obj.locals
		# 			for i in attr_path[::-1]:
		# 				if isinstance(l[i], ClassNode):
		# 					l=l[i].locals
		# 				else:
		# 					l[i]=value
					
		# 		if isinstance(i, NameNode):
		# 			if self.fields['global'].get(i.id) is not None:
		# 				self.fields['global'][i.id] = value
		# 			else:
		# 				self.fields[self.scope_t][i.id] = value
		# 			self.scope[i.id] = value

		# if isinstance(node, AttributeNode):
		# 	attr_path = list()
		# 	while True:
		# 		if isinstance(node, AttributeNode):
		# 			attr_path.append(node.attr)
		# 			node=node.value
		# 		else:
		# 			obj = self.scope[node.id]
		# 			break
		# 	l = obj.locals

		# 	for i in attr_path[::-1]:
		# 		if isinstance(l[i], ClassNode):
		# 			l=l[i].locals
		# 		else:
		# 			return l[i]

		# if isinstance(node, ExprNode):
		# 	return self.run(node.value)

		# if isinstance(node, IfStatementsNode):
		# 	if self.run(node.test):
		# 		for i in node.body:
		# 			self.run(i)
		# 	else:
		# 		for i in node.orelse:
		# 			self.run(i)

		# if isinstance(node, CallNode):
		# 	func = self.run(node.func)
		# 	if isinstance(func, ClassNode):
		# 		pars = Parser(list())
		# 		for i in func.body:
		# 			pars.run(i)
		# 		func.locals = pars.scope
		# 		return ClassNode(func.name, body=deepcopy(func.body), locals=deepcopy(func.locals))
		# 	pars = Parser(list())
		# 	for func_arg, call_arg in zip(func.args, node.args):
		# 		pars.scope[func_arg.value.value] = self.run(call_arg.value)
			
		# 	for i in func.body:
		# 		if isinstance(i, ReturnNode):
		# 			return pars.run(i.value)
		# 		pars.run(i)

		# if isinstance(node, NameNode):
		# 	global_value = self.fields['global'].get(node.id)
		# 	local_value = self.fields[self.scope_t].get(node.id)
		# 	if global_value is not None:
		# 		return global_value
		# 	elif local_value is not None:
		# 		return local_value
		# 	else:
		# 		return self.scope[node.id]