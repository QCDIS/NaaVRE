from .RVisitor import RVisitor
from .RParser import RParser

built_in = ["T", "F", "pi", "is.numeric", "mu", "round"]


class ExtractNames(RVisitor):
    # Get all names and try to infer their types.
    def __init__(self):
        self.names = {}
        self.scoped = set()

    def visitProg(self, ctx: RParser.ProgContext):
        self.visitChildren(ctx)
        return self.names

    def visitCall(self, ctx: RParser.CallContext):
        if isinstance(ctx.expr(), RParser.AssignContext):
            self.visit(ctx.expr())
        self.visit(ctx.sublist())

    def visitFor(self, ctx: RParser.ForContext):
        # Iterator variable is scoped
        self.scoped.add(ctx.ID().getText())
        # If what we iterate over is a variable, type should be list.
        if isinstance(ctx.expr(0), RParser.IdContext):
            self.visit(ctx.expr(0))
            id = ctx.expr(0).getText()
            self.names[id]['type'] = 'list'
        self.visit(ctx.expr(1))
        self.scoped.remove(ctx.ID().getText())

    def visitSub(self, ctx: RParser.SubContext):
        if isinstance(ctx.expr(), RParser.IdContext):
            self.visit(ctx.expr())

    def visitSublist(self, ctx: RParser.SublistContext):
        self.visitChildren(ctx)

    def visitAssign(self, ctx: RParser.AssignContext):
        # Get the identifier and the assigned value of the expr and add to dict.
        id = self.visit(ctx.expr(0))
        xp1 = ctx.expr(1).getText()
        if id is None:
            return None

        if id in self.names and self.names[id]['type'] is not None:
            return None
        # Check if the value is an ID or an expression of which we can get type.
        if xp1 == 'list':
            self.names[id] = {'name': id, 'type': 'list'}
        elif isinstance(ctx.expr(1), RParser.IdContext):
            self.names[id] = {'name': id, 'type': None}
        else:
            type = self.visit(ctx.expr(1))
            self.names[id] = {'name': id, 'type': type}

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

    def visitId(self, ctx: RParser.IdContext):
        id = ctx.ID().getText()
        # Check if id is in dict, otherwise add it.
        if id not in self.names and id not in self.scoped:
            self.names[id] = {'name': id, 'type': None}
        return id

    def visitInt(self, ctx: RParser.IntContext):
        return "int"

    def visitFloat(self, ctx: RParser.FloatContext):
        return "float"

    def visitString(self, ctx: RParser.StringContext):
        return "str"


class ExtractUndefined(RVisitor):
    def __init__(self, defs, scoped):
        self.undefined = set()
        self.defs = defs
        self.scoped = scoped

    def visitProg(self, ctx: RParser.ProgContext):
        self.visitChildren(ctx)
        return self.undefined

    def visitAssign(self, ctx: RParser.AssignContext):
        self.visitChildren(ctx)

    def visitCall(self, ctx: RParser.CallContext):
        # If expr startswith 'function', all sub variables are scoped.
        if ctx.expr().getText().startswith('function'):
            for sub in ctx.sublist().sub():
                self.scoped.add(sub.getText())
        else:
            if isinstance(ctx.expr(), RParser.UseropContext):
                self.visit(ctx.expr())
            self.visit(ctx.sublist())

    # TEST
    def visitUserop(self, ctx: RParser.UseropContext):
        if isinstance(ctx.expr(0), RParser.CallContext):
            self.visit(ctx.expr(0))
        if isinstance(ctx.expr(1), RParser.CallContext):
            self.visit(ctx.expr(1))

    def visitSublist(self, ctx: RParser.SublistContext):
        self.visitChildren(ctx)

    def visitExtract(self, ctx: RParser.ExtractContext):
        self.visit(ctx.expr(0))

    def visitSub(self, ctx: RParser.SubContext):
        if isinstance(ctx.expr(), RParser.IdContext):
            self.visit(ctx.expr())
        elif isinstance(ctx.expr(), RParser.AssignContext):
            self.scoped.add(ctx.expr().expr(0).getText())
            self.visit(ctx.expr().expr(1))
        elif isinstance(ctx.expr(), RParser.CallContext):
            self.visit(ctx.expr())
        elif isinstance(ctx.expr(), RParser.FunctionContext):
            self.visit(ctx.expr())

    def visitFunction(self, ctx: RParser.FunctionContext):
        self.visit(ctx.formlist())
        self.visit(ctx.expr())

    def visitFormlist(self, ctx: RParser.FormlistContext):
        self.visitChildren(ctx)

    def visitForm(self, ctx: RParser.FormContext):
        self.scoped.add(ctx.ID().getText())
        if isinstance(ctx.expr(), RParser.IdContext):
            self.visit(ctx.expr())

    def visitFor(self, ctx: RParser.ForContext):
        # Iterator variable is scoped
        self.scoped.add(ctx.ID().getText())
        self.visit(ctx.expr(0))
        self.visit(ctx.expr(1))
        self.scoped.remove(ctx.ID().getText())

    def visitId(self, ctx: RParser.IdContext):
        id = ctx.ID().getText()
        if id not in self.defs and id not in self.scoped and id not in built_in:
            self.undefined.add(ctx.getText())


class ExtractDefined(RVisitor):
    def __init__(self):
        self.defs = set()
        self.scoped = set()
        self.scope = False

    def visitProg(self, ctx: RParser.ProgContext):
        self.visitChildren(ctx)
        return self.defs, self.scoped

    def visitAssign(self, ctx: RParser.AssignContext):
        # Get the identifier and the assigned value of the expr and add to dict.
        id = self.visit(ctx.expr(0))

        if id is None:
            return None

        if id not in self.scoped and not self.scope:
            self.defs.add(id)
        elif self.scope:
            self.scoped.add(id)

        self.visit(ctx.expr(1))

    def visitCall(self, ctx: RParser.CallContext):
        self.visit(ctx.expr())
        self.visit(ctx.sublist())

    def visitSublist(self, ctx: RParser.SublistContext):
        self.visitChildren(ctx)

    def visitSub(self, ctx: RParser.SubContext):
        # Deal with nested subs
        reset = True
        if self.scope:
            reset = False
        self.scope = True
        if isinstance(ctx.expr(), RParser.IdContext):
            self.visit(ctx.expr())
        elif isinstance(ctx.expr(), RParser.AssignContext):
            self.scoped.add(ctx.expr().expr(0).getText())
            self.visit(ctx.expr().expr(1))
        elif isinstance(ctx.expr(), RParser.CallContext):
            self.visit(ctx.expr())
        elif isinstance(ctx.expr(), RParser.FunctionContext):
            self.visit(ctx.expr())
        if reset:
            self.scope = False

    def visitId(self, ctx: RParser.IdContext):
        return ctx.getText()


class ExtractPrefixedVar(RVisitor):
    def __init__(self, prefix):
        self.prefix = prefix+'_'
        self.params = {}

    def visitProg(self, ctx: RParser.ProgContext):
        self.visitChildren(ctx)
        return self.params

    def visitAssign(self, ctx: RParser.AssignContext):
        # Get the identifier and the assigned value of the expr and add to dict.
        id = self.visit(ctx.expr(0))
        if id is None:
            return None
        # check if id has param_ prefix
        if id.startswith(self.prefix): #and id not in self.params:
            if self.params[id]['val'] is None or id not in self.params:
                expr = self.visit(ctx.expr(1))
                # If returned expression is empty e.g. in case of unaccessible env variables, do not specify type.
                if expr != "":
                    self.params[id] = {'val': expr, 'type': type(expr).__name__}
                else:
                    self.params[id] = {'val': expr, 'type': None}
        return None

    def visitCall(self, ctx: RParser.CallContext):
        if isinstance(ctx.expr(), RParser.AssignContext):
            if ctx.expr().expr(1).getText() == 'list':
                val = ctx.sublist().getText()
                self.params[ctx.expr().expr(0).getText()] = {'val': val, 'type': 'list'}


    def visitId(self, ctx: RParser.IdContext):
        id = ctx.ID().getText()
        if id.startswith(self.prefix) and id not in self.params:
            self.params[id] = {'val': None, 'type': None}

        return str(id)

    def visitInt(self, ctx: RParser.IntContext):
        val = ctx.INT().getText()
        # check if L suffix is present
        if val[-1] == "L":
            val = val[:-1]
        return int(val)

    def visitFloat(self, ctx: RParser.FloatContext):
        val = ctx.FLOAT().getText()
        return float(val)

    def visitString(self, ctx: RParser.StringContext):
        val = ctx.STRING().getText()
        return str(val[1:-1])


class ExtractConfigs(RVisitor):
    def __init__(self):
        self.configs = {}

    def visitProg(self, ctx: RParser.ProgContext):
        self.visitChildren(ctx)
        return self.configs

    def visitAssign(self, ctx: RParser.AssignContext):
        # Get the identifier and the assigned value of the expr and add to dict.
        id = self.visit(ctx.expr(0))

        if id is None:
            return None

        # check if id has conf_ prefix
        if id.startswith("conf_") and id not in self.configs:
            self.configs[id] = ctx.getText()

        return None

    def visitId(self, ctx: RParser.IdContext):
        return ctx.ID().getText()

    def visitString(self, ctx: RParser.StringContext):
        # In the case of environment variables, identifier could be string.
        return ctx.STRING().getText()


class ExtractImports(RVisitor):
    def __init__(self):
        self.imports = {}

    def visitProg(self, ctx: RParser.ProgContext):
        self.visitChildren(ctx)
        return self.imports

    def visitCall(self, ctx: RParser.CallContext):
        # Check function call of library or require functions indicating an import.
        fun = self.visit(ctx.expr())
        if fun == "library" or fun == "require":
            lib = self.visit(ctx.sublist()).strip('"')
            self.imports[lib] = lib

    def visitId(self, ctx: RParser.IdContext):
        return ctx.ID().getText()

    def visitString(self, ctx: RParser.StringContext):
        return ctx.STRING().getText()
