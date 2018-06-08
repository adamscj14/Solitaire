
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

        self.new_flop()
        self.deck.shuffle_deck()

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

        self.board_render(self.player)

        while choice != 4:

            if self.game_over() == True:
                print "Hurray, you have won! Congratulations"
                sys.exit()

            choice = raw_input('''Main Menu:
            1: Move Card
            2: New Flop
            3: New Game
            4: Quit
            ''')

            try:
                choice = int(choice)

            except ValueError:
                print "Error: Invalid choice! Please try again."
                continue

            if choice == 1:
                ## Card To Move
                startInput = raw_input(
                    "Which card would you like to move? Please give the row and the column (row,column):")
                ## Destination Card
                destInput = raw_input(
                    "Where would you like to move the card? Please give the row and the column (row,column):")

                moveInput = [startInput, destInput]

                self.move_board_card(moveInput[0], moveInput[1])
                self.board_render(self.player)

            elif choice == 2:
                self.new_flop()
                self.board_render(self.player)

            elif choice == 3:
                print "-" * 30
                print "NEW GAME"
                print "-"*30
                play = Game(self.player)
                play.main_menu()

            elif choice == 4:
                print "End Game. Thanks for playing!"
                sys.exit()

            else:
                print "Error: Invalid choice! Please try again."

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

    def board_render(self, player):
        renderMatrix = []
        endRow = 0

        suitRenderDict = {"(S)": "\u2660", "(D)": "\u2662", "(H)": "\u2661", "(C)": "\u2663"}
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
                        #suitRendering = suitRenderDict[row[posCount][-3:]]
                        #renderRow[posCount] = u"{}{}".format(row[posCount][:-3], suitRenderDict[row[posCount][-3:]])
                        #renderRow[posCount] = row[posCount][:-3] + u"{}".format(suitRendering)
                        denom = row[posCount][:-3]
                        suit = row[posCount][-3:]
                        if suit == '(H)':
                            renderRow[posCount] = ' '+denom + u'\u2661'
                        elif suit == '(S)':
                            renderRow[posCount] = ' '+denom + u'\u2660'
                        elif suit == '(D)':
                            renderRow[posCount] = ' '+denom + u'\u2662'
                        elif suit == '(C)':
                            renderRow[posCount] = ' '+denom + u'\u2663'

                    elif len(pos) == 1 and pos not in ["-", "X"]:
                        if pos == 'H':
                            renderRow[posCount] = ' '+u'\u2661'+''
                        elif pos == 'S':
                            renderRow[posCount] = ' '+u'\u2660'+''
                        elif pos == 'D':
                            renderRow[posCount] = ' '+u'\u2662'+''
                        elif pos == 'C':
                            renderRow[posCount] = ' '+u'\u2663'+''
                    posCount += 1

                renderMatrix.append(renderRow)

        print "---------------------------------------------------------"
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
        except Exception:
            return

    def game_over(self):
        if self.boardMatrix[0][3] == "K(H)" and self.boardMatrix[0][4] == "K(S)" and self.boardMatrix[0][5] == "K(C)" and self.boardMatrix[0][5] == "K(D)":
            return True
        else:
            return False


class CardMovement:

    def __init__(self, game, location, destination):

        self.current_game = game

        self.userStartLocInput = location
        self.userDestLocInput = destination

        self.startLoc = self.ensure_valid_loc(start = True)
        self.destLoc = self.ensure_valid_loc(start = False)

        if self.startLoc is None or self.destLoc is None:
            raise Exception("Movement Object Failed")

        startCards = self.find_start_cards()
        if startCards is None:
            raise Exception("Movement Object Failed")

        self.startCard = startCards[0]
        self.startCardStack = startCards[1]

        self.destCard = self.find_dest_card()

        if self.destCard is None:
            raise Exception("Movement Object Failed")

        # find the specifics of the card [denomination, suit, color]
        self.startCardDetails = self.find_card_details(start = True)
        self.destCardDetails = self.find_card_details(start = False)

        self.cardOrder = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

        self.make_move()

    def ensure_valid_loc(self, start):

        inLoc = None

        if start == True:
            inLoc = self.userStartLocInput
        elif start == False:
            inLoc = self.userDestLocInput

        if inLoc == "FLOP":
            if start == True:
                return "FLOP"
            else:
                print "Error: Destination location cannot be the Flop. Please try again"
                return None

        else:
            loc = inLoc.strip().split(',')
            if len(loc) != 2:
                print "Error: Malformed input location command. Please try again."
                return None

            try:
                loc[0] = int(loc[0])
                loc[1] = int(loc[1])
            except ValueError:
                print "Error: Must provide ints for location command. Please try again."
                return None

            else:
                try:
                    self.current_game.boardMatrix[loc[0]][loc[1]]
                except IndexError:
                    print "Error: Locations must be within the confines of the board. Please try again."
                    return None

            return loc

    def find_start_cards(self):

        if self.startLoc == "FLOP":
            try:
                startCard = self.current_game.flop[0]
            except IndexError:
                print "Error: There are no cards in the flop. Please try again."
                return None
            return [startCard, []]

        invalidStartCards = ["-" ,"?" ,"X", "H", "S", "C", "D"]
        startCard = self.current_game.boardMatrix[self.startLoc[0]][self.startLoc[1]]

        if startCard[0] in invalidStartCards:
            print "Error: This position of the board cannot be moved. Please try again."
            return None

        potentialStackIndices = range(self.startLoc[0]+1,19)
        stack = []
        for pos in potentialStackIndices:
            stackCard = self.current_game.boardMatrix[pos][self.startLoc[1]]
            if stackCard[0] not in invalidStartCards:
                stack.append(stackCard)
            else:
                break

        return [startCard, stack]

    def find_dest_card(self):
        try:
            destCard = self.current_game.boardMatrix[self.destLoc[0]][self.destLoc[1]]
        except IndexError:
            print "Error: The position chosen does not exist. Please try again"
            return None

        if destCard == "-" and not (self.destLoc[0] == 1 and self.startCard[0] == "K"):

            print "Error: This position of the board is an invalid destination. Please try again."
            return None

        elif destCard == "X" or destCard[0:2] == "H:":

            print "Error: This position of the board is an invalid destination. Please try again."
            return None

        else:
            return destCard

    def find_card_details(self, start):

        cardSuitDict = {"H": "R", "D": "R", "C": "B", "S": "B", "-": "-"}

        card = None

        if start == True:
            card = self.startCard
        elif start == False:
            card = self.destCard
            if len(card) == 1:
                cardColor = cardSuitDict[card]

                return [card, card, cardColor]

        cardSuit = card[-2]
        cardColor = cardSuitDict[cardSuit]

        cardList = card.strip().split('(')
        cardDenom = cardList[0]

        return [cardDenom, cardSuit, cardColor]

    def check_move_validity(self):
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
            elif self.cardOrder.index(destCardDenom) != self.cardOrder.index(startCardDenom) - 1:
                print "Error: Incompatible card denominations -- this card cannot be moved to the {} pile".format(destCardSuit)
                return False

        elif self.destLoc[0] == 1 and self.destCard == "-" and self.startCardDetails[0] == "K":
            return True

        elif self.current_game.boardMatrix[self.destLoc[0]+1][self.destLoc[1]] != "-":
            print "Error: Cannot move card into the middle of stack."
            return False

        elif startCardColor == destCardColor:
            print "Error: These cards are incompatible (same color)."
            return False
        else:
            if self.cardOrder.index(destCardDenom) != self.cardOrder.index(startCardDenom) + 1:
                return False

        return True

    def make_move(self):

        if self.check_move_validity() == False:
            raise Exception("This move is not valid")

        ## remove Flop card
        if self.startLoc == "FLOP":
            self.current_game.flop.pop(0)

            columnDestIndex = self.destLoc[1]
            rowDestIndex = self.destLoc[0] + 1

            # For Aces and Kings
            if rowDestIndex == 0 or rowDestIndex == 1:
                rowDestIndex -= 1

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
                print cards
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


def main():
    # Initialize the player
    player = game_for_player()
    # Initialize the game
    play = Game(player)
    # Begin the loop to run the game
    play.main_menu()


def game_for_player():
    validInput = False
    while validInput != True:
        player = raw_input("Is this game for a super-user? (Y/N)\n")
        if player == "Y":
            player = False
            print "Welcome to the game, super-user!"
            validInput = True

        elif player == "N":
            player = True
            print "Welcome to the game, normal player!"
            validInput = True

        else:
            print "Invalid input, please try again."

    return player


if __name__ == "__main__":
    main()