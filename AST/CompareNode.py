from .expressionNode import ExpressionNode

class CompareNode(ExpressionNode):
	def __init__(self, leftNode, operator, rightNode):
		self.leftNode = leftNode
		self.operator = operator
		self.rightNode = rightNode

	def __str__(self) -> str:
		return f'Compare(left={self.leftNode}, operator={self.operator}, right={self.rightNode})'
	def __repr__(self) -> str:
		return self.__str__()