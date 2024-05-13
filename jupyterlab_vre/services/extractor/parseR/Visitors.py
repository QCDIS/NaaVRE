from .RVisitor import RVisitor
from .RParser import RParser
import re


class ExtractDefs(RVisitor):
    def __init__(self):
        self.defs = set()

    def visitProg(self, ctx: RParser.ProgContext):
        self.visitChildren(ctx)
        return self.defs

    def visitAssign(self, ctx: RParser.AssignContext):
        # Get the identifier and the assigned value of the expr and add to dict.
        id = self.visit(ctx.expr(0))

        if id is None:
            return None

        self.defs.add(id)

        return None

    def visitCall(self, ctx: RParser.CallContext):
        self.visit(ctx.expr())
        return None

    def visitId(self, ctx: RParser.IdContext):
        return ctx.getText()


class ExtractInputs(RVisitor):
    def __init__(self, defs):
        self.defs = defs
        self.inputs = set()
        self.scoped = set()

    def visitProg(self, ctx: RParser.ProgContext):
        self.visitChildren(ctx)
        # remove all inputs with conf_ or param_ prefix
        self.inputs = {i for i in self.inputs if not i.startswith("conf_") and not i.startswith("param_")}
        # remove all built in constants ["T", "F", "pi", "is.numeric", "mu", "round"]
        self.inputs = {i for i in self.inputs if i not in ["T", "F", "pi", "is.numeric", "mu", "round"]}
        return self.inputs

    def visitSublist(self, ctx: RParser.SublistContext):
        self.visitChildren(ctx)

    def visitSub(self, ctx: RParser.SubContext):
        # If function, add all its arguments to scoped, which we find using regex
        if ctx.getText().startswith("function"):
            ids = re.findall(r'\((.*?)\)', ctx.getText())[0].split(", ")
            ids = ids[0].split(",")

            # add all ids to scoped
            for id in ids:
                self.scoped.add(id)

            self.visitChildren(ctx)
            # remove all ids from scoped
            for id in ids:
                self.scoped.remove(id)
            return None

        if ctx.expr() is not None:
            self.visitChildren(ctx)

    def visitFor(self, ctx: RParser.ForContext):
        # Iterator variable is scoped
        self.scoped.add(ctx.ID().getText())
        self.visit(ctx.expr(0))
        self.visit(ctx.expr(1))
        self.scoped.remove(ctx.ID().getText())
        return None

    def visitAssign(self, ctx: RParser.AssignContext):
        return None

    def visitCall(self, ctx: RParser.CallContext):
        # Skip import calls
        if ctx.expr().getText() == "library" or ctx.expr().getText() == "require":
            return None

        self.visit(ctx.sublist())

    def visitId(self, ctx: RParser.IdContext):
        # Only add IDs to input if they have not been defined and are not scoped.
        if ctx.getText() not in self.defs and ctx.getText() not in self.scoped:
            self.inputs.add(ctx.getText())
        return None


class ExtractParams(RVisitor):
    def __init__(self):
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


class ExtractNames(RVisitor):
    # Build a dictionairy to keep track of all identifiers and their data types
    def __init__(self):
        self.names = {}

    def visitProg(self, ctx: RParser.ProgContext):
        self.visitChildren(ctx)
        return self.names

    def visitAssign(self, ctx: RParser.AssignContext):
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

    def visitId(self, ctx: RParser.IdContext):
        id = ctx.ID().getText()
        # Check if id is in dict, otherwise add it.
        if id not in self.names:
            self.names[id] = None
        return id

    def visitInt(self, ctx: RParser.IntContext):
        return "int"

    def visitFloat(self, ctx: RParser.FloatContext):
        return "float"

    def visitString(self, ctx: RParser.StringContext):
        return "string"


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
        return None

    def visitId(self, ctx: RParser.IdContext):
        return ctx.ID().getText()

    def visitString(self, ctx: RParser.StringContext):
        return ctx.STRING().getText()