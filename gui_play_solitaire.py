import random
import pandas as pd
import sys
import numpy as np
import pygame
import time

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
            pygame.time.Clock().tick(60)

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
            if len(slotList) == 1 and not slotList[0].inFlop:
                boardSlot = slotList[0]
                if boardSlot.inDeck:
                    self.deselect_slot()
                    self.new_flop()
                    return

                elif boardSlot.inPile:
                    print "pile"
                    if boardSlot.card != None:
                        if self.selectedSlot != None:
                            ##TODO test whether move is appropriate
                            properMove = self.check_move_validity(boardSlot)
                            if properMove:
                                self.make_move(boardSlot)
                                self.deselect_slot()
                            else:
                                self.update_selected_slot(boardSlot)
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
                    self.make_move(boardSlot)
                    self.deselect_slot()
                else:
                    self.update_selected_slot(boardSlot)
            else:
                self.update_selected_slot(boardSlot)

    def make_move(self, destSlot):

        # Clean up the destination
        destRow = destSlot.boardMatrixRow
        destCol = destSlot.boardMatrixColumn
        if destSlot.inPile:
            self.boardMatrix[destRow][destCol].card = self.selectedSlot.card
        else:
            allStartCards = [self.selectedSlot] + self.startStack
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
            if self.selectedSlot.card.suit == "A":
                self.boardMatrix[startRow][startCol].card = None

            else:
                suit = self.selectedSlot.card.suit
                newDenom = self.deck.cardOrder[self.deck.cardOrder.index(self.selectedSlot.card.denom)-1]
                newCard = "{}-{}".format(newDenom, suit)
                self.boardMatrix[startRow][startCol].card = Graphic_Card(newCard)
                self.boardMatrix[startRow][startCol].hidden = False
                self.boardMatrix[startRow][startCol].covered = False
        else:
            self.boardMatrix[startRow - 1][startCol].hidden = False
            allStartCards = [self.selectedSlot] + self.startStack
            for slotCard in allStartCards:
                startRow += 1
                self.boardMatrix[startRow][startCol].card = None





        # Uncover cards






    def check_move_validity(self, destSlot):

        if self.selectedSlot.inPile and destSlot.inPile:
            return False

        if destSlot.covered:
            return False

        self.startStack = self.find_stack_cards()

        if destSlot.inPile:
            if startStack != []:
                return False
            else:
                if destSlot.card == None and self.selectedSlot.card.denom != "A":
                    return False
                elif self.selectedSlot.card.suit != destSlot.card.suit:
                    return False
                elif self.deck.cardOrder.index(self.selectedSlot.card.denom) != self.deck.cardOrder.index(destSlot.card.denom) + 1:
                    return False

        elif destSlot.boardMatrixRow == 1 and self.selectedSlot.card.denom != "K":
            return False

        elif self.selectedSlot.card.color == destSlot.card.color:
            return False

        elif self.deck.cardOrder.index(self.selectedSlot.card.denom) != self.deck.cardOrder.index(destSlot.card.denom) - 1:
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
            if boardSlot.card == None:
                continue
            elif boardSlot.hidden:
                continue
            else:
                return boardSlot

    def update_selected_slot(self, newSlot):

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
            ["X", "X", "X", "X", "H", "S", "C", "D"],
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
        for loc in self.flop:
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
        for loc in self.flop:
            # if deck is empty
            if self.deck.deck_empty():
                print "deck is empty"
                break
            newFlopCard = Graphic_Card(self.deck.deck.pop(0))
            loc.card = newFlopCard

    def board_render(self):

        for row in self.boardMatrix:
            for boardSlot in row:
                boardSlot.show_image(self.gameDisplay)

        pygame.display.update()

    def game_over(self):
        if self.boardMatrix[0][4] == "K(H)" and self.boardMatrix[0][5] == "K(S)" and\
                self.boardMatrix[0][6] == "K(C)" and self.boardMatrix[0][7] == "K(D)":
            return True
        else:
            return False


class CardMovement:

    def __init__(self, game, destSlot):

        self.pileSuitDict = {"h":[0,3], "c":[0,5], "s":[0,4], "d":[0,6]}
        self.cardOrder = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

        self.game = game
        self.startSlot = game.selectedSlot
        self.destSlot = destSlot

        self.ensure_valid_loc()


        self.startCard = None
        self.startCardStack = []
        self.destCard = None

        self.startCardDetails = None
        self.destCardDetails = None

        self.populate_card_info()

        if self.startCard is None or self.destCard is None:
            #print "Start Card or Dest Card do not exist"
            raise MovementError("Movement Object Failed")

    def populate_card_info(self):
        # If the destination is the pile, then first I need to find the start cards
        if self.destIsPile == True:
            self.find_start_cards()
            self.find_dest_card()

        else:
            self.find_dest_card()
            self.find_start_cards()

    def ensure_compatible_loc(self, start):

        if self.startSlot.inPile and self.destSlot.inPile:
            raise MovementError("Movement Object Failed")



    def find_start_cards(self):

        if self.startIsPile:
            self.startCardStack = []
            self.startCard = self.current_game.boardMatrix[self.startLoc[0]][self.startLoc[1]]

            if len(self.startCard) == 1:
                print "Error: There is no card in the chosen pile."
                raise MovementError("Find Start Cards Failed")

            self.find_card_details(start=True)
            return

        elif self.validStartLoc == "FLOP":
            try:
                self.startCard = self.current_game.flop[0]

            except IndexError:
                #print "Error: There are no cards in the flop. Please try again."
                raise MovementError("Find Start Cards Failed")

            self.startCardStack = []
            self.startLoc = "FLOP"
            self.find_card_details(start=True)
            return

        else:
            col = self.startLoc[1]

            if self.destIsPile:
                possibleRows = range(1, 20)
                for row in possibleRows:
                    card = self.current_game.boardMatrix[row][col]
                    if card == "-":
                        if row == 1:
                            print "Error: Given column has no cards to move. Please try again."
                            raise MovementError("Movement Object Failed")
                        else:
                            self.startCard = self.current_game.boardMatrix[row - 1][col]
                            self.startCardStack = []
                            self.startLoc[0] = row - 1
                            self.find_card_details(start=True)
                            return

            else:
                ###### Otherwise need to find the optimal start that fits the destination... might want to break these into mini functions
                ### Have to assume the dest card is already known

                possibleRows = range(1, 20)
                for row in possibleRows:
                    card = self.current_game.boardMatrix[row][col]
                    if card == "-":
                        if row == 1:
                            print "Error: This column of the board has no cards to be moved."
                            self.startCard = None
                            raise MovementError("Movement Object Failed")
                        else:
                            print "Error: There are no potential cards to be moved in this column."
                            self.startCard = None
                            raise MovementError("Movement Object Failed")
                    elif card[0] == "H":
                        continue

                    # Now check for any compatible cards
                    else:

                        self.startCard = card
                        self.find_card_details(start=True)
                        if self.check_move_validity(supressPrint=True) == True:
                            self.startLoc[0] = row
                            break

                potentialStackIndices = range(row+1,20)
                for pos in potentialStackIndices:
                    stackCard = self.current_game.boardMatrix[pos][col]
                    if stackCard[0] != "-":
                        self.startCardStack.append(stackCard)
                    else:
                        break

    def find_dest_card(self):

        if self.destIsPile:
            startSuit = self.startCardDetails[1].lower()
            self.destLoc = self.pileSuitDict[startSuit]
            self.destCard = self.current_game.boardMatrix[self.destLoc[0]][self.destLoc[1]]
            self.find_card_details(start=False)
            return

        else:
            col = self.destLoc[1]

            possibleRows = range(1,20)

            for row in possibleRows:
                card = self.current_game.boardMatrix[row][col]
                if card == "-":
                    if row == 1:
                        row = row + 1

                    self.destCard = self.current_game.boardMatrix[row - 1][col]
                    self.destLoc[0] = row - 1
                    self.find_card_details(start=False)
                    return

    def find_card_details(self, start):

        cardSuitDict = {"H": "R", "D": "R", "C": "B", "S": "B", "-": "-"}

        card = None

        if start == True:
            card = self.startCard
        elif start == False:
            card = self.destCard
            if len(card) == 1:
                cardColor = cardSuitDict[card]

                self.destCardDetails = [card, card, cardColor]
                return

        cardSuit = card[-2]
        cardColor = cardSuitDict[cardSuit]

        cardList = card.strip().split('(')
        cardDenom = cardList[0]

        if start == True:
            self.startCardDetails = [cardDenom, cardSuit, cardColor]

        elif start == False:
            self.destCardDetails = [cardDenom, cardSuit, cardColor]

    def check_move_validity(self, supressPrint):
        # TODO should probably make cleaner

        startCardDenom = self.startCardDetails[0]
        startCardSuit = self.startCardDetails[1]
        startCardColor = self.startCardDetails[2]

        destCardDenom = self.destCardDetails[0]
        destCardSuit = self.destCardDetails[1]
        destCardColor = self.destCardDetails[2]

        if self.destLoc[0] == 0:
            # Same suit
            if startCardSuit != destCardSuit:
                print "Error: Incompatible suits -- this card cannot be moved to the {} pile.".format(destCardSuit)
                return False
            # Is it an A?
            elif startCardDenom == "A":
                return True
            # If not an A, does it follow the correct card?

            elif destCardDenom in ["C", "H", "D", "S"]:
                print "Error: Incompatible card denominations -- this card cannot be moved to the {} pile".format(destCardSuit)
                return False

            elif self.cardOrder.index(destCardDenom) != self.cardOrder.index(startCardDenom) - 1:
                print "Error: Incompatible card denominations -- this card cannot be moved to the {} pile".format(destCardSuit)
                return False

        elif self.destLoc[0] == 1 and self.destCard == "-" and self.startCardDetails[0] == "K":
            return True

        elif self.current_game.boardMatrix[self.destLoc[0]+1][self.destLoc[1]] != "-":
            if not supressPrint:
                print "Error: Cannot move card into the middle of stack."
            return False

        elif startCardColor == destCardColor:
            if not supressPrint:
                print "Error: These cards are incompatible (same color)."
            return False
        else:
            if self.cardOrder.index(destCardDenom) != self.cardOrder.index(startCardDenom) + 1:
                if not supressPrint:
                    print "Error: Denominations are not consecutive"
                return False

        return True

    def make_move(self):

        if self.check_move_validity(supressPrint=False) == False:
            raise MovementError("This move is not valid")

        ## remove Flop card
        if self.startLoc == "FLOP":
            self.current_game.flop.pop(0)

            columnDestIndex = self.destLoc[1]
            rowDestIndex = self.destLoc[0]

            # For Aces and Kings
            if not (rowDestIndex == 0 or (rowDestIndex == 1 and self.startCardDetails[0] == "K")):
                rowDestIndex += 1

            # Change dest locus
            self.current_game.boardMatrix[rowDestIndex][columnDestIndex] = self.startCard
            return

        ## remove pile card
        elif self.startLoc[0] == 0:

            if self.startCardDetails[0] == "A":
                self.current_game.boardMatrix[0][self.startLoc[1]] = self.startCardDetails[1]

            else:
                newDenom = self.cardOrder[self.cardOrder.index(self.startCardDetails[0])-1]
                suit = self.startCardDetails[1]
                newCard = "{}({})".format(newDenom, suit)
                self.current_game.boardMatrix[0][self.startLoc[1]] = newCard



            columnDestIndex = self.destLoc[1]
            rowDestIndex = self.destLoc[0] + 1

            # Change dest locus
            self.current_game.boardMatrix[rowDestIndex][columnDestIndex] = self.startCard


        ## remove board cards and move it to a new location
        else:

            columnDestIndex = self.destLoc[1]

            columnStartIndex = self.startLoc[1]
            rowStartIndex = self.startLoc[0]

            ## With the exception of destination loci being the piles, the rest of the moves follow the same pattern
            if self.destLoc[0] == 0:
                self.current_game.boardMatrix[0][columnDestIndex] = self.startCard
                self.current_game.boardMatrix[rowStartIndex][columnStartIndex] = "-"

            else:
                cards = [self.startCard] + self.startCardStack
                destCount = 1
                startCount = 0
                if self.destLoc[0] == 1 and self.destCard == "-":
                    destCount -= 1

                for card in cards:

                    columnDestIndex = self.destLoc[1]
                    rowDestIndex = self.destLoc[0] + destCount

                    columnStartIndex = self.startLoc[1]
                    rowStartIndex = self.startLoc[0] + startCount

                    # Change dest locus
                    self.current_game.boardMatrix[rowDestIndex][columnDestIndex] = card
                    # Remove moving cards from start positions
                    self.current_game.boardMatrix[rowStartIndex][columnStartIndex] = "-"

                    destCount += 1
                    startCount += 1


        ## Finally, flip over any cards that should now be visible
        if self.startLoc == "FLOP":
            return

        if self.startLoc[0] >= 2:

            cardInScope = self.current_game.boardMatrix[self.startLoc[0]-1][self.startLoc[1]]

            if cardInScope[0:2] == "H:":
                self.current_game.boardMatrix[self.startLoc[0] - 1][self.startLoc[1]] = cardInScope[2:]


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

    def __init__(self, card, row, col, inDeck=False, inPile=None, pileSuit=None, inFlop=False, flopPosition=None):

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
        self.pileSuit = pileSuit
        self.pileImage = None

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
        yMultiplier = 30

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

class MovementError(Exception):
    pass


def main():

    pygame.init()

    # Set window
    displayWidth = 800
    displayHeight = 600

    black = (0, 0, 0)
    white = (255, 255, 255)
    red = (255, 0, 0)
    green = (0, 128, 0)

    gameDisplay = pygame.display.set_mode((displayWidth, displayHeight))
    gameDisplay.fill(green)
    pygame.display.set_caption("Solitaire")
    gameDisplay.set_colorkey(black)

    Game(gameDisplay).main_loop()

    pygame.quit()
    sys.exit()

## card width = 1
## card height = 1.53



def message_display(text):
    largeText = pygame.font.Font('freesansbold.ttf', 115)
    textSurface, textRectangle = text_objects(text, largeText)
    textRectangle.center = ((displayyWidth / 2), (displayHeight / 2))
    gameDisplay.blit(textSurface, textRectangle)

    pygame.display.update()

    time.sleep(2)

    game_loop()


def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()


if __name__ == "__main__":
    main()