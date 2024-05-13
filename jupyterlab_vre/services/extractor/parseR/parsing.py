from antlr4 import *
from .RParser import RParser
from .RFilter import RFilter
from .RLexer import RLexer

def parse_text(text):
    input_stream = InputStream(text)
    lexer = RLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    tokens.fill()

    r_filter = RFilter(tokens)
    r_filter.stream()
    tokens.reset()

    parser = RParser(tokens)
    tree = parser.prog()

    return tree
