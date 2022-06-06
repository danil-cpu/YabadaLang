class TokenType(object):
	def __init__(self, name, regex):
		self.name = name
		self.regex = regex

	def __str__(self) -> str:
		return f'TokenType.{self.name}'

	def __repr__(self) -> str:
		return self.__str__()

class AttributeDict(dict):
	def __getattr__(self, name):
		if name in self:
			return self[name]
		raise AttributeError(name)

tokenTypes = AttributeDict({
	'Integer': TokenType('Integer', 'Integer'),
	'String': TokenType('String', 'String'),
	'Boolean': TokenType('Boolean', 'Boolean'),

	
	'SEMICOLON': TokenType('SEMICOLON', ';'),
	'COLON': TokenType('COLON', ':'),
	'COMMA': TokenType('COMMA', ','),
	'DOT': TokenType('DOT', r'\.'),
	'SPACE': TokenType('SPACE', r'[ \n\t\r]'),

	'INTEGER_CONST': TokenType('INTEGER_CONST', r'\d+'),
	'STRING_CONST': TokenType('STRING_CONST', r"\'[^\'\']+\'"),
	'BOOLEAN_CONST': TokenType('BOOLEAN_CONST', 'True|False'),

	'CLASS': TokenType('CLASS', 'class'),
	'COMMENT': TokenType('COMMENT', r'#.*[\w\s]*#'),
	'FUNCTION': TokenType('FUNCTION', 'func'),
	'RETURN': TokenType('RETURN', 'return:'),

	'IF': TokenType('IF', 'if'),
	'ELSE': TokenType('ELSE', 'else'),

	'OR': TokenType('OR', 'or'),
	'AND': TokenType('AND', 'and'),
	'LESS_OR_EQUALS': TokenType('LESS_OR_EQUALS', '<='),
	'GREATER_OR_EQUALS': TokenType('GREATER_OR_EQUALS', '>='),
	'EQUALS': TokenType('EQUALS', '=='),
	'GT': TokenType('GT', '>'),
	'LT': TokenType('LT', '<'),
	'ASSIGN': TokenType('ASSIGN', '='),

	'PLUS': TokenType('PLUS', r'\+'),
	'MINUS': TokenType('MINUS', r'\-'),
	'MUL': TokenType('MUL', r'\*'),
	'DIV_FLOAT': TokenType('DIV', r'/'),

	'LPAR': TokenType('LPAR', r'\('),
	'RPAR': TokenType('RPAR', r'\)'),
	'LFPAR': TokenType('LFPAR', r'{'),
	'RFPAR': TokenType('RFPAR', r'}'),
	'PRINT': TokenType('PRINT', 'print:'),
	'ID': TokenType('ID', r'\w*')
})

# '': TokenType(),