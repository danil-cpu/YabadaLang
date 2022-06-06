from .expressionNode import ExpressionNode

class ClassNode(ExpressionNode):
	def __init__(self, name, body):
		self.name = name
		self.body = body
		symbol = None