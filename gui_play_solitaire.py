import random
import sys
import pygame
import time

def main():

    pygame.init()

    # Set window
    displayWidth = 800
    displayHeight = 725

    black = (0, 0, 0)
    green = (0, 128, 0)

    gameDisplay = pygame.display.set_mode((displayWidth, displayHeight))
    gameDisplay.fill(green)
    pygame.display.set_caption("Solitaire")
    gameDisplay.set_colorkey(black)

    Game(gameDisplay).main_loop()

    pygame.quit()
    sys.exit()


class Game:

    def __init__(self, gameDisplay):

        self.deck = CardDeck()
        self.gameDisplay = gameDisplay

        self.flop = [None, None, None]
        self.boardMatrix = self.initial_board_setup()
        self.selectedSlot = None

        self.startStack = None

        self.trash = []

    def main_loop(self):

        gameExit = False
        green = (0, 128, 0)

        while not gameExit:

            self.event_loop()
            self.gameDisplay.fill(green)
            self.board_render()
            gameExit = self.check_game_over()
            pygame.time.Clock().tick(60)

        self.win_sequence(green)

    def event_loop(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONUP:
                print event
                self.find_button_press_loci(event.pos)

    def find_button_press_loci(self, clickedPos):
        slotList = []
        for row in self.boardMatrix:
            for slot in row:
                if slot.rect.collidepoint(clickedPos):
                    slotList.append(slot)

        if slotList == []:
            return
        else:
            self.evaluate_board_slots_clicked(slotList)

    def evaluate_board_slots_clicked(self, slotList):

        if slotList[0].boardMatrixRow == 0:

            if slotList[0].newGame:
                self.reset_game()
                return

            if len(slotList) == 1 and not slotList[0].inFlop:
                boardSlot = slotList[0]
                if boardSlot.inDeck:
                    self.deselect_slot()
                    self.new_flop()
                    return

                elif boardSlot.inPile:
                    print "pile"
                    if self.selectedSlot == None:

                        if boardSlot.card != None:
                            self.update_selected_slot(boardSlot)

                        elif boardSlot.card == None:
                            return

                    else:
                        ##TODO test whether move is appropriate
                        properMove = self.check_move_validity(boardSlot)
                        if properMove:
                            print "proper move"
                            self.make_move(boardSlot)
                            self.deselect_slot()
                        else:
                            self.update_selected_slot(boardSlot)

                    return


            else:
                for boardSlot in slotList:
                    if boardSlot.flopPosition == 0:
                        print "flop"
                        self.update_selected_slot(boardSlot)
                        return

        ### Finally check for those slots that are in the rows
        else:
            boardSlot = self.find_appropriate_board_card(slotList)
            if boardSlot is None:
                return

            if self.selectedSlot != None:
                ##TODO test whether move is appropriate
                properMove = self.check_move_validity(boardSlot)
                if properMove:
                    print "THIS MOVE IS VALID"
                    self.make_move(boardSlot)
                    self.deselect_slot()
                else:
                    print "INVALID MOVE"
                    self.update_selected_slot(boardSlot)
            else:
                self.update_selected_slot(boardSlot)

    ## There must be a better way to do this...
    def reset_game(self):

        green = (0, 128, 0)
        self.gameDisplay.fill(green)

        self.deck = CardDeck()
        self.flop = [None, None, None]
        self.boardMatrix = self.initial_board_setup()
        self.selectedSlot = None
        self.startStack = None
        self.trash = []

    def make_move(self, destSlot):

        # Clean up the destination
        destRow = destSlot.boardMatrixRow
        destCol = destSlot.boardMatrixColumn
        if destSlot.inPile:
            self.boardMatrix[destRow][destCol].card = self.selectedSlot.card
            self.boardMatrix[destRow][destCol].hidden = False
            self.boardMatrix[destRow][destCol].covered = False

        else:
            allStartCards = [self.selectedSlot] + self.startStack
            if destSlot.card == None:
                destRow -= 1
            else:
                destSlot.covered = True

            for slotCard in allStartCards:
                destRow += 1
                self.boardMatrix[destRow][destCol].card = slotCard.card
                self.boardMatrix[destRow][destCol].covered = True
                self.boardMatrix[destRow][destCol].hidden = False
            self.boardMatrix[destRow][destCol].covered = False

        # Clean up the start
        startRow = self.selectedSlot.boardMatrixRow
        startCol = self.selectedSlot.boardMatrixColumn

        if self.selectedSlot.inPile:
            if self.selectedSlot.card.denom == "A":
                self.boardMatrix[startRow][startCol].card = None
                self.boardMatrix[startRow][startCol].hidden = True
                self.boardMatrix[startRow][startCol].covered = True

            else:
                suit = self.selectedSlot.card.suit
                newDenom = self.deck.cardOrder[self.deck.cardOrder.index(self.selectedSlot.card.denom)-1]
                newCard = "{}-{}".format(newDenom, suit)
                self.boardMatrix[startRow][startCol].card = Graphic_Card(newCard)
                self.boardMatrix[startRow][startCol].hidden = False
                self.boardMatrix[startRow][startCol].covered = False

        elif self.selectedSlot.inFlop:
            self.queue_flop_positions()

        else:
            self.boardMatrix[startRow - 1][startCol].hidden = False
            self.boardMatrix[startRow - 1][startCol].covered = False
            allStartCards = [self.selectedSlot] + self.startStack
            for slotCard in allStartCards:
                self.boardMatrix[startRow][startCol].card = None
                startRow += 1

    def queue_flop_positions(self):

        flopSlotThree = self.boardMatrix[0][1]
        flopSlotTwo = self.boardMatrix[0][2]
        flopSlotOne = self.boardMatrix[0][3]

        self.boardMatrix[0][3].card = flopSlotTwo.card
        self.boardMatrix[0][2].card = flopSlotThree.card
        self.boardMatrix[0][1].card = None

    def check_move_validity(self, destSlot):

        if self.selectedSlot.inPile and destSlot.inPile:
            print "Error: Both selected locs are in the piles"
            return False

        if destSlot.card == None and not destSlot.inPile:
            if destSlot.boardMatrixRow == 1 and self.selectedSlot.card.denom == "K":
                self.startStack = self.find_stack_cards()
                return True
            else:
                return False

        if destSlot.covered:
            print "Error: dest slot is covered up"
            return False

        self.startStack = self.find_stack_cards()

        if destSlot.inPile:
            print "dest slot in pile"
            print self.selectedSlot.card.denom
            if self.startStack != []:
                print "Error: there can't be a stack if the dest is a pile"
                return False
            else:
                if destSlot.card == None and self.selectedSlot.card.denom != "A":
                    print "Error: Can only move an ace to the none card"
                    return False
                elif self.selectedSlot.card.suit != destSlot.pileSuit:
                    print "Error: pile suits are not identical"
                    return False
                elif destSlot.card != None:
                    if self.deck.cardOrder.index(self.selectedSlot.card.denom) != self.deck.cardOrder.index(destSlot.card.denom) + 1:
                        print "Error: pile denominations are not consecutive"
                        return False

            return True

        elif self.selectedSlot.card.color == destSlot.card.color and destSlot.card != None:
            print "Error: These cards have the same color"
            return False

        elif self.deck.cardOrder.index(self.selectedSlot.card.denom) != self.deck.cardOrder.index(destSlot.card.denom) - 1:
            print "Error: denominations are not consecutive"
            return False

        return True

    def find_stack_cards(self):

        stackSlots = []

        if self.selectedSlot.inFlop or self.selectedSlot.inPile:
            return []

        rowInScope = self.selectedSlot.boardMatrixRow + 1
        colInScope = self.selectedSlot.boardMatrixColumn
        slot = self.boardMatrix[rowInScope][colInScope]

        while slot.card != None:
            stackSlots.append(slot)
            rowInScope += 1
            slot = self.boardMatrix[rowInScope][colInScope]

        return stackSlots

    def find_appropriate_board_card(self, slotList):
        ## I want to select out the highest row number that has an uncovered card
        for boardSlot in reversed(slotList):
            if boardSlot.card == None and boardSlot.boardMatrixRow == 1 and self.selectedSlot != None:
                if self.selectedSlot.card.denom == "K":
                    #boardSlot.covered = False
                    #boardSlot.hidden = False
                    print "Possible king movement!"
                    return boardSlot
                else:
                    continue

            elif boardSlot.card == None:
                continue

            elif boardSlot.hidden:
                continue

            else:
                return boardSlot

    def update_selected_slot(self, newSlot):

        if newSlot.card == None:
            self.deselect_slot()
            return

        if self.selectedSlot == newSlot:
            self.deselect_slot()
        else:
            self.deselect_slot()
            newSlot.selected = True
            self.selectedSlot = newSlot

    def deselect_slot(self):
        if self.selectedSlot != None:
            self.selectedSlot.selected = False

        self.selectedSlot = None

    def initial_board_setup(self):

        self.deck.shuffle_deck()

        boardMatrix = [
            ["X", "X", "X", "X", "H", "S", "C", "D", "N"],
            ["X", "X", "X", "X", "X", "X", "X"],
            ["-", "X", "X", "X", "X", "X", "X"],
            ["-", "-", "X", "X", "X", "X", "X"],
            ["-", "-", "-", "X", "X", "X", "X"],
            ["-", "-", "-", "-", "X", "X", "X"],
            ["-", "-", "-", "-", "-", "X", "X"],
            ["-", "-", "-", "-", "-", "-", "X"],
            ["-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-"]]

        rowCount = 0
        for row in boardMatrix:
            if rowCount == 0:
                # Set Deck Slot
                boardMatrix[0][0] = Board_Slot(card=None, row=0, col=0, inDeck=True)
                # Set Flop
                boardMatrix[0][1] = Board_Slot(card=None, row=0, col=3, inFlop=True, flopPosition=2)
                boardMatrix[0][2] = Board_Slot(card=None, row=0, col=2, inFlop=True, flopPosition=1)
                boardMatrix[0][3] = Board_Slot(card=None, row=0, col=1, inFlop=True, flopPosition=0)
                # Set Piles
                boardMatrix[0][4] = Board_Slot(card=None, row=0, col=4, inPile=True, pileSuit = "H")
                boardMatrix[0][5] = Board_Slot(card=None, row=0, col=5, inPile=True, pileSuit = "S")
                boardMatrix[0][6] = Board_Slot(card=None, row=0, col=6, inPile=True, pileSuit = "C")
                boardMatrix[0][7] = Board_Slot(card=None, row=0, col=7, inPile=True, pileSuit = "D")

                boardMatrix[0][8] = Board_Slot(card=None, row=0, col=7, newGame=True)

                rowCount += 1
                continue

            posCount = 0
            for pos in row:
                if pos == "X":
                    card = Graphic_Card(self.deck.deck.pop(0))
                    boardMatrix[rowCount][posCount] = Board_Slot(card=card, row=rowCount, col=posCount)
                    if rowCount == posCount + 1:
                        boardMatrix[rowCount][posCount].covered = False
                        boardMatrix[rowCount][posCount].hidden = False

                if pos == "-":
                    boardMatrix[rowCount][posCount] = Board_Slot(card=None, row=rowCount, col=posCount)

                posCount += 1

            rowCount += 1

        print "Board created"

        self.flop = [boardMatrix[0][1], boardMatrix[0][2], boardMatrix[0][3]]
        self.new_flop()

        return boardMatrix

    def new_flop(self):
        # clear current flop
        for loc in reversed(self.flop):
            print "Current flop"
            if loc.card != None:
                self.trash.append(loc.card.cardInfo)
                loc.card = None
            else:
                break

        # set new flop
        if self.deck.deck_empty():
            print "Recycling trash back into deck!"
            self.deck.recycle_deck(self.trash)
            self.deck.show_deck()
            self.trash = []

        posCount = 0
        print "Pick new flop"
        for loc in reversed(self.flop):
            # if deck is empty
            if self.deck.deck_empty():
                print "deck is empty"
                return
            newFlopCard = Graphic_Card(self.deck.deck.pop(0))
            loc.card = newFlopCard

    def board_render(self):

        for row in self.boardMatrix:
            for boardSlot in row:
                boardSlot.show_image(self.gameDisplay)

        pygame.display.update()

    def check_game_over(self):

        if self.trash == [] and self.flop[0].card == None and self.flop[1].card == None and self.flop[2].card == None:
            if self.boardMatrix[0][4].card.denom == "K" and self.boardMatrix[0][5].card.denom == "K" and\
                self.boardMatrix[0][6].card.denom == "K" and self.boardMatrix[0][7].card.denom == "K":
                return True
            else:
                return False

    def win_sequence(self):
        time.sleep(3)
        self.gameDisplay.fill((0, 0, 0))
        youWinImage = pygame.image.load("Images/winImage.png")
        self.gameDisplay.blit(youWinImage, (75,200))
        pygame.display.update()

        time.sleep(5)
        pygame.quit()
        sys.exit()

class CardDeck:

    def __init__(self):

        self.cardOrder = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        self.deck = self.create_deck()

    def create_deck(self):

        suits = ["H", "S", "C", "D"]
        identities = self.cardOrder

        deck = [""] * 52
        count = 0
        for suit in suits:
            for identity in identities:
                card = "{}-{}".format(identity, suit)
                deck[count] = card
                count += 1

        return deck

    def shuffle_deck(self):

        random.shuffle(self.deck)

    def show_deck(self):
        print "DECK: {}".format(self.deck)

    def deck_empty(self):
        if self.deck == []:
            return True
        else:
            return False

    def recycle_deck(self, newDeck):
        self.deck = newDeck

class Board_Slot:

    def __init__(self, card, row, col, inDeck=False, inPile=None, pileSuit=None, inFlop=False, newGame=False, flopPosition=None):

        self.card = card
        self.boardMatrixRow = row
        self.boardMatrixColumn = col

        self.inDeck = inDeck
        self.inFlop = inFlop
        self.flopPosition = flopPosition

        self.hidden = True
        self.covered = True

        if self.inFlop:
            self.hidden = False

            if self.flopPosition == 0:
                self.covered = False


        self.inPile = inPile
        if self.inPile:
            self.covered = False
            self.hidden = False

        self.pileSuit = pileSuit
        self.pileImage = None

        self.newGame = newGame
        self.newGameImage = pygame.image.load('Images/newGame.png')

        self.deckImage = pygame.image.load('Images/deckCard.png')
        self.size = self.deckImage.get_size()

        self.selectedFrameImage = pygame.image.load('Images/FrameImage.png')
        self.selected = False

        self.rectLocX, self.rectLocY = self.get_display_coords()

        if self.inPile and self.card == None:
            suitImageDict = {"H": "Images/pile_heart.png", "S": "Images/pile_spade.png",
                             "C": "Images/pile_club.png", "D": "Images/pile_diamond.png"}
            self.pileImage = pygame.image.load(suitImageDict[self.pileSuit]).convert()

        self.rect = self.declare_rect()

    def get_display_coords(self):

        xMultiplier = 75
        yMultiplier = 27

        row1y = 100
        row1x = 100

        if self.boardMatrixRow == 0:

            if self.inFlop:
                rectLocX = row1x + xMultiplier +  self.flopPosition * 20
                rectLocY = 15

            elif self.inDeck:
                rectLocX = row1x
                rectLocY = 15

            elif self.inPile:
                pilePositionDict = {"H": 3 * xMultiplier + row1x, "S": 4 * xMultiplier + row1x,
                                    "C": 5 * xMultiplier + row1x, "D": 6 * xMultiplier + row1x}
                rectLocX = pilePositionDict[self.pileSuit]
                rectLocY = 15

            elif self.newGame:
                rectLocX = 6 * xMultiplier + row1x + 150
                rectLocY = 15

        else:

            rectLocX = xMultiplier * self.boardMatrixColumn + row1x
            rectLocY = yMultiplier * self.boardMatrixRow + row1y

        return rectLocX, rectLocY

    def declare_rect(self):
        positionRect = pygame.Rect((self.rectLocX, self.rectLocY),self.size)

        return positionRect

    def show_image(self, gameDisplay):

        if self.card == None:

            if self.inPile:
                gameDisplay.blit(self.pileImage, self.rect)

            elif self.inDeck:
                gameDisplay.blit(self.deckImage, self.rect)

            elif self.newGame:
                gameDisplay.blit(self.newGameImage, self.rect)

        else:
            if self.hidden:
                gameDisplay.blit(self.card.cardBackImage, self.rect)
            else:
                gameDisplay.blit(self.card.suitImage, self.rect)
                if self.selected:
                    gameDisplay.blit(self.selectedFrameImage, self.rect)

class Graphic_Card:

    def __init__(self, cardInfo):

        self.suitImagesDict = {
        "A-H": "Images/AH.png",
        "2-H": "Images/2H.png", "3-H": "Images/3H.png", "4-H": "Images/4H.png",
        "5-H": "Images/5H.png", "6-H": "Images/6H.png", "7-H": "Images/7H.png",
        "8-H": "Images/8H.png", "9-H": "Images/9H.png", "10-H": "Images/10H.png",
        "J-H": "Images/JH.png", "Q-H": "Images/QH.png", "K-H": "Images/KH.png",
        "A-S": "Images/AS.png",
        "2-S": "Images/2S.png", "3-S": "Images/3S.png", "4-S": "Images/4S.png",
        "5-S": "Images/5S.png", "6-S": "Images/6S.png", "7-S": "Images/7S.png",
        "8-S": "Images/8S.png", "9-S": "Images/9S.png", "10-S": "Images/10S.png",
        "J-S": "Images/JS.png", "Q-S": "Images/QS.png", "K-S": "Images/KS.png",
        "A-C": "Images/AC.png",
        "2-C": "Images/2C.png", "3-C": "Images/3C.png", "4-C": "Images/4C.png",
        "5-C": "Images/5C.png", "6-C": "Images/6C.png", "7-C": "Images/7C.png",
        "8-C": "Images/8C.png", "9-C": "Images/9C.png", "10-C": "Images/10C.png",
        "J-C": "Images/JC.png", "Q-C": "Images/QC.png", "K-C": "Images/KC.png",
        "A-D": "Images/AD.png",
        "2-D": "Images/2D.png", "3-D": "Images/3D.png", "4-D": "Images/4D.png",
        "5-D": "Images/5D.png", "6-D": "Images/6D.png", "7-D": "Images/7D.png",
        "8-D": "Images/8D.png", "9-D": "Images/9D.png", "10-D": "Images/10D.png",
        "J-D": "Images/JD.png", "Q-D": "Images/QD.png", "K-D": "Images/KD.png",
        }

        self.cardInfo = cardInfo
        print cardInfo
        # split cardInfo into the proper information
        cardInfoList = self.cardInfo.strip().split('-')
        print cardInfoList
        self.suit = cardInfoList[1]
        self.color = self.find_card_color()
        self.denom = cardInfoList[0]
        self.suitImage = pygame.image.load(self.suitImagesDict[self.cardInfo]).convert()
        self.cardBackImage = pygame.image.load('Images/playing_card_back_standard.png').convert()

    def find_card_color(self):
        colorDict = {'H': 'R', 'S': 'B', 'C': 'B', 'D': 'R'}
        color = colorDict[self.suit]
        return color


if __name__ == "__main__":
    main()