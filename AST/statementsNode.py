from .expressionNode import ExpressionNode

class StatementsNode(ExpressionNode):
	def __init__(self):
		self.codeStrings = list()

	def addNode(self, node: ExpressionNode):
		self.codeStrings.append(node)