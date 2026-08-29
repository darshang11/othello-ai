from OthelloState import OthelloState
from OthelloState import Piece
from OthelloState import GameType
import time

class OthelloLog:

	def __init__(self, gameType):
		self.moveLog = []
		self.gameType = gameType
		self.winner = "Tie"
		self.black = 0
		self.white = 0
		self.endCondition = ""
		self.startTime = time.time() 

	def addMove(self, move):
		self.moveLog.append(move)

	def __str__(self):
		return (f"Start Time: {self.startTime}\n"
			   f"Game Kind: {self.gameType}\n"
			   f"Score: {self.black}B - {self.white}W\n"
			   f"Winner: {self.winner}\n"
			   f"Moves: {str(self.moveLog)}\n"
			   f"End Condition: {self.endCondition}")

