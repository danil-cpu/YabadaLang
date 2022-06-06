import argparse
import time

from lexer import Lexer
from parser_new import Parser
from semantic_analyzer import SemanticAnalyzer

arg = argparse.ArgumentParser(
	description='YabadaScript - Interpreter'
)
arg.add_argument('inputfile', nargs='?', help=r'YabadaScript source <path\file>.ya')
# arg.add_argument('inputfile', help=r'YabadaScript source <path\file>.ya')
arg.add_argument(
	'--v',
	help='Print version from language Yabada'
)
arg.add_argument(
	'--scope',
	help='Print scope information',
	action='store_true'
)
args = arg.parse_args()

def run(filename):
	__code__ = open(args.inputfile, 'r').read()
	start = time.time()
	lexer = Lexer(__code__)
	lexer.lexAnalysis()
	parser = Parser(lexer.tokenList)
	rootNode = parser.parseCode()
	parser.run(rootNode)
	print(f'[Finished in {round(time.time()-start, 8)} sec]')
	input('Press enter to continue..')


__code__ = """
x = 8;
"""
if args.inputfile is not None:
	run(args.inputfile)
else:
	start = time.time()
	lexer = Lexer(__code__)
	lexer.lexAnalysis()
	parser = Parser(lexer.tokenList)
	rootNode = parser.parseCode()
	parser.run(rootNode)
	print(f'[Finished in {round(time.time()-start, 4)} sec]')
	input('Press enter to continue..')
# print(parser.scope)