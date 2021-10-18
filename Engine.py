import copy
import numpy as np

pieceValues = {"p": 100, "N": 300, "B": 300, "R": 500, "Q": 900, "K": 0}

class GameState():
  def __init__(self):
    self.board = np.array([
      ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
      ['bp', 'bp', 'bp', 'bp', 'bp', '--', '--', 'bp'],
      ['--', '--', '--', '--', '--', 'bp', '--', '--'],
      ['--', '--', '--', '--', '--', '--', 'bp', '--'],
      ['--', '--', '--', '--', 'wp' '--', '--', '--'],
      ['--', '--', '--', 'wp', '--', '--', '--', '--'],
      ['wp', 'wp', 'wp', '--', '--', 'wp', 'wp', 'wp'],
      ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
    ])

    self.moveFunctions = {"p" : self.getPawnMoves, "R" : self.getRookMoves, "B" : self.getBishopMoves, "N" : self.getKnightMoves, "Q" : self.getQueenMoves, "K" : self.getKingMoves}
    self.promotionOptions = ("Q", "R", "B", "N")
    self.whiteToMove = True
    self.moveLog = []
    self.whiteKingLocation = (7, 4)
    self.blackKingLocation = (0, 4)
    self.inCheck = False
    self.pins = []
    self.checks = []
    self.checkmate = False
    self.stalemate = False
    self.enPassantPossible = ()
    self.enPassantPossibleLog = [self.enPassantPossible]
    self.currentCastlingRight = CastleRights(True, True, True, True)
    self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

  def makeMove(self, move):
    self.board[move.startRow][move.startCol] = "--"
    self.board[move.endRow][move.endCol] = move.pieceMoved
    self.moveLog.append(move)
    self.whiteToMove = not self.whiteToMove
    if move.pieceMoved == "wK":
      self.whiteKingLocation = (move.endRow, move.endCol)
    elif move.pieceMoved == "bK":
      self.blackKingLocation = (move.endRow, move.endCol)

    if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
      self.enPassantPossible = ((move.endRow + move.startRow) // 2, move.endCol)
    else:
      self.enPassantPossible = ()
    
    self.enPassantPossibleLog.append(self.enPassantPossible)

    if move.enPassant:
      self.board[move.startRow][move.endCol] = "--"

    if move.pawnPromotion:
      promotedPiece = "Q"
      '''while promotedPiece not in self.promotionOptions:
        promotedPiece = input("Promote to Q, R, B, or N: ").upper()'''
      self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece


    self.updateCastleRights(move)
    self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    if move.castle:
      if move.endCol - move.startCol == 2:
        self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
        self.board[move.endRow][move.endCol + 1] = "--"
      else:
        self.board[move.endRow] [move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
        self.board[move.endRow][move.endCol - 2] = "--"

  def undoMove(self):
    if len(self.moveLog) != 0:
      move = self.moveLog.pop()
      self.board[move.startRow][move.startCol] = move.pieceMoved
      self.board[move.endRow][move.endCol] = move.pieceCaptured
      self.whiteToMove = not self.whiteToMove
      if move.pieceMoved == "wK":
        self.whiteKingLocation = (move.startRow, move.startCol)
      elif move.pieceMoved == "bK":
        self.blackKingLocation = (move.startRow, move.startCol)

      if move.enPassant:
        self.board[move.endRow][move.endCol] = "--"
        self.board[move.startRow][move.endCol] = move.pieceCaptured
        
      self.enPassantPossibleLog.pop()
      self.enPassantPossible = copy.deepcopy(self.enPassantPossibleLog[-1])

      self.castleRightsLog.pop()
      castleRights = copy.deepcopy(self.castleRightsLog[-1])
      self.currentCastlingRight = castleRights

      if move.castle:
        if move.endCol - move.startCol == 2:
          self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
          self.board[move.endRow][move.endCol - 1] = "--"
        else:
          self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
          self.board[move.endRow][move.endCol + 1] = "--"
      
      self.checkmate = False
      self.stalemate = False


  def updateCastleRights(self, move):
    if move.pieceMoved == "wK":
      self.currentCastlingRight.wks = False
      self.currentCastlingRight.wqs = False
    elif move.pieceMoved == "bK":
      self.currentCastlingRight.bks = False
      self.currentCastlingRight.bqs = False
    elif move.pieceMoved == "wR":
      if move.startRow == 7:
        if move.startCol == 0:
          self.currentCastlingRight.wqs = False
        elif move.startCol == 7:
          self.currentCastlingRight.wks = False
    elif move.pieceMoved == "bR":
      if move.startRow == 0:
        if move.startCol == 0:
          self.currentCastlingRight.bqs = False
        elif move.startCol == 7:
          self.currentCastlingRight.bks = False

    if move.pieceCaptured == "wR":
      if move.endRow == 7:
        if move.endCol == 0:
          self.currentCastlingRight.wqs = False
        elif move.endCol == 7:
          self.currentCastlingRight.wks = False
    elif move.pieceCaptured == "bR":
      if move.endRow == 0:
        if move.endCol == 0:
          self.currentCastlingRight.bqs = False
        elif move.endCol == 7:
          self.currentCastlingRight.bks = False
  
  def getValidMoves(self):
    moves = []
    self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
    if self.whiteToMove:
      kingRow = self.whiteKingLocation[0]
      kingCol = self.whiteKingLocation[1]
    else:
      kingRow = self.blackKingLocation[0]
      kingCol = self.blackKingLocation[1]
    if self.inCheck:
      if len(self.checks) == 1:
        moves = self.getPossibleMoves()
        check = self.checks[0]
        checkRow = check[0]
        checkCol = check[1]
        pieceChecking = self.board[checkRow][checkCol]
        validSquares = []
        if pieceChecking[1] == "N":
          validSquares = [(checkRow, checkCol)]
        else:
          for i in range(1, 8):
            validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
            validSquares.append(validSquare)
            if validSquare[0] == checkRow and validSquare[1] == checkCol:
              break
        for i in range(len(moves) -1, -1, -1):
          if moves[i].pieceMoved[1] != "K":
            if not (moves[i].endRow, moves[i].endCol) in validSquares:
              moves.remove(moves[i])
      else:
        self.getKingMoves(kingRow, kingCol, moves)
    else:
      moves = self.getPossibleMoves()
    
    if len(moves) == 0:
      if self.inCheck:
        self.checkmate = True
      else:
        self.stalemate = True
    else:
      self.checkmate = False
      self.stalemate = False

    return moves

  def getPossibleMoves(self):
    moves = []
    for r in range(len(self.board)):
      for c in range(len(self.board[r])):
        turn = self.board[r][c][0]
        if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
          piece = self.board[r][c][1]
          self.moveFunctions[piece](r, c, moves)
    return moves

  def getPawnMoves(self, r, c, moves):
    piecePinned = False
    pinDirection = ()
    for i in range(len(self.pins) -1, -1, -1):
      if self.pins[i][0] == r and self.pins[i][1] == c:
        piecePinned = True
        pinDirection = (self.pins[i][2], self.pins[i][3])
        self.pins.remove(self.pins[i])
        break

    if self.whiteToMove:
      moveAmount = -1
      startRow = 6
      enemyColour = "b"
      kingRow, kingCol = self.whiteKingLocation
    else:
      moveAmount = 1
      startRow = 1
      enemyColour = "w"
      kingRow, kingCol = self.blackKingLocation

    if self.board[r + moveAmount][c] == "--":
      if not piecePinned or pinDirection == (moveAmount, 0):
        moves.append(Move((r, c), (r + moveAmount, c), self.board))
        if r == startRow and self.board[r + (2 * moveAmount)][c] == "--":
          moves.append(Move((r, c), (r + (2 * moveAmount), c), self.board))
    if c-1 >= 0:
      if not piecePinned or pinDirection == (moveAmount, -1):
        if self.board[r + moveAmount][c - 1][0] == enemyColour:
          moves.append(Move((r, c), (r + moveAmount, c - 1), self.board))
        if (r + moveAmount, c - 1) == self.enPassantPossible:
          attackingPiece = blockingPiece = False
          if kingRow == r:
            if kingCol < c:
              insideRange = range(kingCol + 1, c - 1)
              outsideRange = range(c + 1, 8)
            else:
              insideRange = range(kingCol - 1, c, -1)
              outsideRange = range(c - 2, -1, -1)
            for i in insideRange:
              if self.board[r][i] != "--":
                blockingPiece = True
            for i in outsideRange:
              square = self.board[r][i]
              if square[0] == enemyColour and square[1] == "Q" or square[1] == "Q":
                attackingPiece = True
              elif square[1] != "--":
                blockingPiece = True
          if not attackingPiece or blockingPiece:
            moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, enPassant = True))
    if c+1 <= 7:
      if not piecePinned or pinDirection == (moveAmount, 1):
        if self.board[r + moveAmount][c + 1][0] == enemyColour:
          moves.append(Move((r, c), (r + moveAmount, c + 1), self.board))
        if (r + moveAmount, c + 1) == self.enPassantPossible:
          attackingPiece = blockingPiece = False
          if kingRow == r:
            if kingCol < c:
              insideRange = range(kingCol + 1, c)
              outsideRange = range(c + 2, 8)
            else:
              insideRange = range(kingCol - 1, c + 1, -1)
              outsideRange = range(c - 1, -1, -1)
            for i in insideRange:
              if self.board[r][i] != "--":
                blockingPiece = True
            for i in outsideRange:
              square = self.board[r][i]
              if square[0] == enemyColour and square[1] == "Q" or square[1] == "Q":
                attackingPiece = True
              elif square[1] != "--":
                blockingPiece = True
          if not attackingPiece or blockingPiece:
            moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, enPassant = True))
  
  def getKnightMoves(self, r, c, moves):
    piecePinned = False
    for i in range(len(self.pins) -1, -1, -1):
      if self.pins[i][0] == r and self.pins[i][1] == c:
        piecePinned = True
        self.pins.remove(self.pins[i])
        break

    knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
    allyColour = "w" if self.whiteToMove else "b"
    for m in knightMoves:
      endRow = r + m[0]
      endCol = c + m[1]
      if 0 <= endRow < 8 and 0 <= endCol < 8:
        if not piecePinned:
          endPiece = self.board[endRow][endCol]
          if endPiece[0] != allyColour:
            moves.append(Move((r, c), (endRow, endCol), self.board))

  def getRookMoves(self, r, c, moves):
    piecePinned = False
    pinDirection = ()
    for i in range(len(self.pins) -1, -1, -1):
      if self.pins[i][0] == r and self.pins[i][1] == c:
        piecePinned = True
        pinDirection = (self.pins[i][2], self.pins[i][3])
        if self.board[r][c][1] != "Q":
          self.pins.remove(self.pins[i])
        break

    directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
    enemyColour = "b" if self.whiteToMove else "w"
    for d in directions:
      for i in range(1, 8):
        endRow = r + d[0] * i
        endCol = c + d[1] * i
        if 0 <= endRow < 8 and 0 <= endCol < 8:
          if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
            endPiece = self.board[endRow][endCol]
            if endPiece == "--":
              moves.append(Move((r, c), (endRow, endCol), self.board))
            elif endPiece[0] == enemyColour:
              moves.append(Move((r, c), (endRow, endCol), self.board))
              break
            else:
              break
        else:
          break

  def getBishopMoves(self, r, c, moves):
    piecePinned = False
    pinDirection = ()
    for i in range(len(self.pins) -1, -1, -1):
      if self.pins[i][0] == r and self.pins[i][1] == c:
        piecePinned = True
        pinDirection = (self.pins[i][2], self.pins[i][3])
        self.pins.remove(self.pins[i])
        break

    directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
    enemyColour = "b" if self.whiteToMove else "w"
    for d in directions:
      for i in range(1, 8):
        endRow = r + d[0] * i
        endCol = c + d[1] * i
        if 0 <= endRow < 8 and 0 <= endCol < 8:
          if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
            endPiece = self.board[endRow][endCol]
            if endPiece == "--":
              moves.append(Move((r, c), (endRow, endCol), self.board))
            elif endPiece[0] == enemyColour:
              moves.append(Move((r, c), (endRow, endCol), self.board))
              break
            else:
              break
        else:
          break

  def getQueenMoves(self, r, c, moves):
    self.getRookMoves(r, c, moves)
    self.getBishopMoves(r, c, moves)

  def getKingMoves(self, r, c, moves):
    kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
    allyColour = "w" if self.whiteToMove else "b"
    for i in range(8):
      endRow = r + kingMoves[i][0]
      endCol = c + kingMoves[i][1]
      if 0 <= endRow < 8 and 0 <= endCol < 8:
        endPiece = self.board[endRow][endCol]
        if endPiece[0] != allyColour:
          if allyColour == "w":
            self.whiteKingLocation = (endRow, endCol)
          else:
            self.blackKingLocation = (endRow, endCol)
          inCheck, pins, checks = self.checkForPinsAndChecks()
          if not inCheck:
            moves.append(Move((r, c), (endRow, endCol), self.board))
          if allyColour == "w":
            self.whiteKingLocation = (r, c)
          else:
            self.blackKingLocation = (r, c)
    self.getCastleMoves(r, c, moves, allyColour)

  def getCastleMoves(self, r, c, moves, allyColour):
    if self.squareUnderAttack(r, c, allyColour):
      return
    if (self.whiteToMove and self.currentCastlingRight.wks) or ( not self.whiteToMove and self.currentCastlingRight.bks):
      self.getKingsideCastleMoves(r, c, moves, allyColour)
    if (self.whiteToMove and self.currentCastlingRight.wqs) or ( not self.whiteToMove and self.currentCastlingRight.bqs):
      self.getQueensideCastleMoves(r, c, moves, allyColour)

  def getKingsideCastleMoves(self, r, c, moves, allyColour):
    if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
      if not self.squareUnderAttack(r, c + 1, allyColour) and not self.squareUnderAttack(r, c + 2, allyColour):
        moves.append(Move((r, c), (r, c + 2), self.board, castle = True))

  def getQueensideCastleMoves(self, r, c, moves, allyColour):
    if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
      if not self.squareUnderAttack(r, c - 1, allyColour) and not self.squareUnderAttack(r, c - 2, allyColour):
        moves.append(Move((r, c), (r, c - 2), self.board, castle = True))

  def squareUnderAttack(self, r, c, allyColour):
    enemyColour = "w" if allyColour == "b" else "b"
    directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
    for j in range(len(directions)):
      d = directions[j]
      for i in range(1, 8):
        endRow = r + d[0] * i
        endCol = c + d[1] * i
        if 0 <= endRow < 8 and 0 <= endCol < 8:
          endPiece = self.board[endRow][endCol]
          if endPiece[0] == allyColour:
            break
          elif endPiece[0] == enemyColour:
            type = endPiece[1]
            if (0 <= j <= 3 and type == "R") or \
              (4 <= j <= 7 and type == "B") or \
              (i == 1 and type == "p" and ((enemyColour == "w" and 6 <= j <= 7) or (enemyColour == "b" and 4 <= j <= 5))) or \
              (type == "Q") or (i == 1 and type == "K"):
              return True
            else:
              break
        else:
          break
    knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
    for m in knightMoves:
      endRow = r + m[0]
      endCol = c + m[1]
      if 0 <= endRow < 8 and 0 <= endCol < 8:
        endPiece = self.board[endRow][endCol]
        if endPiece[0] == enemyColour and endPiece[1] == "N":
          return True
    return False

  def checkForPinsAndChecks(self):
    pins = []
    checks = []
    inCheck = False
    if self.whiteToMove:
      enemyColour = "b"
      allyColour = "w"
      startRow = self.whiteKingLocation[0]
      startCol = self.whiteKingLocation[1]
    else:
      enemyColour = "w"
      allyColour = "b"
      startRow = self.blackKingLocation[0]
      startCol = self.blackKingLocation[1]
    directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
    for j in range(len(directions)):
      d = directions[j]
      possiblePin = ()
      for i in range(1, 8):
        endRow = startRow + d[0] * i
        endCol = startCol + d[1] * i
        if 0 <= endRow < 8 and 0 <= endCol < 8:
          endPiece = self.board[endRow][endCol]
          if endPiece[0] == allyColour and endPiece != "K":
            if possiblePin == ():
              possiblePin = (endRow, endCol, d[0], d[1])
            else:
              break
          elif endPiece[0] == enemyColour:
            type = endPiece[1]
            if (0 <= j <= 3 and type == "R") or \
              (4 <= j <= 7 and type == "B") or \
              (i == 1 and type == "p" and ((enemyColour == "w" and 6 <= j <= 7) or (enemyColour == "b" and 4 <= j <= 5))) or \
              (type == "Q") or (i == 1 and type == "K"):
              if possiblePin == ():
                inCheck = True
                checks.append((endRow, endCol, d[0], d[1]))
                break
              else:
                pins.append(possiblePin)
                break
            else:
              break
        else:
          break
    knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
    for m in knightMoves:
      endRow = startRow + m[0]
      endCol = startCol + m[1]
      if 0 <= endRow < 8 and 0 <= endCol < 8:
        endPiece = self.board[endRow][endCol]
        if endPiece[0] == enemyColour and endPiece[1] == "N":
          inCheck =True
          checks.append((endRow, endCol, m[0], m[1]))
    return inCheck, pins, checks

class CastleRights():
  def __init__(self, wks, bks, wqs, bqs):
    self.wks = wks
    self.bks = bks
    self.wqs = wqs
    self.bqs = bqs      

class Move():

  ranksToRows = {"1" : 7, "2" : 6, "3" : 5, "4" : 4, "5" : 3, "6" : 2, "7" : 1, "8" : 0}
  rowsToRanks = {v: k for k, v in ranksToRows.items()}
  filesToCols = {"a" : 0, "b" : 1, "c" : 2, "d" : 3, "e" : 4, "f" : 5, "g" : 6, "h" : 7}
  colsToFiles = {v: k for k, v in filesToCols.items()}

  def __init__(self, startSq, endSq, board, enPassant = False, castle = False):
    self.startRow = startSq[0]
    self.startCol = startSq[1]
    self.endRow = endSq[0]
    self.endCol = endSq[1]
    self.pieceMoved = board[self.startRow][self.startCol]
    self.pieceCaptured = board[self.endRow][self.endCol]
    self.castle = castle

    self.pawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7)

    self.enPassant = enPassant
    if enPassant:
      self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"
    
    self.isCapture = self.pieceCaptured != "--"

    self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

  def __eq__(self, other):
    if isinstance(other, Move):
      return self.moveID == other.moveID
    return False

  def getChessNotation(self):
    return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

  def getRankFile(self, r, c):
    return self.colsToFiles[c] + self.rowsToRanks[r]
  
  def __str__(self):
    if self.castle:
      return "O-O" if self.endCol == 6 else "O-O-O"
    
    endSquare = self.getRankFile(self.endRow, self.endCol)
    if self.pieceMoved[1] == "p":
      if self.isCapture:
        if self.enPassant:
          return self.colsToFiles[self.startCol] + "x" + endSquare + " e.p."
        return self.colsToFiles[self.startCol] + "x" + endSquare
      else:
        return endSquare

    moveString = self.pieceMoved[1]
    if self.isCapture:
      moveString += "x"
    return moveString + endSquare
