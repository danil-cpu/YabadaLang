from .expressionNode import ExpressionNode

class ReturnNode(ExpressionNode):
	def __init__(self, value):
		self.value = value