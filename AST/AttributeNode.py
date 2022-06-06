from .expressionNode import ExpressionNode

class AttributeNode(ExpressionNode):
	def __init__(self, value, attr):
		self.value = value
		self.attr = attr
	def __repr__(self):
		return f'{self.__class__.__name__}({self.value=}, {self.attr=})'