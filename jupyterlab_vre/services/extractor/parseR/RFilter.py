# Generated from RFilter.g4 by ANTLR 4.13.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,64,147,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,1,0,1,0,1,0,5,
        0,14,8,0,10,0,12,0,17,9,0,1,0,1,0,1,1,1,1,4,1,23,8,1,11,1,12,1,24,
        1,2,1,2,3,2,29,8,2,1,2,1,2,1,2,3,2,34,8,2,1,2,1,2,1,2,1,2,5,2,40,
        8,2,10,2,12,2,43,9,2,1,2,1,2,1,2,1,2,1,2,5,2,50,8,2,10,2,12,2,53,
        9,2,1,2,1,2,1,2,1,2,5,2,59,8,2,10,2,12,2,62,9,2,1,2,1,2,1,2,1,2,
        5,2,68,8,2,10,2,12,2,71,9,2,1,2,1,2,1,2,1,2,3,2,77,8,2,1,2,1,2,1,
        2,5,2,82,8,2,10,2,12,2,85,9,2,1,2,1,2,3,2,89,8,2,1,2,1,2,3,2,93,
        8,2,1,2,1,2,1,2,5,2,98,8,2,10,2,12,2,101,9,2,1,2,1,2,3,2,105,8,2,
        1,2,1,2,3,2,109,8,2,1,2,1,2,1,2,5,2,114,8,2,10,2,12,2,117,9,2,1,
        2,1,2,3,2,121,8,2,1,2,1,2,3,2,125,8,2,1,2,1,2,1,2,5,2,130,8,2,10,
        2,12,2,133,9,2,1,2,1,2,3,2,137,8,2,1,2,1,2,3,2,141,8,2,1,3,1,3,1,
        4,1,4,1,4,0,0,5,0,2,4,6,8,0,2,2,0,45,52,56,61,6,0,5,27,29,30,41,
        41,43,44,53,54,62,62,182,0,15,1,0,0,0,2,22,1,0,0,0,4,140,1,0,0,0,
        6,142,1,0,0,0,8,144,1,0,0,0,10,14,3,4,2,0,11,14,5,63,0,0,12,14,5,
        1,0,0,13,10,1,0,0,0,13,11,1,0,0,0,13,12,1,0,0,0,14,17,1,0,0,0,15,
        13,1,0,0,0,15,16,1,0,0,0,16,18,1,0,0,0,17,15,1,0,0,0,18,19,5,0,0,
        1,19,1,1,0,0,0,20,21,5,63,0,0,21,23,6,1,-1,0,22,20,1,0,0,0,23,24,
        1,0,0,0,24,22,1,0,0,0,24,25,1,0,0,0,25,3,1,0,0,0,26,28,3,8,4,0,27,
        29,3,2,1,0,28,27,1,0,0,0,28,29,1,0,0,0,29,141,1,0,0,0,30,141,3,6,
        3,0,31,33,5,36,0,0,32,34,3,2,1,0,33,32,1,0,0,0,33,34,1,0,0,0,34,
        35,1,0,0,0,35,41,6,2,-1,0,36,40,3,4,2,0,37,40,5,63,0,0,38,40,5,1,
        0,0,39,36,1,0,0,0,39,37,1,0,0,0,39,38,1,0,0,0,40,43,1,0,0,0,41,39,
        1,0,0,0,41,42,1,0,0,0,42,44,1,0,0,0,43,41,1,0,0,0,44,45,6,2,-1,0,
        45,141,5,37,0,0,46,51,5,34,0,0,47,50,3,4,2,0,48,50,3,2,1,0,49,47,
        1,0,0,0,49,48,1,0,0,0,50,53,1,0,0,0,51,49,1,0,0,0,51,52,1,0,0,0,
        52,54,1,0,0,0,53,51,1,0,0,0,54,141,5,35,0,0,55,60,5,4,0,0,56,59,
        3,4,2,0,57,59,3,2,1,0,58,56,1,0,0,0,58,57,1,0,0,0,59,62,1,0,0,0,
        60,58,1,0,0,0,60,61,1,0,0,0,61,63,1,0,0,0,62,60,1,0,0,0,63,141,5,
        3,0,0,64,69,5,2,0,0,65,68,3,4,2,0,66,68,3,2,1,0,67,65,1,0,0,0,67,
        66,1,0,0,0,68,71,1,0,0,0,69,67,1,0,0,0,69,70,1,0,0,0,70,72,1,0,0,
        0,71,69,1,0,0,0,72,73,5,3,0,0,73,141,5,3,0,0,74,76,5,33,0,0,75,77,
        3,2,1,0,76,75,1,0,0,0,76,77,1,0,0,0,77,78,1,0,0,0,78,83,5,34,0,0,
        79,82,3,4,2,0,80,82,3,2,1,0,81,79,1,0,0,0,81,80,1,0,0,0,82,85,1,
        0,0,0,83,81,1,0,0,0,83,84,1,0,0,0,84,86,1,0,0,0,85,83,1,0,0,0,86,
        88,5,35,0,0,87,89,3,2,1,0,88,87,1,0,0,0,88,89,1,0,0,0,89,141,1,0,
        0,0,90,92,5,40,0,0,91,93,3,2,1,0,92,91,1,0,0,0,92,93,1,0,0,0,93,
        94,1,0,0,0,94,99,5,34,0,0,95,98,3,4,2,0,96,98,3,2,1,0,97,95,1,0,
        0,0,97,96,1,0,0,0,98,101,1,0,0,0,99,97,1,0,0,0,99,100,1,0,0,0,100,
        102,1,0,0,0,101,99,1,0,0,0,102,104,5,35,0,0,103,105,3,2,1,0,104,
        103,1,0,0,0,104,105,1,0,0,0,105,141,1,0,0,0,106,108,5,42,0,0,107,
        109,3,2,1,0,108,107,1,0,0,0,108,109,1,0,0,0,109,110,1,0,0,0,110,
        115,5,34,0,0,111,114,3,4,2,0,112,114,3,2,1,0,113,111,1,0,0,0,113,
        112,1,0,0,0,114,117,1,0,0,0,115,113,1,0,0,0,115,116,1,0,0,0,116,
        118,1,0,0,0,117,115,1,0,0,0,118,120,5,35,0,0,119,121,3,2,1,0,120,
        119,1,0,0,0,120,121,1,0,0,0,121,141,1,0,0,0,122,124,5,38,0,0,123,
        125,3,2,1,0,124,123,1,0,0,0,124,125,1,0,0,0,125,126,1,0,0,0,126,
        131,5,34,0,0,127,130,3,4,2,0,128,130,3,2,1,0,129,127,1,0,0,0,129,
        128,1,0,0,0,130,133,1,0,0,0,131,129,1,0,0,0,131,132,1,0,0,0,132,
        134,1,0,0,0,133,131,1,0,0,0,134,136,5,35,0,0,135,137,3,2,1,0,136,
        135,1,0,0,0,136,137,1,0,0,0,137,141,1,0,0,0,138,139,5,39,0,0,139,
        141,6,2,-1,0,140,26,1,0,0,0,140,30,1,0,0,0,140,31,1,0,0,0,140,46,
        1,0,0,0,140,55,1,0,0,0,140,64,1,0,0,0,140,74,1,0,0,0,140,90,1,0,
        0,0,140,106,1,0,0,0,140,122,1,0,0,0,140,138,1,0,0,0,141,5,1,0,0,
        0,142,143,7,0,0,0,143,7,1,0,0,0,144,145,7,1,0,0,145,9,1,0,0,0,30,
        13,15,24,28,33,39,41,49,51,58,60,67,69,76,81,83,88,92,97,99,104,
        108,113,115,120,124,129,131,136,140
    ]

class RFilter ( Parser ):

    grammarFileName = "RFilter.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "';'", "'[['", "']'", "'['", "'::'", "':::'", 
                     "'$'", "'@'", "'^'", "'-'", "'+'", "':'", "'*'", "'/'", 
                     "'>'", "'>='", "'<'", "'<='", "'=='", "'!='", "'!'", 
                     "'&'", "'&&'", "'|'", "'||'", "'~'", "'<-'", "'<<-'", 
                     "'='", "'->'", "'->>'", "':='", "'function'", "'('", 
                     "')'", "'{'", "'}'", "'if'", "'else'", "'for'", "'in'", 
                     "'while'", "'repeat'", "'?'", "'next'", "'break'", 
                     "'NULL'", "'NA'", "'Inf'", "'NaN'", "'TRUE'", "'FALSE'", 
                     "','", "'...'", "'.'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "HEX", "INT", "FLOAT", "COMPLEX", "STRING", "ID", 
                      "USER_OP", "NL", "WS" ]

    RULE_stream = 0
    RULE_eat = 1
    RULE_elem = 2
    RULE_atom = 3
    RULE_op = 4

    ruleNames =  [ "stream", "eat", "elem", "atom", "op" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    T__13=14
    T__14=15
    T__15=16
    T__16=17
    T__17=18
    T__18=19
    T__19=20
    T__20=21
    T__21=22
    T__22=23
    T__23=24
    T__24=25
    T__25=26
    T__26=27
    T__27=28
    T__28=29
    T__29=30
    T__30=31
    T__31=32
    T__32=33
    T__33=34
    T__34=35
    T__35=36
    T__36=37
    T__37=38
    T__38=39
    T__39=40
    T__40=41
    T__41=42
    T__42=43
    T__43=44
    T__44=45
    T__45=46
    T__46=47
    T__47=48
    T__48=49
    T__49=50
    T__50=51
    T__51=52
    T__52=53
    T__53=54
    T__54=55
    HEX=56
    INT=57
    FLOAT=58
    COMPLEX=59
    STRING=60
    ID=61
    USER_OP=62
    NL=63
    WS=64

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None



        self.curlies = 0



    class StreamContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(RFilter.EOF, 0)

        def elem(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RFilter.ElemContext)
            else:
                return self.getTypedRuleContext(RFilter.ElemContext,i)


        def NL(self, i:int=None):
            if i is None:
                return self.getTokens(RFilter.NL)
            else:
                return self.getToken(RFilter.NL, i)

        def getRuleIndex(self):
            return RFilter.RULE_stream

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStream" ):
                listener.enterStream(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStream" ):
                listener.exitStream(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStream" ):
                return visitor.visitStream(self)
            else:
                return visitor.visitChildren(self)




    def stream(self):

        localctx = RFilter.StreamContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_stream)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 15
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & -36028975528542218) != 0):
                self.state = 13
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30, 33, 34, 36, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 56, 57, 58, 59, 60, 61, 62]:
                    self.state = 10
                    self.elem()
                    pass
                elif token in [63]:
                    self.state = 11
                    self.match(RFilter.NL)
                    pass
                elif token in [1]:
                    self.state = 12
                    self.match(RFilter.T__0)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 17
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 18
            self.match(RFilter.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EatContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self._NL = None # Token

        def NL(self, i:int=None):
            if i is None:
                return self.getTokens(RFilter.NL)
            else:
                return self.getToken(RFilter.NL, i)

        def getRuleIndex(self):
            return RFilter.RULE_eat

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEat" ):
                listener.enterEat(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEat" ):
                listener.exitEat(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEat" ):
                return visitor.visitEat(self)
            else:
                return visitor.visitChildren(self)




    def eat(self):

        localctx = RFilter.EatContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_eat)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 22 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 20
                    localctx._NL = self.match(RFilter.NL)
                    localctx._NL.channel = Token.HIDDEN_CHANNEL

                else:
                    raise NoViableAltException(self)
                self.state = 24 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,2,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ElemContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def op(self):
            return self.getTypedRuleContext(RFilter.OpContext,0)


        def eat(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RFilter.EatContext)
            else:
                return self.getTypedRuleContext(RFilter.EatContext,i)


        def atom(self):
            return self.getTypedRuleContext(RFilter.AtomContext,0)


        def elem(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RFilter.ElemContext)
            else:
                return self.getTypedRuleContext(RFilter.ElemContext,i)


        def NL(self, i:int=None):
            if i is None:
                return self.getTokens(RFilter.NL)
            else:
                return self.getToken(RFilter.NL, i)

        def getRuleIndex(self):
            return RFilter.RULE_elem

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterElem" ):
                listener.enterElem(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitElem" ):
                listener.exitElem(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitElem" ):
                return visitor.visitElem(self)
            else:
                return visitor.visitChildren(self)




    def elem(self):

        localctx = RFilter.ElemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_elem)
        self._la = 0 # Token type
        try:
            self.state = 140
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30, 41, 43, 44, 53, 54, 62]:
                self.enterOuterAlt(localctx, 1)
                self.state = 26
                self.op()
                self.state = 28
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
                if la_ == 1:
                    self.state = 27
                    self.eat()


                pass
            elif token in [45, 46, 47, 48, 49, 50, 51, 52, 56, 57, 58, 59, 60, 61]:
                self.enterOuterAlt(localctx, 2)
                self.state = 30
                self.atom()
                pass
            elif token in [36]:
                self.enterOuterAlt(localctx, 3)
                self.state = 31
                self.match(RFilter.T__35)
                self.state = 33
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
                if la_ == 1:
                    self.state = 32
                    self.eat()


                self.curlies += 1
                self.state = 41
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while (((_la) & ~0x3f) == 0 and ((1 << _la) & -36028975528542218) != 0):
                    self.state = 39
                    self._errHandler.sync(self)
                    token = self._input.LA(1)
                    if token in [2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30, 33, 34, 36, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 56, 57, 58, 59, 60, 61, 62]:
                        self.state = 36
                        self.elem()
                        pass
                    elif token in [63]:
                        self.state = 37
                        self.match(RFilter.NL)
                        pass
                    elif token in [1]:
                        self.state = 38
                        self.match(RFilter.T__0)
                        pass
                    else:
                        raise NoViableAltException(self)

                    self.state = 43
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.curlies -= 1 
                self.state = 45
                self.match(RFilter.T__36)
                pass
            elif token in [34]:
                self.enterOuterAlt(localctx, 4)
                self.state = 46
                self.match(RFilter.T__33)
                self.state = 51
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while (((_la) & ~0x3f) == 0 and ((1 << _la) & -36028975528542220) != 0):
                    self.state = 49
                    self._errHandler.sync(self)
                    token = self._input.LA(1)
                    if token in [2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30, 33, 34, 36, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 56, 57, 58, 59, 60, 61, 62]:
                        self.state = 47
                        self.elem()
                        pass
                    elif token in [63]:
                        self.state = 48
                        self.eat()
                        pass
                    else:
                        raise NoViableAltException(self)

                    self.state = 53
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 54
                self.match(RFilter.T__34)
                pass
            elif token in [4]:
                self.enterOuterAlt(localctx, 5)
                self.state = 55
                self.match(RFilter.T__3)
                self.state = 60
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while (((_la) & ~0x3f) == 0 and ((1 << _la) & -36028975528542220) != 0):
                    self.state = 58
                    self._errHandler.sync(self)
                    token = self._input.LA(1)
                    if token in [2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30, 33, 34, 36, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 56, 57, 58, 59, 60, 61, 62]:
                        self.state = 56
                        self.elem()
                        pass
                    elif token in [63]:
                        self.state = 57
                        self.eat()
                        pass
                    else:
                        raise NoViableAltException(self)

                    self.state = 62
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 63
                self.match(RFilter.T__2)
                pass
            elif token in [2]:
                self.enterOuterAlt(localctx, 6)
                self.state = 64
                self.match(RFilter.T__1)
                self.state = 69
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while (((_la) & ~0x3f) == 0 and ((1 << _la) & -36028975528542220) != 0):
                    self.state = 67
                    self._errHandler.sync(self)
                    token = self._input.LA(1)
                    if token in [2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30, 33, 34, 36, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 56, 57, 58, 59, 60, 61, 62]:
                        self.state = 65
                        self.elem()
                        pass
                    elif token in [63]:
                        self.state = 66
                        self.eat()
                        pass
                    else:
                        raise NoViableAltException(self)

                    self.state = 71
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 72
                self.match(RFilter.T__2)
                self.state = 73
                self.match(RFilter.T__2)
                pass
            elif token in [33]:
                self.enterOuterAlt(localctx, 7)
                self.state = 74
                self.match(RFilter.T__32)
                self.state = 76
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==63:
                    self.state = 75
                    self.eat()


                self.state = 78
                self.match(RFilter.T__33)
                self.state = 83
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while (((_la) & ~0x3f) == 0 and ((1 << _la) & -36028975528542220) != 0):
                    self.state = 81
                    self._errHandler.sync(self)
                    token = self._input.LA(1)
                    if token in [2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30, 33, 34, 36, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 56, 57, 58, 59, 60, 61, 62]:
                        self.state = 79
                        self.elem()
                        pass
                    elif token in [63]:
                        self.state = 80
                        self.eat()
                        pass
                    else:
                        raise NoViableAltException(self)

                    self.state = 85
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 86
                self.match(RFilter.T__34)
                self.state = 88
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,16,self._ctx)
                if la_ == 1:
                    self.state = 87
                    self.eat()


                pass
            elif token in [40]:
                self.enterOuterAlt(localctx, 8)
                self.state = 90
                self.match(RFilter.T__39)
                self.state = 92
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==63:
                    self.state = 91
                    self.eat()


                self.state = 94
                self.match(RFilter.T__33)
                self.state = 99
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while (((_la) & ~0x3f) == 0 and ((1 << _la) & -36028975528542220) != 0):
                    self.state = 97
                    self._errHandler.sync(self)
                    token = self._input.LA(1)
                    if token in [2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30, 33, 34, 36, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 56, 57, 58, 59, 60, 61, 62]:
                        self.state = 95
                        self.elem()
                        pass
                    elif token in [63]:
                        self.state = 96
                        self.eat()
                        pass
                    else:
                        raise NoViableAltException(self)

                    self.state = 101
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 102
                self.match(RFilter.T__34)
                self.state = 104
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,20,self._ctx)
                if la_ == 1:
                    self.state = 103
                    self.eat()


                pass
            elif token in [42]:
                self.enterOuterAlt(localctx, 9)
                self.state = 106
                self.match(RFilter.T__41)
                self.state = 108
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==63:
                    self.state = 107
                    self.eat()


                self.state = 110
                self.match(RFilter.T__33)
                self.state = 115
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while (((_la) & ~0x3f) == 0 and ((1 << _la) & -36028975528542220) != 0):
                    self.state = 113
                    self._errHandler.sync(self)
                    token = self._input.LA(1)
                    if token in [2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30, 33, 34, 36, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 56, 57, 58, 59, 60, 61, 62]:
                        self.state = 111
                        self.elem()
                        pass
                    elif token in [63]:
                        self.state = 112
                        self.eat()
                        pass
                    else:
                        raise NoViableAltException(self)

                    self.state = 117
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 118
                self.match(RFilter.T__34)
                self.state = 120
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,24,self._ctx)
                if la_ == 1:
                    self.state = 119
                    self.eat()


                pass
            elif token in [38]:
                self.enterOuterAlt(localctx, 10)
                self.state = 122
                self.match(RFilter.T__37)
                self.state = 124
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==63:
                    self.state = 123
                    self.eat()


                self.state = 126
                self.match(RFilter.T__33)
                self.state = 131
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while (((_la) & ~0x3f) == 0 and ((1 << _la) & -36028975528542220) != 0):
                    self.state = 129
                    self._errHandler.sync(self)
                    token = self._input.LA(1)
                    if token in [2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30, 33, 34, 36, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 56, 57, 58, 59, 60, 61, 62]:
                        self.state = 127
                        self.elem()
                        pass
                    elif token in [63]:
                        self.state = 128
                        self.eat()
                        pass
                    else:
                        raise NoViableAltException(self)

                    self.state = 133
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 134
                self.match(RFilter.T__34)
                self.state = 136
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,28,self._ctx)
                if la_ == 1:
                    self.state = 135
                    self.eat()


                pass
            elif token in [39]:
                self.enterOuterAlt(localctx, 11)
                self.state = 138
                self.match(RFilter.T__38)

                tok = self._input.LT(-2)
                if self.curlies > 0 and tok.type == self.NL:
                   tok.channel = Token.HIDDEN_CHANNEL
                    
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AtomContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(RFilter.ID, 0)

        def STRING(self):
            return self.getToken(RFilter.STRING, 0)

        def HEX(self):
            return self.getToken(RFilter.HEX, 0)

        def INT(self):
            return self.getToken(RFilter.INT, 0)

        def FLOAT(self):
            return self.getToken(RFilter.FLOAT, 0)

        def COMPLEX(self):
            return self.getToken(RFilter.COMPLEX, 0)

        def getRuleIndex(self):
            return RFilter.RULE_atom

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAtom" ):
                listener.enterAtom(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAtom" ):
                listener.exitAtom(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAtom" ):
                return visitor.visitAtom(self)
            else:
                return visitor.visitChildren(self)




    def atom(self):

        localctx = RFilter.AtomContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_atom)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 142
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 4548600439272112128) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OpContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def USER_OP(self):
            return self.getToken(RFilter.USER_OP, 0)

        def getRuleIndex(self):
            return RFilter.RULE_op

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOp" ):
                listener.enterOp(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOp" ):
                listener.exitOp(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOp" ):
                return visitor.visitOp(self)
            else:
                return visitor.visitChildren(self)




    def op(self):

        localctx = RFilter.OpContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_op)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 144
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 4638736205372981216) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





