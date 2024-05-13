from .RVisitor import RVisitor
from .RParser import RParser

class ExtractParams(RVisitor):
    def __init__(self):
        self.params = {}
    
    def visitProg(self, ctx:RParser.ProgContext):
        self.visitChildren(ctx)
        return self.params
    
    def visitAssign(self, ctx: RParser.AssignContext):
        # Get the identifier and the assigned value of the expr and add to dict.
        id = self.visit(ctx.expr(0))

        if id is None:
            return None

        # check if id has param_ prefix
        if id.startswith("param_") and id not in self.params:
            expr = self.visit(ctx.expr(1))
            # If returned expression is empty e.g. in case of unaccessible env variables, do not specify type.
            if expr != "":
                self.params[id] = {'val': expr, 'type': type(expr).__name__}
            else:
                self.params[id] = {'val': expr, 'type': None}

        return None

    def visitId(self, ctx: RParser.IdContext):
        id = ctx.ID().getText()
        return str(id)

    def visitInt(self, ctx: RParser.IntContext):
        val = ctx.INT().getText()
        return int(val)

    def visitFloat(self, ctx: RParser.FloatContext):
        val = ctx.FLOAT().getText()
        return int(val)

    def visitString(self, ctx: RParser.StringContext):
        val = ctx.STRING().getText()
        return str(val[1:-1])