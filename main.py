# Risk Bot
# This code will create a classic risk board and then a bot will play a game so that it can win a majority of its games

# Current Issues: Drafting is still manual, eventually need computer input, a computer cannot determine the amount of
# drafts they get yet
# Visualization is working almost correctly, needs to handle player death still
# Cards are still unused. Will be used after bot has been created

import csv
import random
import time
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from matplotlib.lines import Line2D


class Territory:
    def __init__(self):
        self.num_troops = 0
        self.connections = []
        self.player_control = ""
        self.ID = ""


class Continent:
    def __init__(self):
        self.territories = []
        self.ID = ""
        self.bonus = 0


class Player:
    def __init__(self):
        self.num_troops = 0
        self.controlled_territories = []
        self.color = ""
        self.cards = []

    def set_num_troops(self):
        numTroops = 0
        for item in self.controlled_territories:
            numTroops += item.num_troops
        self.num_troops = numTroops

    def play_cards(self, played_cards):
        values = [4, 6, 8, 10]
        infantry = 0
        cavalry = 0
        artillery = 0
        controlled = 0
        for item in played_cards:
            if item.kind == "Infantry":
                infantry += 1
            elif item.kind == "Cavalry":
                cavalry += 1
            elif item.kind == "Artillery":
                artillery += 1
            else:
                infantry += 1
                cavalry += 1
                artillery += 1
            if controlled == 0:
                for terr in self.controlled_territories:
                    if item.territory == terr.ID:
                        controlled = 1
                        terr.num_troops += 2
                        break

        if infantry == 3:  # This section needs to be updated to allow AI thinking
            for i in range(0, values[0]):
                self.draft(self.controlled_territories[0])
        elif cavalry == 3:
            for i in range(0, values[1]):
                self.draft(self.controlled_territories[0])
        elif artillery == 3:
            for i in range(0, values[2]):
                self.draft(self.controlled_territories[0])
        else:
            for i in range(0, values[3]):
                self.draft(self.controlled_territories[0])

    def draft(self, territory):  # will draft one troop at a time everytime it is called
        territory.num_troops += 1
        self.set_num_troops()

    def draw_card(self, deck):
        flag = 0
        while flag == 0:
            for card in deck.cards:
                if random.random() * 400 < 1:
                    self.cards.append(card)
                    deck.cards.remove(card)
                    flag = 1
                    break

    def fortify(self, terr_from, terr_to, num_troops):  # Must be verified with bfs before executing to establish connection
        terr_from.num_troops -= num_troops
        terr_to.num_troops += num_troops

    def attack(self, terr_from, terr_to, num_attackers):  # will perform one attack every time it is called
        connected = False
        for item in terr_from.connections:
            if item.ID == terr_to.ID:
                connected = True
        if num_attackers > 3:
            print('too many attackers')
            return
        if num_attackers < 1:
            print('too few attackers')
            return
        if num_attackers > terr_from.num_troops:
            print('too many attackers compared to territory')
            return
        if not connected:
            print('not connected')
            return
        attacker_dice = num_attackers
        defender_dice = 1
        if terr_to.num_troops > 1:
            defender_dice = 2
        rolled_attackers = []
        rolled_defenders = []
        for i in range(0, attacker_dice):
            rolled_attackers.append(int(random.random() * 6) + 1)
        for i in range(0, defender_dice):
            rolled_defenders.append(int(random.random() * 6) + 1)
        rolled_attackers.sort(reverse=True)
        rolled_defenders.sort(reverse=True)
        comparisons = 0
        if len(rolled_defenders) > len(rolled_attackers):
            comparisons = len(rolled_attackers)
        else:
            comparisons = len(rolled_defenders)
        for i in range(0, comparisons):
            if rolled_attackers[i] > rolled_defenders[i]:
                terr_to.num_troops -= 1
                terr_to.player_control.num_troops -= 1
                if terr_to.num_troops <= 0:
                    if terr_to.player_control.num_troops == 0:
                        death = terr_to.player_control
                    else:
                        death = None
                    terr_to.player_control.controlled_territories.remove(terr_to)
                    terr_to.player_control = self
                    self.controlled_territories.append(terr_to)
                    terr_to.num_troops = num_attackers
                    terr_from.num_troops -= num_attackers
                    if terr_from.num_troops > 1:
                        self.fortify(terr_from, terr_to, terr_from.num_troops - 1)
                    return death
            else:
                terr_from.num_troops -= 1
            self.set_num_troops()
            terr_to.player_control.set_num_troops()

    def fortify_path(self, terr_from, terr_to):  # Determines if the path can be fortified to using BFS
        path = [terr_from]
        checked = []
        while len(path) > 0:
            terr = path.pop()
            checked.append(terr)
            for connection in terr.connections:
                if connection.player_control == self and not checked.__contains__(connection) and not path.__contains__(connection):
                    path.append(connection)
                    if connection == terr_to:
                        return True
        return False

    def attack_path(self,terr_from, terr_to):  # Appears to return the path in reverse order
        # Finds the least costliest path from a location on the board to another, returns cost of action. This may
        # need to change in the future to allow for different outcomes and opportunities such as completing a continent

        class Node:
            def __init__(self):
                self.territory = ""
                self.cost = 9999999999999 # when assigning cost, always add 1 to a territory, because one must be left behind on previous territory
                self.backedge = ''

        node = Node()
        node.territory = terr_from
        node.cost = 0
        multimap = []
        dict = {
            "Distance": node.cost,
            "Node": node
        }
        # Create first Node, place on multimap
        multimap.append(dict)
        #multimap = sorted(multimap, key=lambda dict: dict['Distance'])

        # Visit first Node, pop it, all new nodes have a backedge to the first node
        visited = []
        while len(multimap) > 0:
            # Pops the first element, with the shortest distance
            currentDict = multimap.pop(0)
            currentNode = currentDict["Node"]
            visited.append(currentNode.territory)
            if visited.__contains__(terr_to):
                while currentNode.backedge != "":
                    currentNode = currentNode.backedge
                return
            # Creates a new Node and associated dictionary, places it back on the multimap
            for terr in currentNode.territory.connections:
                if visited.__contains__(terr) or terr.player_control == self:
                    continue
                newNode = Node()
                newNode.territory = terr
                newNode.cost = terr.num_troops
                newNode.backedge = currentNode
                dict = {
                    "Distance": newNode.cost + 1,
                    "Node": newNode
                }
                multimap.append(dict)

class Card:
    def __init__(self):
        self.kind = ""
        self.territory = ""


class Deck:

    def __init__(self, continents):
        self.cards = []
        self.discard = []
        kinds = ["Infantry", "Cavalry", "Artillery", "Wild"]
        assigned = []
        for i in range(0, 3):
            for j in range(0, 14):
                card = Card()
                card.kind = kinds[i]
                flag = 0
                while flag == 0:
                    for cont in continents:
                        if flag == 1:
                            break
                        for terr in cont.territories:
                            if random.random() * 400 < 1 and assigned.__contains__(terr) is False:
                                flag = 1
                                card.territory = terr.ID
                                assigned.append(terr)
                                self.cards.append(card)
                                break
        for i in range(0, 2):
            card = Card()
            card.kind = kinds[3]
            self.cards.append(card)


    def shuffle(self, discard):
        print()


def create_territories():
    # This part creates all the territories from a csv file
    # The territories all have connections that are still in string format and not class
    continents = []
    with open("TestMap.csv") as file:
        csv_file = csv.reader(file, delimiter=",")
        for row in csv_file:
            if row[1] == "":
                cont = Continent()
                cont.ID = row[0]
                continents.append(cont)
                continue
            terr = Territory()
            for item in row:
                if item == row[0]:
                    terr.ID = item
                elif item != "":
                    terr.connections.append(item)
            cont.territories.append(terr)

    # The following part converts the string connections into classes

    for item in continents:
        for terr in item.territories:
            for i in range(0, len(terr.connections)):
                con = terr.connections
                flag = 0
                for terr2 in item.territories:
                    if terr2.ID == con[i]:
                        con[i] = terr2
                        flag = 1
                        break
                if flag != 1:
                    for item2 in continents:
                        for terr2 in item2.territories:
                            if terr2.ID == con[i]:
                                con[i] = terr2
                                break
    return continents


def create_map(num_players, continents):
    # This portion defines the players into existence
    colors = ["Red", "Green", "Blue", "Yellow", "Purple", "Black"]
    num_troops = 40 - (num_players - 2) * 5
    players = []
    for i in range(0, num_players):
        players.append(create_player(num_troops, colors[i]))

    # This creates a list of territories that currently have no control or troops assigned to them
    unassigned = []
    for continent in continents:
        for territory in continent.territories:
            unassigned.append(territory)

    # This assigns one troop to the unassigned territories
    unassigned_troops = num_troops
    while len(unassigned) > 0:
        for player in players:
            flag = 0
            while flag == 0 and len(unassigned) > 0:
                for terr in unassigned:
                    # if random number rolled is 1 / num territories, then update the lists for players and territories
                    if random.random() * 400 < 1:
                        player.controlled_territories.append(terr)
                        terr.player_control = player
                        terr.num_troops += 1
                        unassigned.remove(terr)
                        flag = 1
                        break
        unassigned_troops -= 1

    # This will assign the remaining number of troops to each players' territories
    for player in players:
        deployed = len(player.controlled_territories)
        while deployed < num_troops:
            for terr in player.controlled_territories:
                if random.random() * 400 < 1:
                    terr.num_troops += 1
                    deployed += 1
                    break
    return players


def create_player(num_troops, color):  # This will create a player and set the color and number of troops
    player = Player()
    player.num_troops = num_troops
    player.color = color
    return player


class Chart:

    def __init__(self, players):
        plt.ion()
        self.turns = [0]

        self.lines = []
        self.lines2 = []

        self.troop_count = []
        self.terr_count = []

        self.figure, self.ax = plt.subplots()
        self.ax.set_title("Turns vs Number of Troops")
        self.ax.set_xlabel("Turns")
        self.ax.set_ylabel("Total Number of Troops")

        self.fig2, self.ax2 = plt.subplots()
        self.ax2.set_title("Turns vs Number of Territories")
        self.ax2.set_xlabel("Turns")
        self.ax2.set_ylabel("Total Number of Territories")

        for player in players:
            line, = self.ax.plot([], [], color=player.color)
            line2, = self.ax2.plot([], [], color=player.color)

            self.lines.append(line)
            self.lines2.append(line2)

            self.troop_count.append([players[0].num_troops])
            self.terr_count.append([len(player.controlled_territories)])


        # AutoScales on the x and y axes
        self.ax.set_autoscaley_on(True)
        self.ax.set_autoscalex_on(True)
        self.ax.grid()

        self.ax2.set_autoscaley_on(True)
        self.ax2.set_autoscalex_on(True)
        self.ax2.grid()

    def update_chart(self, players, turn):
        self.turns.append(turn)
        for i in range(0, len(players)):
            self.troop_count[i].append(players[i].num_troops)
            self.lines[i].set_xdata(self.turns)
            self.lines[i].set_ydata(self.troop_count[i])

            self.terr_count[i].append(len(players[i].controlled_territories))
            self.lines2[i].set_xdata(self.turns)
            self.lines2[i].set_ydata(self.terr_count[i])

        # Need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()

        self.ax2.relim()
        self.ax2.autoscale_view()
        # We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

        self.fig2.canvas.draw()
        self.fig2.canvas.flush_events()


def gameplay(continents, players, deck):
    turn = 0
    chart = Chart(players)

    while(len(players)) > 1:
        turn += 1
        for player in players:
            # Draft Phase: This determines how many troops a player can draft
            if int(len(player.controlled_territories) / 3) > 3:
                drafted_troops = int(len(player.controlled_territories) / 3)
            else:
                drafted_troops = 3
            if turn == 1 and len(players) >= 4:
                if player == players[3]:
                    drafted_troops += 1
                if len(players) >= 5:
                    if player == players[4]:
                        drafted_troops += 2
                    if len(players) >= 6:
                        if player == players[5]:
                            drafted_troops += 3
            bonus = 0
            for continent in continents:
                for terr in continent.territories:
                    if terr.player_control != player:
                        bonus = 0
                        break
                    else:
                        bonus = continent.bonus
            drafted_troops += bonus

            # AI places troops now (Places troops randomly in all territories)
            for i in range(0, drafted_troops):
                drafted = 0
                while drafted == 0:
                    for terr in player.controlled_territories:
                        if random.random() * 400 < 1:
                            player.draft(terr)
                            drafted = 1
                            break

            # Attack Phase
            # AI does attack here (Attacks territories with maximum troops in territory randomly with all troops)
            for terr in player.controlled_territories:
                if terr.num_troops > 1:
                    for connection in terr.connections:
                        if connection.player_control != player:
                            if terr.num_troops > 4:
                                death = player.attack(terr, connection, 3)
                                for item in players:
                                    if item == death:
                                        players.remove(death)
                            elif terr.num_troops > 1:
                                death = player.attack(terr, connection, terr.num_troops-1)
                                for item in players:
                                    if item == death:
                                        players.remove(death)

            # print(player.color, player.num_troops)
            # print(len(player.controlled_territories))
            # for item in player.controlled_territories:
                # print(item.ID, item.num_troops)
            # Fortify Phase
            # AI fortifies here (Does not fortify)
        chart.update_chart(players, turn)



    print(players[0].color, "WINS in", turn, "Turns!")






continents = create_territories()
players = create_map(6, continents)
deck = Deck(continents)
gameplay(continents, players, deck)
