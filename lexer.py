from typing import List, Union
from token_ya import Token
from type import TokenType, tokenTypes

import re

class Lexer(object):
	def __init__(self, code: str):
		self.code = code

		self.pos = 0

		self.tokenList = list()

	def lexAnalysis(self) -> List[Token]:
		while self.nextToken():
			pass
		self.tokenList = list(filter(lambda v: v.type.name != tokenTypes.SPACE.name and v.type.name != tokenTypes.COMMENT.name, self.tokenList))
		return self.tokenList
			

	def nextToken(self) -> bool:
		if self.pos >= len(self.code):
			return False
		for type, tokenType in tokenTypes.items():
			result = re.match(f'^{tokenType.regex}', self.code[self.pos:])
			
			if result and result[0]: # Проверяем валидность кода

				token = Token(
					type=tokenType,
					value=result[0],
					pos=self.pos
				)

				self.tokenList.append(token)
				self.pos += len(result[0])
				return True
		raise ValueError(f'Token is invalid')
