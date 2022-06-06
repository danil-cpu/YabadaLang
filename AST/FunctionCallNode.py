from .expressionNode import ExpressionNode

class FunctionCallNode(ExpressionNode):
	def __init__(self, function, params):
		self.function = function
		self.actual_params = params
