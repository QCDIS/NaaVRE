from RVisitor import RVisitor
from RParser import RParser

class ExtractConfigs(RVisitor):
    def __init__(self):
        self.configs = {}

    def visitProg(self, ctx:RParser.ProgContext):
        self.visitChildren(ctx)
        return self.configs
    
    def visitAssign(self, ctx:RParser.AssignContext):
        # Get the identifier and the assigned value of the expr and add to dict.
        id = self.visit(ctx.expr(0))
        # check if id has conf_ prefix
        if id.startswith("conf_") and id not in self.configs:
            self.configs[id] = ctx.expr(1).getText()

        return None
    
    def visitId (self, ctx:RParser.IdContext):
        return ctx.ID().getText()