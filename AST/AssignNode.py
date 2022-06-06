from .expressionNode import ExpressionNode

class AssignNode(ExpressionNode):
	def __init__(self, targets, value):
		self.targets = targets
		self.value = value