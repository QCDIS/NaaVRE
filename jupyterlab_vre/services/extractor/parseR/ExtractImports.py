from .RVisitor import RVisitor
from .RParser import RParser

class ExtractImports(RVisitor):
    def __init__(self):
        self.imports = {}

    def visitProg(self, ctx:RParser.ProgContext):
        self.visitChildren(ctx)
        return self.imports
    
    def visitCall(self, ctx: RParser.CallContext):
        # Check function call of library or require functions indicating an import.
        fun = self.visit(ctx.expr())
        if fun == "library" or fun == "require":
            lib = self.visit(ctx.sublist()).strip('"')
            self.imports[lib] = lib
        return None
    
    def visitId(self, ctx:RParser.IdContext):
        return ctx.ID().getText()
    
    def visitString(self, ctx:RParser.StringContext):
        return ctx.STRING().getText()