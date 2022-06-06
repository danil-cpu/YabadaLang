from AST import *

from token import Token
from lexer import Lexer
from type import TokenType, tokenTypes
from typing import Union

class BuiltinFunction(object):
	def __init__(self, node):
		self.function = node.function
		self.params = node.params
	def __str__(self) -> str:
		return f'Function<{self.function.value}>(params={[i.var_node.value for i in self.params]})'
	def __repr__(self) -> str:
		return self.__str__()

class Parser(object):
	def __init__(self, tokens):
		self.tokens = tokens
		self.pos = 0
		self.scope = dict()

	def find(self, types, token) -> bool:
		for i in types:
			if i.name == token.type.name:
				return True
		return False

	def match(self, *types) -> Union[Token, None]:
		if self.pos < len(self.tokens):
			currentToken = self.tokens[self.pos]
			if self.find(types, currentToken):
				self.pos += 1
				return currentToken
		return None

	def require(self, *types) -> Token:
		token = self.match(*types)
		if token is None:
			raise Exception(f'На позиции {self.pos+1} ожидается -> {types[0].name}')
		return token

	def parseVariable(self) -> ExpressionNode:
		variable = self.match(tokenTypes.ID)
		if variable is not None:
			return VariableNode(variable)

	def parseVariableOrString(self) -> ExpressionNode:
		string = self.match(tokenTypes.STRING_CONST)
		if string is not None:
			return StringNode(string)
		variable = self.match(tokenTypes.ID)
		if variable is not None:
			return VariableNode(variable)

	def parseVariableOrInteger(self) -> ExpressionNode:
		integer = self.match(tokenTypes.INTEGER_CONST)
		if integer is not None:
			return IntegerNode(integer)
		variable = self.match(tokenTypes.ID)
		if variable is not None:
			return VariableNode(variable)

	def parseVariableOrIntegerOrString(self) -> ExpressionNode:
		integer = self.match(tokenTypes.INTEGER_CONST)
		if integer is not None:
			return IntegerNode(integer)
		string = self.match(tokenTypes.STRING_CONST)
		if string is not None:
			return StringNode(string)
		variable = self.match(tokenTypes.ID)
		if variable is not None:
			return VariableNode(variable)

	def parseVariableOrIntegerOrStringOrFunction(self)  -> ExpressionNode:
		integer = self.match(tokenTypes.INTEGER_CONST)
		if integer is not None:
			return IntegerNode(integer)
		string = self.match(tokenTypes.STRING_CONST)
		if string is not None:
			return StringNode(string)
		variable = self.match(tokenTypes.ID)
		if variable is not None:
			if self.match(tokenTypes.LPAR) is not None:
				return self.callFunction()
			return VariableNode(variable)


	def parseParantheses(self) -> ExpressionNode:
		if self.match(tokenTypes.LPAR) is not None:
			node = self.parseFormula()
			self.require(tokenTypes.RPAR)
			return node
		else:
			return self.parseVariableOrIntegerOrStringOrFunction()

	def parseFormula(self) -> ExpressionNode:
		leftNode = self.parseParantheses()
		
		operator = self.match(tokenTypes.PLUS, tokenTypes.MINUS, tokenTypes.MUL, tokenTypes.DIV_FLOAT)
		while (operator != None):
			rightNode = self.parseParantheses()
			leftNode = BinOperationNode(operator, leftNode, rightNode)
			operator = self.match(tokenTypes.PLUS, tokenTypes.MINUS, tokenTypes.MUL, tokenTypes.DIV_FLOAT)
		return leftNode

	def parsePrint(self) -> ExpressionNode:
		operatorPrint = self.match(tokenTypes.PRINT)
		if operatorPrint is not None:
			return UnarOperationNode(operatorPrint, self.parseFormula())

	def parseReturn(self) -> ExpressionNode:
		operatorReturn = self.match(tokenTypes.RETURN)
		if operatorReturn is not None:
			return UnarOperationNode(operatorReturn, self.parseFormula())

	def parseParamsFunction(self) -> Token:
		params = []
		type = self.match(tokenTypes.String, tokenTypes.Integer)
		token = self.parseFormula(paran=False)

		while token is not None:
			params.append(token)
			if self.match(tokenTypes.COMMA) is not None:
				type = self.match(tokenTypes.String, tokenTypes.Integer)
				token = self.parseFormula(paran=False)
			else:
				break
		return params

	def parseBlock(self) -> ExpressionNode:
		self.require(tokenTypes.LFPAR)
		tokensCode = list()
		while self.match(tokenTypes.RFPAR) is None:
			tokensCode.append(self.tokens[self.pos])
			self.pos += 1
		return tokensCode



	def parseFunction(self) -> ExpressionNode:
		id_func = self.require(tokenTypes.ID)
		if self.require(tokenTypes.LPAR) is not None:
			params = self.parseParamsFunction()

			self.require(tokenTypes.RPAR)
			code = self.parseBlock()
			
			return FunctionNode(id_func, params, code)

	def callFunction(self) -> ExpressionNode:
		function = self.tokens[self.pos-2]
		actual_params = self.parseParamsFunction()
		self.require(tokenTypes.RPAR)
		return FunctionCallNode(function, actual_params)
		

	def parseExpression(self) -> ExpressionNode:
		"""
			FUNCTION ID(PARAMS){
				...
			}
			ID() -> call function or error if variable
			ID -> return Variable or builtin type
			print: (ID|type) -> none
		"""







		if self.match(tokenTypes.ID) is None:
			if self.match(tokenTypes.FUNCTION) is not None:
				return self.parseFunction()
			elif self.find([tokenTypes.PRINT], self.tokens[self.pos]) is not None:
				return self.parsePrint()
			elif self.find([tokenTypes.RETURN], self.tokens[self.pos]) is not None:
				return self.parseReturn()

		if self.match(tokenTypes.LPAR) is not None:
			return self.callFunction()
		self.pos -= 1
		variableNode = self.parseVariableOrIntegerOrStringOrFunction()
		assignOperator = self.match(tokenTypes.ASSIGN)
		if assignOperator is not None:
			rightFormulaNode = self.parseFormula()
			binaryNode = BinOperationNode(assignOperator, variableNode, rightFormulaNode)
			return binaryNode


		raise ValueError('Ожидалась строка или переменная')


	def parseCode(self) -> ExpressionNode:
		root = StatementsNode()
		while self.pos < len(self.tokens):
			codeStringNode = self.parseExpression()
			self.require(tokenTypes.SEMICOLON)
			root.addNode(codeStringNode)
		return root

	def run(self, node: ExpressionNode):
		pass

















		# if isinstance(node, IntegerNode):
		# 	return int(node.integer.value)
		# if isinstance(node, StringNode):
		# 	return str(node.string.value).replace("'",'')
		# if isinstance(node, FunctionNode):
		# 	self.scope[node.function.value] = node
		# if isinstance(node, FunctionCallNode):
		# 	scope = self.scope[node.function.value]
		# 	parser = Parser(scope.code)
		# 	rootNode = parser.parseCode()
		# 	rootNode.codeStrings.extend(node.actual_params)
		# 	try:
		# 		self.run(rootNode)
		# 	except RecursionError:
		# 		print(f'File __main__.code in Function<{node.function.value}>\n\tRecursionError: maximum recursion depth exceeded in comparison')
		# 		exit()
			
		# 	# print(Parser(scope.code.copy()).tokens)
		# 	return str(scope)


		# if isinstance(node, UnarOperationNode):
		# 	name = node.operator.type.name
		# 	if name == tokenTypes.PRINT.name:
		# 		print(self.run(node.operand))
		# 		return;

		# if isinstance(node, BinOperationNode):
		# 	name = node.operator.type.name
		# 	if name == tokenTypes.PLUS.name:
		# 		return self.run(node.leftNode) + self.run(node.rightNode)
		# 	if name == tokenTypes.MINUS.name:
		# 		return self.run(node.leftNode) - self.run(node.rightNode)
		# 	if name == tokenTypes.MUL.name:
		# 		return self.run(node.leftNode) * self.run(node.rightNode)
		# 	if name == tokenTypes.ASSIGN.name:
		# 		result = self.run(node.rightNode)

		# 		variableNode = VariableNode(node.leftNode.variable)
		# 		self.scope[variableNode.variable.value] = result
		# 		return result

		# if isinstance(node, VariableNode):
		# 	if node.variable.value in self.scope:
		# 		return self.scope[node.variable.value]
		# 	raise ValueError("переменная не обнаружена")

		# if isinstance(node, StatementsNode):
		# 	for i in node.codeStrings:
		# 		self.run(i)
		# 	return


class Parser(object):
	def __init__(self, tokens):
		self.tokens = tokens

		self.pos = 0

