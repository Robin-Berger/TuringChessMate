class ChessPiece:
    def __init__(self,pos):
        self.pos = pos
        self.possible_moves = []
        self.extra_moves = []
        self.capture_moves = []
        self.extra_capture_moves = []
        self.repeat_moves = False

class ChessPieceKing(ChessPiece):
    def __init__(self,pos):
        ChessPiece.__init__(self, pos)
        self.repeat_moves = False
        self.possible_moves=[(1,0),(1,1),(0,1),(-1,-1),(-1,0),(-1,-1),(0,-1),(1,-1)]

class ChessPieceKnight(ChessPiece):
    def __init__(self, pos):
        ChessPiece.__init__(self, pos)
        self.repeat_moves = False
        self.possible_moves=[(2, 1),(1,2),(-1, 2),(1,-2),(-2,-1),(-1,-2),(1,-2),(2,-1)]

class ChessPieceBishop(ChessPiece):
    def __init__(self, pos):
        ChessPiece.__init__(self, pos)
        self.repeat_moves = True
        self.possible_moves = [(1, 1), (-1, 1), (-1, -1), (1, -1)]

class ChessPieceTower(ChessPiece):
    def __init__(self, pos):
        ChessPiece.__init__(self, pos)
        self.repeat_moves = True
        self.possible_moves=[(0,-1),(1,0),(0,1),(-1,0)]

class ChessPiecePawn(ChessPiece):
    def __init__(self, pos):
        ChessPiece.__init__(self, pos)
        self.repeat_moves = True
        self.possible_moves = [(1, 0)]
        self.extra_moves = [(2, 0)]
        self.capture_moves = [(1, 1),(1, -1)]
        self.extra_capture_moves = [(0, 1),(0, -1)]
