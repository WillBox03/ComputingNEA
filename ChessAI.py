import random
import numpy as np

pieceValues = {"p": 100, "N": 300, "B": 300, "R": 500, "Q": 900, "K": 0}
CHECKMATE = 10000
STALEMATE = 0

pawnSquareTable = np.array([
    [0,  0,  0,  0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50, 50, 50,50],
    [10, 10, 20, 30, 30, 20, 10,10],
    [5,  5, 10, 25, 25, 10,  5,  5],
    [0,  0,  0, 20, 20,  0,  0,  0],
    [5, -5,-10,  0,  0,-10, -5,  5],
    [5, 10, 10,-20,-20, 10, 10,  5],
    [0,  0,  0,  0,  0,  0,  0,  0]
    ])


knightSquareTable = np.array([
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  0, 10, 15, 15, 10,  0,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  0, 15, 20, 20, 15,  0,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
])

bishopSquareTable = np.array([
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5, 10, 10,  5,  0,-10],
    [-10,  5,  5, 10, 10,  5,  5,-10],
    [-10,  0, 10, 10, 10, 10,  0,-10],
    [-10, 10, 10, 10, 10, 10, 10,-10],
    [-10,  5,  0,  0,  0,  0,  5,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20]
])

rookSquareTable = np.array([
    [0,  0,  0,  0,  0,  0,  0,  0],
    [5, 10, 10, 10, 10, 10, 10,  5],
    [-5,  0,  0,  0,  0,  0,  0,-5],
    [-5,  0,  0,  0,  0,  0,  0,-5],
    [-5,  0,  0,  0,  0,  0,  0,-5],
    [-5,  0,  0,  0,  0,  0,  0,-5],
    [-5,  0,  0,  0,  0,  0,  0,-5],
    [0,  0,  0,  5,  5,  0,  0,  0]
])

queenSquareTable = np.array([
    [-20,-10,-10, -5, -5,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [ -5,  0,  5,  5,  5,  5,  0, -5],
    [  0,  0,  5,  5,  5,  5,  0, -5],
    [-10,  5,  5,  5,  5,  5,  0,-10],
    [-10,  0,  5,  0,  0,  0,  0,-10],
    [-20,-10,-10, -5, -5,-10,-10,-20]
])

kingSqaureTable = np.array([
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [ 20, 20,  0,  0,  0,  0, 20, 20],
    [ 20, 30, 10,  0,  0, 10, 30, 20]
])


pieceSquareTables = {"wp" : pawnSquareTable, "bp" : np.flip(pawnSquareTable), "wN" : knightSquareTable,
 "bN": np.flip(knightSquareTable), "wB" : bishopSquareTable, "bB" : np.flip(bishopSquareTable), 
 "wR" : rookSquareTable, "bR" : np.flip(rookSquareTable),  "wQ" : queenSquareTable, "bQ" : np.flip(queenSquareTable), 
 "wK" : kingSqaureTable, "bK" : np.flip(kingSqaureTable)}

def findRandomMove(gs, validMoves, returnQueue):
    nextMove = validMoves[random.randint(0, len(validMoves) - 1)]
    returnQueue.put(nextMove)

def calculateBoardValue(gs, board):
    boardValue = 0
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] != "--":
                if board[i][j][0] == "w":
                    boardValue += pieceValues[board[i][j][1]]
                    boardValue += pieceSquareTables[board[i][j]][i][j]
                else:
                    boardValue -= pieceValues[board[i][j][1]]
                    boardValue -= pieceSquareTables[board[i][j]][i][j]

    return boardValue

def findBestestMove(gs, validMoves, returnQueue):
    Depth = 4
    CurrentDepth = 0
    Max = -CHECKMATE
    Min = CHECKMATE

    '''if gs.whiteToMove:
        returnQueue.put(minimax(gs, Depth, True, Max, Min)[1])
    else:
        returnQueue.put(minimax(gs, Depth, False, Max, Min)[1])'''

    if gs.whiteToMove:
        returnQueue.put(maxestValue(gs, Depth, CurrentDepth, Max, Min)[1])
    else:
        returnQueue.put(minestValue(gs, Depth, CurrentDepth, Max, Min)[1])

def minimax(gs, depth, maximizing, alpha, beta):
    if depth == 0:
        return calculateBoardValue(gs, gs.board), None

    move = None
    highestValue = -CHECKMATE if maximizing else CHECKMATE
    moves = orderMoves(gs.getValidMoves())
    for currentMove in moves:
        gs.makeMove(currentMove)
        if gs.checkmate:
            tempValue = CHECKMATE if maximizing else -CHECKMATE
            return tempValue, currentMove
        elif gs.stalemate:
            tempValue = STALEMATE
            return tempValue, currentMove
        else:
            tempValue = minimax(gs, depth - 1, not maximizing, alpha, beta)[0]
            if maximizing:
                alpha = max(alpha, tempValue)
            else:
                beta = min(beta, tempValue)
        if (tempValue > highestValue and maximizing) or (tempValue < highestValue and not maximizing):
            highestValue = tempValue
            move = currentMove
        gs.undoMove()
        if alpha >= beta:
            break
    return highestValue, move

def orderMoves(moves):
    moveScores = []
    for currentMove in moves:
        tempScore = 0
        if currentMove.isCapture:
            tempScore += 10 * pieceValues[currentMove.pieceCaptured[1]] - pieceValues[currentMove.pieceMoved[1]]
        moveScores.append(tempScore)
    for j in range(len(moves) - 1):
        for k in range(len(moves) - j - 1, 0, -1):
            swapIndex = k - 1
            if moveScores[swapIndex] < moveScores[k]:
                moves[k], moves[swapIndex] = moves[swapIndex], moves[k]
                moveScores[k], moveScores[swapIndex] = moveScores[swapIndex], moveScores[k]
    #print(moveScores)
    return moves




def maxestValue(gs, Depth, CurrentDepth, Max, Min):
    if Depth != CurrentDepth:
        CurrentDepth += 1
        move = None
        highestValue = -CHECKMATE
        moves = orderMoves(gs.getValidMoves())
        for currentMove in moves:
            gs.makeMove(currentMove)
            #print(gs.board)
            if gs.checkmate:
                tempValue = CHECKMATE
                return tempValue, currentMove
            elif gs.stalemate:
                tempValue = STALEMATE
                return tempValue, currentMove
            else:
                tempValue = minestValue(gs, Depth, CurrentDepth, Max, Min)[0]
                Max = max(Max, tempValue)
            if tempValue > highestValue:
                highestValue = tempValue
                move = currentMove
            gs.undoMove()
            if Max >= Min:
                break
        #print(highestValue)
        return highestValue, move
    else:
        boardValue = calculateBoardValue(gs, gs.board)
        #print(boardValue)
        return boardValue, None


def minestValue(gs, Depth, CurrentDepth, Max, Min):
    if Depth != CurrentDepth:
        CurrentDepth += 1
        move = None
        highestValue = CHECKMATE
        moves = orderMoves(gs.getValidMoves())
        for currentMove in moves:
            gs.makeMove(currentMove)
            #print(gs.board)
            if gs.checkmate:
                tempValue = -CHECKMATE
                return tempValue, currentMove
            elif gs.stalemate:
                tempValue = STALEMATE
                return tempValue, currentMove
            else:
                tempValue = maxestValue(gs, Depth, CurrentDepth, Max, Min)[0]
                Min = min(Min, tempValue)
            if tempValue < highestValue:
                highestValue = tempValue
                move = currentMove
            gs.undoMove()
            if Max >= Min:
                break
        #print(highestValue)
        return highestValue, move
    else:
        boardValue = calculateBoardValue(gs, gs.board)
        #print(boardValue)
        return boardValue, None