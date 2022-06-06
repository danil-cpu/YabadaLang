from .expressionNode import ExpressionNode

class FunctionNode(ExpressionNode):
	def __init__(self, name, args, body):
		self.name = name
		self.args = args
		self.body = body
		symbol = None