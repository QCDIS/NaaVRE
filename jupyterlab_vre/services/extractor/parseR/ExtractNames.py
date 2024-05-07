from RVisitor import RVisitor
from RParser import RParser

class ExtractNames(RVisitor):
# Build a dictionairy to keep track of all identifiers and their data types
    def __init__(self):
        self.names = {}

    def visitProg(self, ctx:RParser.ProgContext):
        self.visitChildren(ctx)
        return self.names
    
    def visitAssign(self, ctx:RParser.AssignContext):
        # Get the identifier and the assigned value of the expr and add to dict.
        id = self.visit(ctx.expr(0))
        self.names[id] = self.visit(ctx.expr(1))
        return None

    def visitAddsub(self, ctx: RParser.AddsubContext):
        # Visit left and right expressions
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))

        # Check if left and right are in dict i.e. they're variables
        if left in self.names:
            left = self.names[left]
        if right in self.names:
            right = self.names[right]

        # Check if the left and right children are of the same type
        if (left == "int" and right == "int"):
            return "int"
        elif (left == "float" or right == "float"):
            return "float"
        else:
            return None

    def visitMuldiv(self, ctx: RParser.MuldivContext):
        # Same procedure as addsub
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))

        if left in self.names:
            left = self.names[left]
        if right in self.names:
            right = self.names[right]

        if (left == "int" and right == "int"):
            return "int"
        elif (left == "float" or right == "float"):
            return "float"
        else:
            return None

    def visitId(self, ctx:RParser.IdContext):
        id = ctx.ID().getText()
        # Check if id is in dict, otherwise add it.
        if id not in self.names:
            self.names[id] = None
        return id
    
    def visitInt(self, ctx:RParser.IntContext):
        return "int"
    
    def visitFloat(self, ctx: RParser.FloatContext):
        return "float"
    
    def visitString(self, ctx: RParser.StringContext):
        return "string"