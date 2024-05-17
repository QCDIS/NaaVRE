# Generated from R.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .RParser import RParser
else:
    from RParser import RParser

# This class defines a complete listener for a parse tree produced by RParser.
class RListener(ParseTreeListener):

    # Enter a parse tree produced by RParser#prog.
    def enterProg(self, ctx:RParser.ProgContext):
        pass

    # Exit a parse tree produced by RParser#prog.
    def exitProg(self, ctx:RParser.ProgContext):
        pass


    # Enter a parse tree produced by RParser#next.
    def enterNext(self, ctx:RParser.NextContext):
        pass

    # Exit a parse tree produced by RParser#next.
    def exitNext(self, ctx:RParser.NextContext):
        pass


    # Enter a parse tree produced by RParser#parens.
    def enterParens(self, ctx:RParser.ParensContext):
        pass

    # Exit a parse tree produced by RParser#parens.
    def exitParens(self, ctx:RParser.ParensContext):
        pass


    # Enter a parse tree produced by RParser#compare.
    def enterCompare(self, ctx:RParser.CompareContext):
        pass

    # Exit a parse tree produced by RParser#compare.
    def exitCompare(self, ctx:RParser.CompareContext):
        pass


    # Enter a parse tree produced by RParser#string.
    def enterString(self, ctx:RParser.StringContext):
        pass

    # Exit a parse tree produced by RParser#string.
    def exitString(self, ctx:RParser.StringContext):
        pass


    # Enter a parse tree produced by RParser#userop.
    def enterUserop(self, ctx:RParser.UseropContext):
        pass

    # Exit a parse tree produced by RParser#userop.
    def exitUserop(self, ctx:RParser.UseropContext):
        pass


    # Enter a parse tree produced by RParser#for.
    def enterFor(self, ctx:RParser.ForContext):
        pass

    # Exit a parse tree produced by RParser#for.
    def exitFor(self, ctx:RParser.ForContext):
        pass


    # Enter a parse tree produced by RParser#dot.
    def enterDot(self, ctx:RParser.DotContext):
        pass

    # Exit a parse tree produced by RParser#dot.
    def exitDot(self, ctx:RParser.DotContext):
        pass


    # Enter a parse tree produced by RParser#addsub.
    def enterAddsub(self, ctx:RParser.AddsubContext):
        pass

    # Exit a parse tree produced by RParser#addsub.
    def exitAddsub(self, ctx:RParser.AddsubContext):
        pass


    # Enter a parse tree produced by RParser#index2.
    def enterIndex2(self, ctx:RParser.Index2Context):
        pass

    # Exit a parse tree produced by RParser#index2.
    def exitIndex2(self, ctx:RParser.Index2Context):
        pass


    # Enter a parse tree produced by RParser#unary.
    def enterUnary(self, ctx:RParser.UnaryContext):
        pass

    # Exit a parse tree produced by RParser#unary.
    def exitUnary(self, ctx:RParser.UnaryContext):
        pass


    # Enter a parse tree produced by RParser#while.
    def enterWhile(self, ctx:RParser.WhileContext):
        pass

    # Exit a parse tree produced by RParser#while.
    def exitWhile(self, ctx:RParser.WhileContext):
        pass


    # Enter a parse tree produced by RParser#float.
    def enterFloat(self, ctx:RParser.FloatContext):
        pass

    # Exit a parse tree produced by RParser#float.
    def exitFloat(self, ctx:RParser.FloatContext):
        pass


    # Enter a parse tree produced by RParser#not.
    def enterNot(self, ctx:RParser.NotContext):
        pass

    # Exit a parse tree produced by RParser#not.
    def exitNot(self, ctx:RParser.NotContext):
        pass


    # Enter a parse tree produced by RParser#and.
    def enterAnd(self, ctx:RParser.AndContext):
        pass

    # Exit a parse tree produced by RParser#and.
    def exitAnd(self, ctx:RParser.AndContext):
        pass


    # Enter a parse tree produced by RParser#function.
    def enterFunction(self, ctx:RParser.FunctionContext):
        pass

    # Exit a parse tree produced by RParser#function.
    def exitFunction(self, ctx:RParser.FunctionContext):
        pass


    # Enter a parse tree produced by RParser#repeat.
    def enterRepeat(self, ctx:RParser.RepeatContext):
        pass

    # Exit a parse tree produced by RParser#repeat.
    def exitRepeat(self, ctx:RParser.RepeatContext):
        pass


    # Enter a parse tree produced by RParser#complex.
    def enterComplex(self, ctx:RParser.ComplexContext):
        pass

    # Exit a parse tree produced by RParser#complex.
    def exitComplex(self, ctx:RParser.ComplexContext):
        pass


    # Enter a parse tree produced by RParser#block.
    def enterBlock(self, ctx:RParser.BlockContext):
        pass

    # Exit a parse tree produced by RParser#block.
    def exitBlock(self, ctx:RParser.BlockContext):
        pass


    # Enter a parse tree produced by RParser#hex.
    def enterHex(self, ctx:RParser.HexContext):
        pass

    # Exit a parse tree produced by RParser#hex.
    def exitHex(self, ctx:RParser.HexContext):
        pass


    # Enter a parse tree produced by RParser#nan.
    def enterNan(self, ctx:RParser.NanContext):
        pass

    # Exit a parse tree produced by RParser#nan.
    def exitNan(self, ctx:RParser.NanContext):
        pass


    # Enter a parse tree produced by RParser#id.
    def enterId(self, ctx:RParser.IdContext):
        pass

    # Exit a parse tree produced by RParser#id.
    def exitId(self, ctx:RParser.IdContext):
        pass


    # Enter a parse tree produced by RParser#power.
    def enterPower(self, ctx:RParser.PowerContext):
        pass

    # Exit a parse tree produced by RParser#power.
    def exitPower(self, ctx:RParser.PowerContext):
        pass


    # Enter a parse tree produced by RParser#if.
    def enterIf(self, ctx:RParser.IfContext):
        pass

    # Exit a parse tree produced by RParser#if.
    def exitIf(self, ctx:RParser.IfContext):
        pass


    # Enter a parse tree produced by RParser#seq.
    def enterSeq(self, ctx:RParser.SeqContext):
        pass

    # Exit a parse tree produced by RParser#seq.
    def exitSeq(self, ctx:RParser.SeqContext):
        pass


    # Enter a parse tree produced by RParser#inf.
    def enterInf(self, ctx:RParser.InfContext):
        pass

    # Exit a parse tree produced by RParser#inf.
    def exitInf(self, ctx:RParser.InfContext):
        pass


    # Enter a parse tree produced by RParser#or.
    def enterOr(self, ctx:RParser.OrContext):
        pass

    # Exit a parse tree produced by RParser#or.
    def exitOr(self, ctx:RParser.OrContext):
        pass


    # Enter a parse tree produced by RParser#break.
    def enterBreak(self, ctx:RParser.BreakContext):
        pass

    # Exit a parse tree produced by RParser#break.
    def exitBreak(self, ctx:RParser.BreakContext):
        pass


    # Enter a parse tree produced by RParser#false.
    def enterFalse(self, ctx:RParser.FalseContext):
        pass

    # Exit a parse tree produced by RParser#false.
    def exitFalse(self, ctx:RParser.FalseContext):
        pass


    # Enter a parse tree produced by RParser#index.
    def enterIndex(self, ctx:RParser.IndexContext):
        pass

    # Exit a parse tree produced by RParser#index.
    def exitIndex(self, ctx:RParser.IndexContext):
        pass


    # Enter a parse tree produced by RParser#int.
    def enterInt(self, ctx:RParser.IntContext):
        pass

    # Exit a parse tree produced by RParser#int.
    def exitInt(self, ctx:RParser.IntContext):
        pass


    # Enter a parse tree produced by RParser#muldiv.
    def enterMuldiv(self, ctx:RParser.MuldivContext):
        pass

    # Exit a parse tree produced by RParser#muldiv.
    def exitMuldiv(self, ctx:RParser.MuldivContext):
        pass


    # Enter a parse tree produced by RParser#ifelse.
    def enterIfelse(self, ctx:RParser.IfelseContext):
        pass

    # Exit a parse tree produced by RParser#ifelse.
    def exitIfelse(self, ctx:RParser.IfelseContext):
        pass


    # Enter a parse tree produced by RParser#call.
    def enterCall(self, ctx:RParser.CallContext):
        pass

    # Exit a parse tree produced by RParser#call.
    def exitCall(self, ctx:RParser.CallContext):
        pass


    # Enter a parse tree produced by RParser#help.
    def enterHelp(self, ctx:RParser.HelpContext):
        pass

    # Exit a parse tree produced by RParser#help.
    def exitHelp(self, ctx:RParser.HelpContext):
        pass


    # Enter a parse tree produced by RParser#na.
    def enterNa(self, ctx:RParser.NaContext):
        pass

    # Exit a parse tree produced by RParser#na.
    def exitNa(self, ctx:RParser.NaContext):
        pass


    # Enter a parse tree produced by RParser#extract.
    def enterExtract(self, ctx:RParser.ExtractContext):
        pass

    # Exit a parse tree produced by RParser#extract.
    def exitExtract(self, ctx:RParser.ExtractContext):
        pass


    # Enter a parse tree produced by RParser#null.
    def enterNull(self, ctx:RParser.NullContext):
        pass

    # Exit a parse tree produced by RParser#null.
    def exitNull(self, ctx:RParser.NullContext):
        pass


    # Enter a parse tree produced by RParser#utilde.
    def enterUtilde(self, ctx:RParser.UtildeContext):
        pass

    # Exit a parse tree produced by RParser#utilde.
    def exitUtilde(self, ctx:RParser.UtildeContext):
        pass


    # Enter a parse tree produced by RParser#true.
    def enterTrue(self, ctx:RParser.TrueContext):
        pass

    # Exit a parse tree produced by RParser#true.
    def exitTrue(self, ctx:RParser.TrueContext):
        pass


    # Enter a parse tree produced by RParser#namespace.
    def enterNamespace(self, ctx:RParser.NamespaceContext):
        pass

    # Exit a parse tree produced by RParser#namespace.
    def exitNamespace(self, ctx:RParser.NamespaceContext):
        pass


    # Enter a parse tree produced by RParser#btilde.
    def enterBtilde(self, ctx:RParser.BtildeContext):
        pass

    # Exit a parse tree produced by RParser#btilde.
    def exitBtilde(self, ctx:RParser.BtildeContext):
        pass


    # Enter a parse tree produced by RParser#assign.
    def enterAssign(self, ctx:RParser.AssignContext):
        pass

    # Exit a parse tree produced by RParser#assign.
    def exitAssign(self, ctx:RParser.AssignContext):
        pass


    # Enter a parse tree produced by RParser#exprlist.
    def enterExprlist(self, ctx:RParser.ExprlistContext):
        pass

    # Exit a parse tree produced by RParser#exprlist.
    def exitExprlist(self, ctx:RParser.ExprlistContext):
        pass


    # Enter a parse tree produced by RParser#formlist.
    def enterFormlist(self, ctx:RParser.FormlistContext):
        pass

    # Exit a parse tree produced by RParser#formlist.
    def exitFormlist(self, ctx:RParser.FormlistContext):
        pass


    # Enter a parse tree produced by RParser#form.
    def enterForm(self, ctx:RParser.FormContext):
        pass

    # Exit a parse tree produced by RParser#form.
    def exitForm(self, ctx:RParser.FormContext):
        pass


    # Enter a parse tree produced by RParser#sublist.
    def enterSublist(self, ctx:RParser.SublistContext):
        pass

    # Exit a parse tree produced by RParser#sublist.
    def exitSublist(self, ctx:RParser.SublistContext):
        pass


    # Enter a parse tree produced by RParser#sub.
    def enterSub(self, ctx:RParser.SubContext):
        pass

    # Exit a parse tree produced by RParser#sub.
    def exitSub(self, ctx:RParser.SubContext):
        pass



del RParser