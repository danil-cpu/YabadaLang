class Token(object):
	def __init__(self, type, value, pos=None):
		self.type = type
		self.value = value
		self.pos = pos

	def __str__(self) -> str:
		return 'Token({type}, {value}, position={pos})'.format(
			type=self.type,
			value=self.value,
			pos=self.pos
		)

	def __repr__(self):
		return self.__str__()