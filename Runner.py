from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame as p
import Engine
import ChessAI as AI
from multiprocessing import Process, Queue
import time

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQSIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

def loadImages():
  pieces = ['wp', 'bp', 'wN', 'bN', 'wB', 'bB', 'wR', 'bR', 'wQ', 'bQ', 'wK', 'bK']
  for piece in pieces:
    IMAGES[piece] = p.transform.scale(p.image.load("ImagePieces/" + piece + ".png"), (SQSIZE, SQSIZE))

def main():
  p.init()
  screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
  clock = p.time.Clock()
  screen.fill(p.Color("white"))
  moveLogFont = p.font.SysFont("Arial", 14, False, False)
  gs = Engine.GameState()
  validMoves = gs.getValidMoves()
  moveMade = False 
  animate = False
  loadImages()
  running = True
  sqSelected = ()
  playerClicks = []
  gameOver = False
  playerOne = True
  playerTwo = False
  AIThinking =False
  moveFinderProcess = None
  moveUndone = False

  while running:
    humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
    for e in p.event.get():
      if e.type == p.QUIT:
        running = False
      elif e.type == p.MOUSEBUTTONDOWN:
        if not gameOver:
          location = p.mouse.get_pos()
          col = location[0]//SQSIZE
          row = location[1]//SQSIZE
          if sqSelected == (row, col) or col >= 8:
            sqSelected = ()
            playerClicks = []
          else:
            sqSelected = (row, col)
            playerClicks.append(sqSelected)
          if len(playerClicks) == 2 and humanTurn:
            move = Engine.Move(playerClicks[0], playerClicks[1], gs.board)
            print(move.getChessNotation())
            for i in range(len(validMoves)):
              if move == validMoves[i]:
                gs.makeMove(validMoves[i])
                moveMade = True
                animate = True
                sqSelected = ()
                playerClicks = []
            if not moveMade:
              playerClicks = [sqSelected]
      elif e.type == p.KEYDOWN:
        if e.key == p.K_z:
          gs.undoMove()
          sqSelected = ()
          playerClicks = []
          moveMade = True
          animate = False
          gameOver = False
          if AIThinking:
            moveFinderProcess.terminate()
            AIThinking = False
          moveUndone = True
        if e.key == p.K_r:
          gs = Engine.GameState()
          validMoves = gs.getValidMoves()
          sqSelected = ()
          playerClicks = []
          moveMade = False
          animate = False
          gameOver = False
          if AIThinking:
            moveFinderProcess.terminate()
            AIThinking = False
          moveUndone = True

    if not gameOver and not humanTurn and not moveUndone:
      if not AIThinking:
        AIThinking = True
        print("Thinking...")
        start = time.perf_counter()
        returnQueue = Queue()
        moveFinderProcess = Process(target=AI.findBestestMove, args=(gs, validMoves, returnQueue))
        moveFinderProcess.start()
      if not moveFinderProcess.is_alive():
        stop = time.perf_counter()
        print(f"Done Thinking in {stop - start:0.4f} seconds!")
        AIMove = returnQueue.get()
        gs.makeMove(AIMove)
        moveMade = True
        animate = True
        AIThinking = False

    if moveMade:
      if animate:
        animateMove(gs.moveLog[-1], screen, gs.board, clock)
      validMoves = gs.getValidMoves()
      moveMade = False
      animate = False
      moveUndone = False

    drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)

    if gs.checkmate or gs.stalemate:
      gameOver = True
      drawEndGameText(screen, text = "Draw by statemate" if gs.stalemate else "Black wins by checkmate" if gs.whiteToMove else "White wins by checkmate")

    clock.tick(MAX_FPS)
    p.display.flip()

def drawBoard(screen):
  global colours
  colours = [p.Color("white"), p.Color("gray")]
  for r in range(DIMENSION):
    for c in range(DIMENSION):
      colour = colours[((r + c) % 2)]
      p.draw.rect(screen, colour, p.Rect(c*SQSIZE, r*SQSIZE, SQSIZE, SQSIZE))

def highlightSquares(screen, gs, validMoves, sqSelected):
  if sqSelected != ():
    r, c = sqSelected
    if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):
      s = p.Surface((SQSIZE, SQSIZE))
      s.set_alpha(100)
      s.fill(p.Color('blue'))
      screen.blit(s,  (c*SQSIZE, r*SQSIZE))
      s.fill(p.Color('yellow'))
      for move in validMoves:
        if move.startRow == r and move.startCol == c:
          screen.blit(s, (move.endCol*SQSIZE, move.endRow*SQSIZE))

def drawPieces(screen, board):
  for r in range(DIMENSION):
    for c in range(DIMENSION):
      piece = board[r][c]
      if piece != "--":
        screen.blit(IMAGES[piece], p.Rect(c*SQSIZE, r*SQSIZE, SQSIZE, SQSIZE))

def drawMoveLog(screen, gs, font):
  moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
  p.draw.rect(screen, p.Color("black"), moveLogRect)
  moveLog = gs.moveLog
  moveTexts = []
  for i in range(0, len(moveLog), 2):
    moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " "
    if i + 1 < len(moveLog):
      moveString += str(moveLog[i + 1]) + "  "
    moveTexts.append(moveString)

  movesPerRow = 3
  padding = 5
  lineSpacing = 2
  textY = padding
  for i in range(0, len(moveTexts), movesPerRow):
    text = ""
    for j in range(movesPerRow):
      if i + j < len(moveTexts):
        text += moveTexts[i + j]
    textObject = font.render(text, True, p.Color('white'))
    textLocation = moveLogRect.move(padding, textY)
    screen.blit(textObject, textLocation)
    textY += textObject.get_height() + lineSpacing

def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
  drawBoard(screen)
  highlightSquares(screen, gs, validMoves, sqSelected)
  drawPieces(screen, gs.board)
  drawMoveLog(screen, gs, moveLogFont)

def animateMove(move, screen, board, clock):
  global colours
  dR = move.endRow - move.startRow
  dC = move.endCol - move.startCol
  framesPerSquare = 10
  frameCount = (abs(dR) + abs(dC)) * framesPerSquare
  for frame in range(frameCount + 1):
    r, c = ((move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount))
    drawBoard(screen)
    drawPieces(screen, board)
    colour = colours[(move.endRow + move.endCol) % 2]
    endSquare = p.Rect(move.endCol*SQSIZE, move.endRow*SQSIZE, SQSIZE, SQSIZE)
    p.draw.rect(screen, colour, endSquare)
    if move.pieceCaptured != "--":
      if move.enPassant:
        enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == "b" else move.endRow - 1
        endSquare = p.Rect(move.endCol*SQSIZE, enPassantRow*SQSIZE, SQSIZE, SQSIZE)
      screen.blit(IMAGES[move.pieceCaptured], endSquare)
    screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQSIZE, r*SQSIZE, SQSIZE, SQSIZE))
    p.display.flip()
    clock.tick(60)

def drawEndGameText(screen, text):
  font = p.font.SysFont("Helvitca", 32, True, False)
  textObject = font.render(text, 0, p.Color('Black'))
  textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH/2 - textObject.get_width()/2, BOARD_HEIGHT/2 - textObject.get_height()/2)
  screen.blit(textObject, textLocation)



if __name__ == '__main__':
  main()
  input()