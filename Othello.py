# import the pygame module, so you can use it
import pygame
import time
from datetime import datetime
from sys import platform
import os
from OthelloLog import OthelloLog
from OthelloState import OthelloState
from OthelloState import Piece
from OthelloState import GameType
from Player import Player
from Agent import Agent
from SpareAgent import SpareAgent
from copy import deepcopy


 
NUM_COLS = 8
NUM_ROWS = 8
SQUARE_WIDTH = 100
SQUARE_BUFFER = 3

BACKGROUND_COLOR = (36, 163, 57)

#measured in ms
MAX_MOVE_TIME = 5000

def main():
     
    pygame.init()

    gameType = playerSelect()
    match gameType:
        case GameType.PVP:
            log = OthelloLog(GameType.PVP)
            agentA = Player()
            agentB = Player()

        case GameType.AVP:
            log = OthelloLog(GameType.AVP)
            agentA = Agent()
            agentB = Player()

        case GameType.PVA:
            log = OthelloLog(GameType.PVA)
            agentA = Player()
            agentB = Agent()

        case GameType.AVA:
            log = OthelloLog(GameType.AVA)
            agentA = Agent()
            agentB = SpareAgent()


    screen = pygame.display.set_mode((SQUARE_WIDTH * NUM_COLS, 
                                      SQUARE_WIDTH * NUM_ROWS))

    state = OthelloState(numCols = NUM_COLS, numRows = NUM_ROWS, 
                         squareWidth = SQUARE_WIDTH, squareBuffer = SQUARE_BUFFER) 
    state.draw(screen)
    pygame.display.update()

    running = True
    gameOver = False
    curPlayer = agentA
    while running:

        while (not gameOver):

            if(type(curPlayer) is Agent or type(curPlayer) is SpareAgent):

                stateCopy = deepcopy(state)
                startTime = round(time.time()*1000)
                move = curPlayer.getNextMove(stateCopy)
                endTime = round(time.time()*1000)

                if(endTime - startTime > MAX_MOVE_TIME):

                    
                    if(state.nextMove == Piece.RED):
                        log.winner = Piece.YELLOW
                    else:
                        log.winner = Piece.RED
                    
                    log.endCondition = "Timeout"
                    running = False
                    gameOver = True

                else:
                    try:
                        log.addMove(move)
                        state.placePiece(move[0], move[1])
                        
                    except:
                        log.endCondition = "Placement Error"
                        running = False
                        gameOver = True



            elif (type(curPlayer) is Player):

                playerHasMoved = False
                while(not playerHasMoved):
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            gameOver = True
                            playerHasMoved = True
                            log.endCondition = "Player Interupt"
                            break

                        elif (event.type == pygame.MOUSEBUTTONDOWN):
                            clickPos = pygame.mouse.get_pos()
                            col = getClickCol(clickPos)
                            row = getClickRow(clickPos)
                            if(state.isValidMove(col, row, state.nextMove)):
                                log.addMove((col, row))
                                state.placePiece(col, row)
                                playerHasMoved = True
                            else:
                                print(f"Move at ({col}, {row}) is not valid")
                            


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False


            state.draw(screen)
            pygame.display.update()
            
            
            if(not state.skipped):
                if(curPlayer == agentA):
                    curPlayer = agentB
                else:
                    curPlayer = agentA


            if(not state.existsNextMove()):
                    gameOver = True
                    scores = state.pieceCounts()
                    log.black = scores[0]
                    log.white = scores[1]
                    log.endCondition = "Game finish"
                    if(scores[0] > scores[1]):
                        log.winner = "Black"
                    elif(scores[1] > scores[0]):
                        log.winner = "White"
                    else:
                        log.winner = "Tie"
                    
                    print(f"Game over! Winner: {log.winner} | Score: {scores[0]}B - {scores[1]}W")


        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

    writeLogToOS(log)

def writeLogToOS(log):

    if not os.path.exists("logs"):
        os.makedirs("logs")

    if(platform == "win32"):
        with open(f"logs\\{datetime.now()}.log", "w") as logFile:
            logFile.write(str(log))
    else:
        with open(f"logs/{datetime.now()}.log", "w") as logFile:
            logFile.write(str(log))


def playerSelect():
    #chock full of magic numbers and other sins
    #but what can ya do
    screen = pygame.display.set_mode((500, 650))
    font = pygame.font.SysFont('Corbel', 35)

    screen.fill(BACKGROUND_COLOR)



    pygame.draw.rect(screen, (128, 128, 128), (100, 50, 300, 100))
    PVPButton = font.render('Player vs. Player' , True , (255, 255, 255))
    PVPButtonRect = PVPButton.get_rect(center=(250, 100))
    screen.blit(PVPButton , PVPButtonRect)

    pygame.draw.rect(screen, (128, 128, 128), (100, 200, 300, 100))
    PVAButton = font.render('Player vs. Agent' , True , (255, 255, 255))
    PVAButtonRect = PVPButton.get_rect(center=(250, 250))
    screen.blit(PVAButton , PVAButtonRect)

    pygame.draw.rect(screen, (128, 128, 128), (100, 350, 300, 100))
    AVPButton = font.render('Agent vs. Player' , True , (255, 255, 255))
    AVPButtonRect = PVPButton.get_rect(center=(250, 400))
    screen.blit(AVPButton , AVPButtonRect)

    pygame.draw.rect(screen, (128, 128, 128), (100, 500, 300, 100))
    AVAButton = font.render('Agent vs. Agent' , True , (255, 255, 255))
    AVAButtonRect = PVPButton.get_rect(center=(250, 550))
    screen.blit(AVAButton , AVAButtonRect)

    pygame.display.update()

    setup = True
    while setup:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                setup = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                clickPos = pygame.mouse.get_pos()
                response = getClickButtonSetup(clickPos)
                if(response != None):
                    return response
                

def getClickButtonSetup(clickPos):
    #also full of magic numbers
    if(clickPos[0] >= 100 and clickPos[0] <= 400):
        if(clickPos[1] >= 50 and clickPos[1] <= 150):
            return GameType.PVP
        elif(clickPos[1] >= 200 and clickPos[1] <= 300):
            return GameType.PVA
        elif(clickPos[1] >= 350 and clickPos[1] <= 450):
            return GameType.AVP
        elif(clickPos[1] >= 500 and clickPos[1] <= 600):
            return GameType.AVA

    return None



def getClickCol(clickPos):

    for i in range(NUM_COLS):
        if (clickPos[0] < (i + 1) * SQUARE_WIDTH):
            return i

def getClickRow(clickPos):

    for i in range(NUM_ROWS):
        if (clickPos[1] < (i + 1) * SQUARE_WIDTH):
            return i


if __name__=="__main__":
    main()