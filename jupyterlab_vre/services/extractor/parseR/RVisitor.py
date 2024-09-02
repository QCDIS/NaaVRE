# Generated from R.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .RParser import RParser
else:
    from RParser import RParser

# This class defines a complete generic visitor for a parse tree produced by RParser.

class RVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by RParser#prog.
    def visitProg(self, ctx:RParser.ProgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#next.
    def visitNext(self, ctx:RParser.NextContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#parens.
    def visitParens(self, ctx:RParser.ParensContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#compare.
    def visitCompare(self, ctx:RParser.CompareContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#string.
    def visitString(self, ctx:RParser.StringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#userop.
    def visitUserop(self, ctx:RParser.UseropContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#for.
    def visitFor(self, ctx:RParser.ForContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#dot.
    def visitDot(self, ctx:RParser.DotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#addsub.
    def visitAddsub(self, ctx:RParser.AddsubContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#index2.
    def visitIndex2(self, ctx:RParser.Index2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#unary.
    def visitUnary(self, ctx:RParser.UnaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#while.
    def visitWhile(self, ctx:RParser.WhileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#float.
    def visitFloat(self, ctx:RParser.FloatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#not.
    def visitNot(self, ctx:RParser.NotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#and.
    def visitAnd(self, ctx:RParser.AndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#function.
    def visitFunction(self, ctx:RParser.FunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#repeat.
    def visitRepeat(self, ctx:RParser.RepeatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#complex.
    def visitComplex(self, ctx:RParser.ComplexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#block.
    def visitBlock(self, ctx:RParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#hex.
    def visitHex(self, ctx:RParser.HexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#nan.
    def visitNan(self, ctx:RParser.NanContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#id.
    def visitId(self, ctx:RParser.IdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#power.
    def visitPower(self, ctx:RParser.PowerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#if.
    def visitIf(self, ctx:RParser.IfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#seq.
    def visitSeq(self, ctx:RParser.SeqContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#inf.
    def visitInf(self, ctx:RParser.InfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#or.
    def visitOr(self, ctx:RParser.OrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#break.
    def visitBreak(self, ctx:RParser.BreakContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#false.
    def visitFalse(self, ctx:RParser.FalseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#index.
    def visitIndex(self, ctx:RParser.IndexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#int.
    def visitInt(self, ctx:RParser.IntContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#muldiv.
    def visitMuldiv(self, ctx:RParser.MuldivContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#ifelse.
    def visitIfelse(self, ctx:RParser.IfelseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#call.
    def visitCall(self, ctx:RParser.CallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#help.
    def visitHelp(self, ctx:RParser.HelpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#na.
    def visitNa(self, ctx:RParser.NaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#extract.
    def visitExtract(self, ctx:RParser.ExtractContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#null.
    def visitNull(self, ctx:RParser.NullContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#utilde.
    def visitUtilde(self, ctx:RParser.UtildeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#true.
    def visitTrue(self, ctx:RParser.TrueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#namespace.
    def visitNamespace(self, ctx:RParser.NamespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#btilde.
    def visitBtilde(self, ctx:RParser.BtildeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#assign.
    def visitAssign(self, ctx:RParser.AssignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#exprlist.
    def visitExprlist(self, ctx:RParser.ExprlistContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#formlist.
    def visitFormlist(self, ctx:RParser.FormlistContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#form.
    def visitForm(self, ctx:RParser.FormContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#sublist.
    def visitSublist(self, ctx:RParser.SublistContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RParser#sub.
    def visitSub(self, ctx:RParser.SubContext):
        return self.visitChildren(ctx)



del RParser