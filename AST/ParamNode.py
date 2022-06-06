from .expressionNode import ExpressionNode

class ParamNode(ExpressionNode):
	def __init__(self, value):
		self.value = value
