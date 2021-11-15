import numpy as np
import os.path

class ZobristKey:
    
    PieceTypeIndexConversion = {"K": 0, "p" : 1, "N" : 2, "B" : 3, "R" : 4, "Q" : 5 }

    def __init__(self):
        
        self.pieceTypeIndexConversion = {"K": 0, "p" : 1, "N" : 2, "B" : 3, "R" : 4, "Q" : 5 }
        self.seed = np.random.seed(2361912)
        self.randomNumbersFileName = "RandomNumbers.txt"
        self.piecesArray = np.empty([6, 2, 64], dtype = np.uint64)
        self.castlingRights = np.empty([16], dtype = np.uint64)
        self.enPassantFile = np.empty([8], dtype = np.uint64)
        self.sideToMove = np.uint64(0)
        

    def writeRandomNumbers(self):
        self.randomNumberString = ""
        self.numRandomNumbers = (64 * 6 * 2) + 16 + 8 + 1

        for i in range(self.numRandomNumbers):
            i += 1
            self.randomNumberString += str(self.randomUnsigned64BitInteger())
            if i != self.numRandomNumbers:
                self.randomNumberString += ","

            with open(self.randomNumbersFileName, "w") as file:
                file.write(self.randomNumberString)

    def readRandomNumbers(self):
        if not os.path.isfile(self.randomNumbersFileName):
            print("Creating File and Numbers...")
            self.writeRandomNumbers()
            print("Done!")

        with open(self.randomNumbersFileName, "r") as file:
            self.randomNumbers = file.read()
        
        self.randomNumbers = self.randomNumbers.split(",")
            
        return self.randomNumbers

    
    def Zobrist(self):
        
        self.ZobristNumbers = self.readRandomNumbers()

        for square in range(64):
            for pieceIndex in range(6):
                self.piecesArray[pieceIndex, 0, square] = self.ZobristNumbers.pop()
                self.piecesArray[pieceIndex, 1, square] = self.ZobristNumbers.pop()

        for right in range(16):
            self.castlingRights[right] = self.ZobristNumbers.pop()
            
        for file in range(8):
            self.enPassantFile[file] = self.ZobristNumbers.pop()       

        self.sideToMove = np.uint64(self.ZobristNumbers.pop())

    def CalculateZobristKey(self, gs):

        self.ZobristKey = np.uint64(0)
        self.board = gs.board

        for rank in range(len(self.board)):
            for file in range(len(self.board)):
                if self.board[rank][file] != "--":
                    self.squareCount = (file + (rank * 8))
                    self.pieceType = self.PieceTypeIndexConversion[self.board[rank][file][1]]
                    self.pieceColour = 0 if self.board[rank][file][0] == "w" else 1
                    
                    self.ZobristKey = np.bitwise_xor(self.ZobristKey, self.piecesArray[self.pieceType, self.pieceColour, self.squareCount])   
        
        self.enPassantIndex = gs.enPassantPossible
        if self.enPassantIndex != ():
            self.ZobristKey = np.bitwise_xor(self.ZobristKey, self.enPassantFile[self.enPassantIndex[1]])

        self.listOfCastlingRights = gs.currentCastlingRight
        self.castleRightsIndex = 0
        self.castleRightsIndex += 1 if self.listOfCastlingRights.wks else 0 
        self.castleRightsIndex += 2 if self.listOfCastlingRights.bks else 0 
        self.castleRightsIndex += 4 if self.listOfCastlingRights.wqs else 0 
        self.castleRightsIndex += 8 if self.listOfCastlingRights.bqs else 0 

        self.ZobristKey = np.bitwise_xor(self.ZobristKey,self.castlingRights[self.castleRightsIndex])  
        
        self.whiteToMove = gs.whiteToMove
        if self.whiteToMove:
            self.ZobristKey = np.bitwise_xor(self.ZobristKey, self.sideToMove)
        
        print(self.ZobristKey)
        
        return self.ZobristKey

    def randomUnsigned64BitInteger(self):
        self.random64BitInteger = np.random.randint(0, 18446744073709551615, dtype = np.uint64)
        return self.random64BitInteger
