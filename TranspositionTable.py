import numpy as np


class TranspositionTable:

    def __init__(self, size):

        self.size = size
        self.entries = np.empty([self.size, 4])
  
    def indexKey(self, zobristKey):
        return (np.uint(zobristKey % self.size))

    def getStoredMove(self, zobristKey):
        return self.entries[self.indexKey(zobristKey)][3]
    
    def storeEval(self, zobristKey, evalValue, depth, bestMove):
        self.entries[self.indexKey(zobristKey)] = np.array([zobristKey, evalValue, depth, bestMove])

    def lookupEval(self, zobristKey, depth):
        
        self.lookupEntry = self.entries[self.indexKey(zobristKey)]
        
        if self.lookupEntry[0] == zobristKey:
            
            if self.lookupEntry[2] >= depth:
                return self.lookupEntry[1]
            
        return False
    
tt = TranspositionTable(64000)