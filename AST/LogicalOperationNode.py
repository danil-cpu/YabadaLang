from .expressionNode import ExpressionNode

class LogicalOperationNode(ExpressionNode):
	def __init__(self, leftNode, operator, rightNode):
		self.leftNode = leftNode
		self.operator = operator
		self.rightNode = rightNode