from .expressionNode import ExpressionNode

class CallNode(ExpressionNode):
	def __init__(self, func, args):
		self.func = func
		self.args = args