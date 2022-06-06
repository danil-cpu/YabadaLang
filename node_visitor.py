class NodeVisitor:
	def visit(self, node):
		method = f'visit_{type(node).__name__}'
		visitor = getattr(self, method, self.generic_visit)
		return visitor(node)

	def generic_visit(self, node):
		raise Exception('No visit_{} method'.format(type(node).__name__))