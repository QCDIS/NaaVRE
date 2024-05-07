from RVisitor import RVisitor
from RParser import RParser

class ExtractParams(RVisitor):
    def __init__(self):
        self.params = {}
    
    def visitProg(self, ctx:RParser.ProgContext):
        self.visitChildren(ctx)
        return self.params
    
    def visitAssign(self, ctx: RParser.AssignContext):
        # Get the identifier and the assigned value of the expr and add to dict.
        id = self.visit(ctx.expr(0))
        # check if id has param_ prefix
        if id.startswith("param_") and id not in self.params:
            expr = self.visit(ctx.expr(1))
            # TODO we could also use the types gathered from names here.
            self.params[id] = {'expr': expr, 'type': type(expr)}

        return None
    
    def visitId(self, ctx:RParser.IdContext):
        return ctx.ID().getText()
    
    def visitInt(self, ctx:RParser.IntContext):
        return int(ctx.INT().getText())
    
    def visitFloat(self, ctx: RParser.FloatContext):
        return super().visitFloat(ctx)
    
    def visitString(self, ctx: RParser.StringContext):
        return super().visitString(ctx) 