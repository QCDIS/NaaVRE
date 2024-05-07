from RParser import RParser

from RListener import RListener

class MyListener(RListener):
    def __init__(self, stream) -> None:
        super().__init__()
        self.exps = []
        self.token_stream = stream

    def enterProg(self, ctx: RParser.ProgContext):
        print("enterProg")

    def exitProg(self, ctx: RParser.ProgContext):
        print("exitProg")

    def enterId(self, ctx: RParser.IdContext):
        print(ctx.ID().getText())