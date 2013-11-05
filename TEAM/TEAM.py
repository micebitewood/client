import socket
import random
import sys
import pdb
#import networkx as nx
import time
import re
from copy import deepcopy

programs = ["dlru", "dlur", "drlu", "drul", "dulr", "durl", "ldru", "ldur", "lrdu", "lrud", "ludr", "lurd", "rdlu", "rdul", "rldu", "rlud", "rudl", "ruld", "udlr", "udrl", "uldr", "ulrd", "urdl", "urld"];

class Muncher():

    def __init__(self, start, nodes, edges, edges_data, munched, program=None, player=1):
        self.node = start
        self.score = 1
        self.player = player
        self.eaten = [self.node]
        self.program = ""
        self.counter = 0
        if program == None:
            self.program = self._infer_program(nodes, edges_data)
        elif program == "best":
            (self.score, self.program) = self._best_program_by_score(nodes, edges, edges_data, munched)
        else:
            self.program = program

    def _infer_program(self):
        return "urld"

    #Return next node (may be same position), -1 if muncher disintegrated
    def next(self, munched, nodes, edges):
        if self.node == -1:
            return -1
        for i in range(4):
            maybe_next = edges[self.node].get(self.program[self.counter], -1)
            self.counter = (self.counter + 1) % 4
            if maybe_next != -1 and not(maybe_next in munched or maybe_next in self.eaten):
                self.node = maybe_next
                self.score = self.score + 1
                self.eaten.append(self.node)
                return self.node
        return -1

    def get_pos(self):
        return self.node

    #Return program with maximum score and score
    def _best_program_by_score(self, nodes, edges, edges_data, munched):
        best_score = -1
        best_program = ''
        for program in programs:
            #The proper way of doing this is to create a copy of self
            clone = deepcopy(self)
            clone.program = program

            #PLAY GAME
            while (clone.next(munched, nodes, edges) != -1):
                pass

            #TODO: all programs give the same score
            if clone.score >= best_score:
                best_score = clone.score
                best_program = program
                
        return (best_score, best_program)

def send(msg):
    print "sending"
    print "Send: " + msg
    msg += "\n<EOM>\n"
    totalsent = 0
    while totalsent < len(msg):
        sent = s.send(msg[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent

def receive():
    msg = ''
    while '<EOM>\n' not in msg:
        chunk = s.recv(1024)
        if not chunk: break
        if chunk == '':
            raise RuntimeError("socket connection broken")
        msg += chunk
    msg = msg[:-7]
    return msg

def parseData(data):
    isNode = False
    isEdge = False
    nodes = []
    edges = []
    edges_data = []
    for line in data.split():
        line = line.strip().lower()
        if 'nodeid,xloc,yloc' in line:
            isNode = True
        elif 'nodeid1' in line:
            isEdge = True
            edges = [dict() for i in xrange(len(nodes))]
        elif isEdge:
            [node1, node2] = map(int, line.split(','))
            edges_data.append([node1, node2])
            if nodes[node1][0] == nodes[node2][0]:
                if nodes[node1][1] > nodes[node2][1]:
                    edges[node1]['u'] = node2
                    edges[node2]['d'] = node1
                else:
                    edges[node1]['d'] = node2
                    edges[node2]['u'] = node1
            else:
                if nodes[node1][0] > nodes[node2][0]:
                    edges[node1]['l'] = node2
                    edges[node2]['r'] = node1
                else:
                    edges[node1]['r'] = node2
                    edges[node2]['l'] = node1
        elif isNode:
            temp = map(int, line.split(','))
            nodes.append((temp[1], temp[2]))
    return (nodes, edges, edges_data)

def parseStatus(status):
    munched = set()
    liveMunchers = []
    otherLiveMunchers = []
    otherNewMunchers = []
    lines = status.split()
    if lines[0] != '0':
        [num, munchedNodes] = lines[0].split(':')
        munchedNodes = map(int, re.split("[/,]", munchedNodes))
        for i in xrange(int(num)):
            munched.add(munchedNodes[i])
        for m in lines[0].split(':')[1].split(","):
            if "/" in m:
                otherNewMunchers.append(map(int, m.split("/")))
    if lines[1] != '0':
        [num, myMunchers] = lines[1].split(':')
        myMunchers = myMunchers.split(',')
        for i in xrange(int(num)):
            temp = myMunchers[i].split('/')
            liveMunchers.append((int(temp[0]), temp[1], int(temp[2])))
    if lines[2] != '0':
        [num, otherMunchers] = lines[2].split(':')
        otherMunchers = map(int, otherMunchers.split(','))
        for i in xrange(int(num)):
            otherLiveMunchers.append(otherMunchers[i])
    scores = map(int, lines[3].split(','))
    remainingStuff = map(int, lines[4].split(','))
    return (munched, liveMunchers, otherLiveMunchers, otherNewMunchers, scores, remainingStuff)

#Return best (node, program, score) for nodes of interest sorted and maximized by score
def greedy_neighbor(munched, nodes, edges, edges_data, otherNewMunchers):
    result = []
    for node in otherNewMunchers:
        node = node[1]
        #Look around current position of newly placed munchers
        ranking = []
        for neighbor in edges[node].values():
            if not (neighbor in munched):
                m = Muncher(neighbor, nodes, edges, edges_data, munched, "best")
                if m.score > 4:
                    ranking.append((neighbor, m.program, m.score))
        if not ranking:
            continue
        ranking.sort(key=lambda x: x[2], reverse=True)
        result.append(ranking[0])

    return result

#Return best (node, program, score) for nodes of interest sorted and maximized by score
def greedy_global(munched, nodes, edges, edges_data):
    ranking = []
    for node in range(len(nodes)):
        if not (node in munched):
            m = Muncher(node, nodes, edges, edges_data, munched, "best")
            ranking.append((node, m.program, m.score))
    ranking.sort(key=lambda x: x[2], reverse=True)

    return ranking

def greedyMove(munched,nodes,edges, edges_data, otherNewMunchers, round):
    move_string = str(0)
    node = 0
    program = ''
    if (remainingStuff[1] == 0 and remainingStuff[0] > 0):
        ranking = greedy_global(munched, nodes, edges, edges_data)
        num_next = remainingStuff[0]
        move_string = str(num_next) + ':'
        for next_move in ranking[:num_next]:
            move_string += str(next_move[0]) + "/" + str(next_move[1]) + ","
        move_string = move_string[:-1]
    if (remainingStuff[0]>0 and otherNewMunchers) or remainingStuff[2] < 1000:
        granking = greedy_global(munched, nodes, edges, edges_data)
        ranking = greedy_neighbor(munched, nodes, edges, edges_data, otherNewMunchers)
        num_next = len(ranking)
        num_g = len(otherNewMunchers) - len(ranking)
        move_string = str(num_next + num_g) + ':'
        for next_move in ranking[:num_next]:
	    print "Best score: ",next_move[2]
            move_string += str(next_move[0]) + "/" + str(next_move[1]) + ","
        for next_move in granking[:num_g]:
	    print "Best score: ",next_move[2]
            move_string += str(next_move[0]) + "/" + str(next_move[1]) + ","
        move_string = move_string[:-1]
    return move_string

#def update_owner(newly_munched, live_munchers, other_live_munchers, nodes_owner):
#    pass
    
if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', int(sys.argv[1])))
    send("TEAM")
    (nodes, edges, edges_data) = parseData(receive())
#    nodes_owner = [0] * len(nodes)
#    G = nx.Graph()
#    G.add_edges_from(edges_data)
    round = 0
    munched = set()
    while(True):
        status = receive()
        print "Status: " + status
        #TODO If the server sends a status that corresponds to nothing, the while loop will break here
        if status == "0" or status == '':
            break
        (newlyMunched, liveMunchers, otherLiveMunchers, 
            otherNewMunchers, scores, remainingStuff) = parseStatus(status)
#        update_owner(newlyMunched, liveMunchers, otherLiveMunchers, nodes_owner)
        munched.update(newlyMunched)
        send(greedyMove(munched,nodes,edges, edges_data, otherNewMunchers, round))
        round += 1
    print remainingStuff[2]

