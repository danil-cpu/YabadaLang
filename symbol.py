class AttrDict(dict):
	def __getattr__(self, name):
		if name in self:
			return self[name]
		raise AttributeError(name)

class Symbol(AttrDict):
	def __init__(self, name, type=None):
		super().__init__({'toString': self.toString})
		self.scope_level = 0
		self['__value__'] = None
		self['__name__'] = name
		self['__type__'] = type

	def __repr__(self) -> str:
		return f"<Object '{self.__name__}' is {self.__type__}>"

	def toString(self) -> str:
		return str(self.__value__)

	def toRepr(self) -> str:
		return self.__repr__
 
	def __dir__(self) -> list:
		return self.keys()

	def __str__(self) -> str:
		return f'<{self.__class__.__name__}(name={self.__name__}, type={self.__type__})>'

	__repr__ = __str__


class ClassSymbol(Symbol):
	def __init__(self, name):
		super().__init__(name, type='Class')
		self['body'] = None
		
class FunctionSymbol(Symbol):
	def __init__(self, name, args=None):
		super().__init__(name)
		self.args = [] if args is None else args
		self.body = None

	def __str__(self) -> str:
		return f'<{self.__class__.__name__}(name={self.__name__}, parameters={self.args})>'

class NameSymbol(Symbol):
	def __init__(self, name, value=None):
		super().__init__(name, type='Name')
		self['__value__'] = value

	def __str__(self) -> str:
		return f'<{self.__class__.__name__}(name={self.__name__})>'

	__repr__ = __str__

class BuiltinTypeSymbol(Symbol):
	def __init__(self, name):
		super().__init__(name)

	def __str__(self) -> str:
		return self.__name__

	def __repr__(self):
		return f'<{self.__class__.__name__}(name={self.__name__})>'

class SymbolTable(dict):
	def __init__(self, scope_name, scope_level, enclosing_scope=None):
		self.scope_name = scope_name
		self.scope_level = scope_level
		self.enclosing_scope = enclosing_scope

	def _init_builtins(self):
		self.insert(BuiltinTypeSymbol('INTEGER'))

	def __str__(self) -> str:
		h1 = 'SCOPE (SCOPED SYMBOL TABLE)'
		lines = ['\n', h1, '=' * len(h1)]
		for header_name, header_value in (
			('Scope name', self.scope_name),
			('Scope level', self.scope_level),
			('Enclosing scope', self.enclosing_scope.scope_name if self.enclosing_scope else None)
		):
			lines.append(f'{header_name:<15}: {header_value}')
		h2 = 'Scope (Scoped symbol table) contents'
		lines.extend([h2, '-' * len(h2)])
		lines.extend(f'{key:>7}: {value}' for key, value in self.items())
		s = '\n'.join(lines)
		return s

	__repr__ = __str__

	def __dir__(self):
		return self.keys()

	def insert(self, symbol: Symbol) -> None:
		self[symbol.__name__] = symbol

	def lookup(self, name: str, current_scope_only=False) -> Symbol:
		symbol = self.get(name)

		if symbol is not None:
			return symbol

		if current_scope_only:
			return None

		if self.enclosing_scope is not None:
			return self.enclosing_scope.lookup(name)

# table = SymbolTable()

# table.insert(ClassSymbol('TestClass', [NameSymbol('x', 'Integer')]))
# table.insert(NameSymbol('b', 'Integer'))

# print(table)
# print(dir(table['TestClass'].x))