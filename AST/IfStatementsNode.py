from .expressionNode import ExpressionNode

class IfStatementsNode(ExpressionNode):
	def __init__(self, test, orelse, body):
		self.test = test
		self.orelse = orelse
		self.body = body