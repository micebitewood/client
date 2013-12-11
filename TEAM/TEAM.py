import socket
import random
import sys
import pdb
import networkx as nx
import time
import re
from itertools import combinations
from copy import deepcopy

PROGRAMS = {'all': ["dlru", "dlur", "drlu", "drul", "dulr", "durl", 
                    "ldru", "ldur", "lrdu", "lrud", "ludr", "lurd", 
                    "rdlu", "rdul", "rldu", "rlud", "rudl", "ruld", 
                    "udlr", "udrl", "uldr", "ulrd", "urdl", "urld",
                    "ulur", "urul"],
             'd':  ["dlru", "dlur", "drlu", "drul", "dulr", "durl"],
             'l':  ["ldru", "ldur", "lrdu", "lrud", "ludr", "lurd"],
             'r':  ["rdlu", "rdul", "rldu", "rlud", "rudl", "ruld"],
             'u':  ["udlr", "udrl", "uldr", "ulrd", "urdl", "urld",
                    "ulur", "urul"]}

class Muncher():

    def __init__(self, start, nodes, edges, edges_data, munched, program=None, programs=None, player=1):
        self.node = start
        self.start = start
        self.score = 1
        self.player = player
        self.eaten = [self.node]
        self.program = ""
        self.program_no = 0
        self.counter = 0
        if not programs:
            self.programs = PROGRAMS['all']
        else:
            self.programs = programs
        self.program_scores = dict((program, 0) for program in self.programs)
        if program:
            self.program = program
        else:
            self._sort_programs_by_score(nodes, edges, edges_data, munched)
            self.set_program(0)

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
        self.node = -1
        return -1

    def is_disintegrated(self):
        return self.node == -1
    
    def get_pos(self):
        return self.node

    def get_best_local_greedy_score(self):
        return self.program_scores[self.programs[0]]

    def get_program_score_by_number(self, program_no):
        return self.program_scores[self.programs[program_no]]

    def get_program_score_by_program(self, program):
        return self.program_scores[program]

    def set_program(self, program_no):
        self.program_no = min(self.program_no, len(self.programs))
        self.program = self.programs[self.program_no]

    def _sort_programs_by_score(self, nodes, edges, edges_data, munched):
        for program in self.programs:
            clone = deepcopy(self)
            clone.program = program
            #PLAY GAME
            while (clone.next(munched, nodes, edges) != -1):
                pass
            self.program_scores[program] = clone.score
        self.programs.sort(key = lambda x : self.program_scores[x], reverse = True)

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

def test_run(munched, munchers, nodes, edges):
    munched_copy = deepcopy(munched)
    munchers_copy = deepcopy(munchers)
    #Play
    ended = False
    while(not ended):
        visited = []
        ended = True
        for m in munchers_copy:
            visited.append(m.next(munched_copy, nodes, edges))
            ended = ended and (m.node == -1)
        munched_copy.update(visited)
        #Store subset of good munchers, if did well overall
    return sum(map(lambda x: x.score, munchers_copy))

def direction_inverse(direction):
    if direction == "u":
        return "d"
    elif direction == "d":
        return "u"
    elif direction == "r":
        return "l"
    elif direction == "l":
        return "r"

def direction_win(enemy, us):
    if us == 'u' and enemy in ('l', 'd', 'r'):
        return True
    if us == 'l' and enemy in ('d', 'r'):
        return True
    elif us == 'l' and enemy == 'u':
        return False
    if us == 'd' and enemy == 'r':
        return True
    elif us == 'd' and enemy in ('u', 'l'):
        return False
    if us == 'r':
        return False

def random_unif(range):
    return random.randint(-range, range)

#x + y mod field
def int_mod_add(x, y, field):
    return int(round((x + y) % field))

#Return best (node, program, score) for nodes of interest sorted and maximized by score
def greedy_neighbor(munched, nodes, edges, edges_data, otherNewMunchers):
    #consider contains a list of munchers we can answer the enemy with
    consider = dict((m, []) for m in otherNewMunchers)
    for enemy in consider:
        replys = consider[enemy]
        #Look at immediate enemy nbh
        nbh = edges[enemy].values()
        for (enemy_direction, neighbor) in edges[enemy].iteritems():
            #Consider nodes around next node of enemy
            for (direction, node) in edges[neighbor].iteritems():
#                if node in nbh or node == enemy:
#                    continue
                if node not in munched and len(edges[neighbor].keys()) == 1:
                    m = Muncher(node, nodes, edges, edges_data, munched)
                    #Don't do it if we run into a small area immediately after
                    if m.get_best_local_greedy_score() > 3:
                        replys.append(m)
                #If we could move to win that move, do it
                #We have to invert the direction, becasue edges stores it in direction away from the key
                elif node not in munched and direction_win(enemy_direction, direction_inverse(direction)):
                    m = Muncher(node, nodes, edges, edges_data, 
                                      munched, programs=PROGRAMS[direction_inverse(direction)])
                    #Don't do it if we run into a small area immediately after
                    if m.get_best_local_greedy_score() > 3:
                        replys.append(m)

    #Ignore nodes that we cannot respond to 
    consider = dict((enemy, reply) for (enemy, reply) in consider.iteritems() if reply) 

    #The response in consider corresponding to the enemy muncher
    best_munchers = []
    best_munchers_ind = dict((enemy, 0) for enemy in consider.keys())
    best_score = -1 
    for trash in range(min(len(otherNewMunchers) * 10000, 100000)):
        #Randomly pick new replys per enemy
        munchers_ind = deepcopy(best_munchers_ind)
        for enemy in munchers_ind.keys():
            no_replys = len(consider[enemy])
            munchers_ind[enemy] = int_mod_add(munchers_ind[enemy], random_unif(no_replys), no_replys)
        
        #Create a run with these replys
        run = []
        for (enemy, ind) in munchers_ind.iteritems():
            m = deepcopy(consider[enemy][ind])
            #Permute program
            no_programs = len(m.programs)
            m.set_program(int_mod_add(m.program_no, random_unif(no_programs), no_programs))
            run.append(m)
        
        score = test_run(munched, run, nodes, edges)
        if score > best_score:
            best_munchers_ind = munchers_ind
            best_score = score
            best_munchers = run
    
    #Convert into a format the return function can use
    result = []
    for m in best_munchers:
        result.append((m.start, m.program))
        munched.add(m.start)

    return result

#Return best (node, program, score) for nodes of interest sorted and maximized by score
def greedy_global(munched, nodes, edges, edges_data):
    ranking = []
    for node in range(len(nodes)):
#        if node == 90:
#            pdb.set_trace()
#        if node == 92:
#            pdb.set_trace()
        if not (node in munched):
            m = Muncher(node, nodes, edges, edges_data, munched)
            ranking.append((node, m.program, m.get_best_local_greedy_score()))
    ranking.sort(key=lambda x: x[2], reverse=True)

    return ranking

def greedyMove(munched,nodes,edges, edges_data, otherNewMunchers, round_no, subGs, liveMunchers, otherMunchers):
    move_string = str(0)
    node = 0
    program = ''

    if (remainingStuff[0] > 0 and otherNewMunchers):
        scorchers = greedy_neighbor(munched, nodes, edges, edges_data, otherNewMunchers)
        num_next = len(scorchers)
#        pdb.set_trace()
        num_g = len(otherNewMunchers) - len(scorchers)
        greedys = []
        for g in subGs:
            g.remove_nodes_from(munched)
        subGs.sort(key = lambda x: len(x), reverse=True)
        num_g = min(len(otherNewMunchers) - len(scorchers), len(greedys))
        move_string = str(num_next + num_g) + ':'
        for next_move in scorchers[:num_next]:
            move_string += str(next_move[0]) + "/" + str(next_move[1]) + ","
        if(len(liveMunchers) + len(otherMunchers) == 0):
            subGs.sort(key = lambda x: len(x), reverse=True)
            for g in subGs:
                sub_grs = greedy_global(munched, g.nodes(), edges, edges_data)
                no_sub_grs = int(min(num_g, round(float(len(g))/(len(nodes) - len(munched)) * num_g)))
                no_sub_grs = min(num_g, no_sub_grs)
                for n in sub_grs[:(no_sub_grs + 1)]:
                    greedys.append(n)
                num_g = num_g - no_sub_grs
                if num_g <= 0:
                    break
            random.shuffle(greedys)
            next_move = greedys[0]
            move_string += str(next_move[0]) + "/" + str(next_move[1]) + ","
        move_string = move_string[:-1]

    elif (remainingStuff[1] == 0 and remainingStuff[0] > 0):
        ranking = greedy_global(munched, nodes, edges, edges_data)
        num_next = remainingStuff[0]
        move_string = str(num_next) + ':'
        for next_move in ranking[:num_next]:
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
    nodes_owner = [0] * len(nodes)
    G = nx.Graph()
    G.add_edges_from(edges_data)
    subGs = nx.connected_component_subgraphs(G)
    round_no = 0
    munched = set()
    while(True):
        status = receive()
        print "Status: " + status
        if status == "0" or status == '':
            break
        (newlyMunched, liveMunchers, otherLiveMunchers, 
            otherNewMunchers, scores, remainingStuff) = parseStatus(status)
#        update_owner(newlyMunched, liveMunchers, otherLiveMunchers, nodes_owner)
        munched.update(newlyMunched)
        send(greedyMove(munched,nodes,edges, edges_data, otherLiveMunchers, round_no, subGs, liveMunchers, otherLiveMunchers))
        round_no += 1
    print remainingStuff[2]

