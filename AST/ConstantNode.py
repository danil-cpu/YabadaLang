from .expressionNode import ExpressionNode

class ConstantNode(ExpressionNode):
	def __init__(self, value):
		self.value = value

	def __str__(self) -> str:
		return f'Constant(value={self.value})'
		
	def __repr__(self) -> str:
		return self.__str__()