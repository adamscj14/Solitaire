
import random
import pandas as pd
import sys
import numpy as np

class Game:

    def __init__(self, player):

        self.deck = CardDeck()
        self.flop = ["NA", "NA", "NA"]
        self.boardMatrix = self.initial_board_setup()
        self.trash = []
        self.player = player

    def initial_board_setup(self):


        self.deck.shuffle_deck()
        self.new_flop()

        boardMatrix = [["X", "X", "X", "H", "S", "C", "D"],
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

        rowCount = 1
        for row in boardMatrix[1:8]:
            posCount = rowCount - 1
            for pos in row[posCount:]:

                if pos == "X":
                    card = self.deck.deck.pop(0)
                    if rowCount <= posCount:
                        card = "H:{}".format(card)
                    boardMatrix[rowCount][posCount] = card
                posCount += 1

            rowCount += 1

        print "Board created"

        return boardMatrix

    def main_menu(self):

        choice = None

        while 1:

            self.board_render(self.player)

            if self.game_over() == True:
                print "Hurray, you have won! Congratulations"
                sys.exit()

            choice = str(raw_input('''Main Menu:
            M: Move Card
            F: New Flop
            Q: Quit
            '''))

            choice = choice.lower()

            if choice not in ["m", "f", "q"]:
                print "Error: Invalid choice! Please try again."
                continue


            if choice == "m":
                ## Card To Move
                userCardInput = self.get_card_inputs()

                if userCardInput is None:
                    continue

                startInput = userCardInput[0]
                destInput = userCardInput[1]

                self.move_board_card(startInput,destInput)

            elif choice == "f":
                self.new_flop()

            elif choice == "q":

                quitMenu = self.main_menu_quit()
                if quitMenu == True:
                    sys.exit()
                else:
                    continue

            else:
                print "Error: Invalid choice! Please try again."

    def main_menu_quit(self):
        validInput = False
        affirmativeList = ["y", "yes"]
        negativeList = ["n", "no"]
        while validInput != True:
            quitCommand = str(raw_input("Are you sure you want to quit? (y/n)\n"))

            if quitCommand.lower() in affirmativeList:
                print "Exiting game. Thanks for playing!"
                return True

            elif quitCommand.lower() in negativeList:
                return False

            else:
                print "Invalid input, please try again."

    def new_flop(self):
        # clear current flop
        posCount = 0
        for card in self.flop:
            if card != "NA":
                self.trash.append(card)
                self.flop[posCount] = "NA"
            else:
                break
            posCount += 1

        self.flop = ["NA", "NA", "NA"]

        # set new flop
        if self.deck.deck_empty():
            print "Recycling trash back into deck!"
            self.deck.recycle_deck(self.trash)
            self.trash = []

        posCount = 0
        for pos in self.flop:
            if self.deck.deck == []:
                self.flop = [card for card in self.flop if card != "NA"]
                break
            newFlopCard = self.deck.deck.pop(0)
            self.flop[posCount] = newFlopCard
            posCount += 1

    def get_card_inputs(self):
        pileCommands = ["pile", "p"]
        suits = ["h", "c", "s", "d"]

        startInput = str(raw_input("Which card would you like to move? Please either give the column index, pile (p), or flop (f):"))
        if startInput.lower() in pileCommands:

            pileSuit = str(raw_input("Which suit pile would you like to move a card from? Please give the suit (s,c,d, or h):"))
            if pileSuit.lower() not in suits:
                print "Error: This suit does not exist. Please try again"
                return

            else:
                startInput = "P-{}".format(pileSuit)

        ## Destination Card
        destInput = str(raw_input("Where would you like to move the card? Please give a column or pile (p):"))

        if startInput == "" or destInput == "":
            print "Error: No input given for one of the inputs. Please try again."
            return

        return [startInput, destInput]

    def board_render(self, player):
        renderMatrix = []
        endRow = 0

        suitRenderDict = {"(S)": u"\u2660", "(D)": u"\u2662", "(H)": u"\u2661", "(C)": u"\u2663"}

        for row in self.boardMatrix:
            if row == ["-", "-", "-", "-", "-", "-", "-"]:
                endRow += 1
                if endRow == 2:
                    break
                else:
                    renderMatrix.append(row)

            elif not player:
                renderMatrix.append(row)
            else:
                posCount = 0
                renderRow = list(row)
                for pos in renderRow:
                    if pos[0:2] == "H:":
                        renderRow[posCount] = "?"
                    elif len(pos) > 1:
                        denom = row[posCount][:-3]
                        suit = row[posCount][-3:]

                        renderRow[posCount] = u"{}{}".format(denom, suitRenderDict[suit])

                    elif len(pos) == 1 and pos not in ["-", "X"]:
                        suit = "({})".format(pos)
                        renderRow[posCount] = u"{}".format(suitRenderDict[suit])

                    posCount += 1

                renderMatrix.append(renderRow)

        print "-" *30
        sys.stdout.write("FLOP: ")
        for card in self.flop:
            denom = card[:-3]
            suit = card[-3:]
            if suit == '(H)':
                sys.stdout.write(denom + u'\u2661 ')
            elif suit == '(S)':
                sys.stdout.write(denom + u'\u2660 ')
            elif suit == '(D)':
                sys.stdout.write(denom + u'\u2662 ')
            elif suit == '(C)':
                sys.stdout.write(denom + u'\u2663 ')
        sys.stdout.flush()
        print
        print pd.DataFrame(renderMatrix)

        if not player:
            print "TRASH: {}".format(self.trash)
            self.deck.show_deck()

    def move_board_card(self, userLocationInput, userDestinationInput):

        try:
            move = CardMovement(self, userLocationInput, userDestinationInput)
            move.make_move()
        except MovementError:
            print "Error: Movement failed."
            return

    def game_over(self):
        if self.boardMatrix[0][3] == "K(H)" and self.boardMatrix[0][4] == "K(S)" and self.boardMatrix[0][5] == "K(C)" and self.boardMatrix[0][5] == "K(D)":
            return True
        else:
            return False


class CardMovement:

    def __init__(self, game, location, destination):

        self.pileSuitDict = {"h":[0,3], "c":[0,5], "s":[0,4], "d":[0,6]}
        self.cardOrder = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

        self.current_game = game
        self.userStartLocInput = location
        self.userDestLocInput = destination

        self.startIsPile = False
        self.destIsPile = False

        self.startLoc = None
        self.destLoc = None

        self.validStartLoc = self.ensure_valid_loc(start = True)
        self.validDestLoc = self.ensure_valid_loc(start = False)

        if self.validStartLoc is None or self.validDestLoc is None:
            #print "Locations are not considered valid"
            raise MovementError("Movement Object Failed")

        if self.startIsPile and self.destIsPile:
            #print "Both the start card and dest are piles"
            raise MovementError("Movement Object Failed")

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

    def ensure_valid_loc(self, start):

        inLoc = None
        flopCommands = ["flop", "f"]
        pileCommands = ["pile", "p"]

        if start == True:
            inLoc = self.userStartLocInput
        elif start == False:
            inLoc = self.userDestLocInput

        if inLoc.lower() in flopCommands:
            if start == True:
                return "FLOP"
            else:
                print "Error: Destination location cannot be the Flop. Please try again"
                return None

        if inLoc.lower()[0] in pileCommands:
            if start == False:
                self.destIsPile = True
                self.destLoc = "PILE"
                return True

            else:
                self.startIsPile = True
                suitPile = inLoc[2]
                startLoc = self.pileSuitDict[suitPile]
                self.startLoc = startLoc
                return True

        else:
            if len(inLoc) > 1:
                print "Error: Malformed input. Please try again."
                return

            try:
                col = int(inLoc)
            except ValueError:
                print "Error: Invalid position input"
                return

            if not -1 < col < 7:
                print "Error: This column is out of range. Please try again."
                return

            if start == True:
                self.startLoc = ["", col]
            else:
                self.destLoc = ["", col]

        return True

    def find_start_cards(self):

        if self.startIsPile:
            self.startCardStack = []
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
                self.current_game.boardMatrix[0][self.destLoc[1]] = self.startCardDetails[1]
            else:
                newDenom = self.cardOrder[self.cardOrder.index(self.startCardDetails[0])-1]
                suit = self.startCardDetails[1]
                newCard = "{}({})".format(newDenom, suit)
                self.current_game.boardMatrix[0][self.destLoc[1]] = newCard

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
        deck = self.create_deck()
        self.deck = deck

    def create_deck(self):
        suits = ["H", "S", "C", "D"]
        identities = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]

        deck = [""] * 52
        count = 0
        for suit in suits:
            for identity in identities:
                card = "{}({})".format(identity, suit)
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


class MovementError(Exception):
    pass


def game_for_player():
    validInput = False
    affirmativeList = ["y", "yes"]
    negativeList = ["n", "no"]
    while validInput != True:
        player = str(raw_input("Is this game for a super-user? (y/n)\n"))

        if player.lower() in affirmativeList:
            player = False
            print "Welcome to the game, super-user!"
            validInput = True

        elif player.lower() in negativeList:
            player = True
            print "Welcome to the game, normal player!"
            validInput = True

        else:
            print "Invalid input, please try again."

    return player


def main():
    # Initialize the player
    #player = game_for_player()
    player = True
    # Initialize the game
    play = Game(player)
    # Begin the loop to run the game
    play.main_menu()


if __name__ == "__main__":
    main()