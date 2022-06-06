from .expressionNode import ExpressionNode

class NameNode(ExpressionNode):
	def __init__(self, id, ctx):
		self.id = id
		self.ctx = ctx
		self.symbol = None