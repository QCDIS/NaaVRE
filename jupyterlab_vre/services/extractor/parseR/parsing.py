import sys
from antlr4 import *
from .RParser import RParser
from .RFilter import RFilter
from .RLexer import RLexer

def parse_text(text):
    # first arg is the file name
    
    # input_stream = FileStream("./test.r", encoding='utf-8')
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
