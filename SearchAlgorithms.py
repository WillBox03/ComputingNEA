CHECKMATE = 1000
STALEMATE = 0



def findBestestMove(gs, validMoves, returnQueue):
    Depth = 4
    CurrentDepth = 0
    Max = -CHECKMATE
    Min = CHECKMATE

    if gs.whiteToMove:
        returnQueue.put(minimax(gs, Depth, True)[1])
    else:
        returnQueue.put(minimax(gs, Depth, False)[1])

    if gs.whiteToMove:
        returnQueue.put(minimaxabp(gs, Depth, True, Max, Min)[1])
    else:
        returnQueue.put(minimaxabp(gs, Depth, False, Max, Min)[1])

    if gs.whiteToMove:
        returnQueue.put(maxestValue(gs, Depth, CurrentDepth, Max, Min)[1])
    else:
        returnQueue.put(minestValue(gs, Depth, CurrentDepth, Max, Min)[1])
def minimax(gs, depth, maximizing):
    if depth == 0:
        return calculateBoardValue(gs, gs.board), None





def minimax(gs, depth, maximizing):
    if depth == 0:
        return calculateBoardValue(gs, gs.board), None

    move = None
    highestValue = -CHECKMATE if maximizing else CHECKMATE
    moves = gs.getValidMoves()
    for currentMove in moves:
        gs.makeMove(currentMove)
        if gs.checkmate:
            tempValue = CHECKMATE if maximizing else -CHECKMATE
            return tempValue, currentMove
        elif gs.stalemate:
            tempValue = STALEMATE
            return tempValue, currentMove
        else:
            tempValue = minimax(gs, depth - 1, not maximizing)[0]
        if (tempValue > highestValue and maximizing) or (tempValue < highestValue and not maximizing):
            highestValue = tempValue
            move = currentMove
        gs.undoMove()
    return highestValue, move

def minimaxabp(gs, depth, maximizing, alpha, beta):
    if depth == 0:
        return calculateBoardValue(gs, gs.board), None

    move = None
    highestValue = -CHECKMATE if maximizing else CHECKMATE
    moves = gs.getValidMoves()
    for currentMove in moves:
        gs.makeMove(currentMove)
        if gs.checkmate:
            tempValue = CHECKMATE if maximizing else -CHECKMATE
            return tempValue, currentMove
        elif gs.stalemate:
            tempValue = STALEMATE
            return tempValue, currentMove
        else:
            tempValue = minimaxabp(gs, depth - 1, not maximizing, alpha, beta)[0]
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

def maxestValue(gs, Depth, CurrentDepth, Max, Min):
    if Depth != CurrentDepth:
        CurrentDepth += 1
        move = None
        highestValue = -CHECKMATE
        moves = gs.getValidMoves()
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
        moves = gs.getValidMoves()
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
