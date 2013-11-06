import socket
import random
import sys
import re
import time

programs = ["dlru", "dlur", "drlu", "drul", "dulr", "durl", "ldru", "ldur", "lrdu", "lrud", "ludr", "lurd", "rdlu", "rdul", "rldu", "rlud", "rudl", "ruld", "udlr", "udrl", "uldr", "ulrd", "urdl", "urld"];

def send(msg):
    print "sending"
    print msg
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
        chunk = s.recv(1)
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
    for line in data.split():
        line = line.strip().lower()
        if 'nodeid,xloc,yloc' in line:
            isNode = True
        elif 'nodeid1' in line:
            isEdge = True
            edges = [dict() for i in xrange(len(nodes))]
        elif isEdge:
            [node1, node2] = map(int, line.split(','))
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
    return (nodes, edges)
        
def parseStatus(status):
    munched = set()
    liveMunchers = []
    otherLiveMunchers = []
    lines = status.split()
    if lines[0] != '0':
        [num, munchedNodes] = lines[0].split(':')
        munchedNodes = map(int, re.split("[/,]", munchedNodes))
        for i in xrange(int(num)):
            munched.add(munchedNodes[i])
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
    return (munched, liveMunchers, otherLiveMunchers, scores, remainingStuff)

def randomMove(munched):
    rand = random.randint(0, remainingStuff[0])
    nextMove = str(rand)
    if rand == 0:
        return nextMove
    nextMove += ':'
    for i in xrange(rand):
        randNode = random.randint(1, len(nodes)) - 1
        while randNode in munched:
            randNode = random.randint(1, len(nodes)) - 1
        munched.add(randNode)
        nextMove += '{0}/{1},'.format(randNode, programs[random.randint(1, 24) - 1])
    nextMove = nextMove[:-1]
    print "nextMove"
    print nextMove
    return nextMove
#-----------------------------------------------------
class Path():
    def __init__(self):
        self.path = []
        self.program = 'rdlu'

def move(nodes,edges,munched,pos,program,path):
    for direction in program:
        if direction in edges[pos]:
            if edges[pos][direction] not in munched:
                if edges[pos][direction] not in path:
                    pos = edges[pos][direction]
                    return pos
    return None

# pos has to be not munched
def roadmap(nodes,edges,munched,pos,program):
    """
    find a path with given starting node and a muncher's program
    pos is the node number a muncher is placed. program is its program.
    """
    path = []
    path.append(pos)
    while True:
        pos = move(nodes,edges,munched,pos,program,path)
        if pos == None:
            break
        path.append(pos)
    return path

def compare_paths(path1,path2):
    i = 1
    while True:
        if len(path1) > i and len(path2) > i:
            if path1[i] == path2[i]:
                i+= 1
            else:
                break
        else: 
            break
    return i

def whim_path(nodes,edges,munched,pos):
    paths = []
    for program in programs:
        path = Path()
        path.program = program
        path.path = roadmap(nodes,edges,munched,pos,program)
        paths.append(path)

    longest = 0
    longest_path = Path()

    for path in paths:
        i = 2
        while i < len(path.path):
            if len(edges[path.path[i]]) > 2:
                for d in edges[path.path[i]]:
                    if edges[path.path[i]][d] != path.path[i] and edges[path.path[i]][d] not in munched:
                        if i > longest:
                            longest = i
                            longest_path = path
                            break
            else:
                break
            i+= 1
    return longest,longest_path

def find_longest(nodes,edges,munched,pos):
    paths = []
    for program in programs:
        path = Path()
        path.program = program
        path.path = roadmap(nodes,edges,munched,pos,program)
        paths.append(path)
    longest = 0
    longest_path = Path()
    for path in paths:
        if len(path.path) > longest:
            longest = len(path.path)
            longest_path = path
    return longest,longest_path

def graph_size(nodes,edges,munched,pos):
    nodes_set = set(range(0,len(nodes)))
    nodes_set = nodes_set - munched
    processed = []
    queue = [pos]
    while queue != []:
        source = queue.pop(0)
        processed.append(source)
        for d in edges[source]:
            if edges[source][d] in nodes_set:
                if edges[source][d] not in queue and edges[source][d] not in processed:
                    queue.append(edges[source][d])
    return processed

def basic_predict(otherLiveMunchers,munched,nodes,edges):
    if otherLiveMunchers != []:
        verdict = []
        for pos in otherLiveMunchers:
            i = 0
            for d in edges[pos]:
                if edges[pos][d] not in munched:
                    i+= 1
                    nextnode = edges[pos][d]
            if i == 1:
                j = 0
                for d in edges[nextnode]:
                    if edges[nextnode][d] not in munched:
                        j+= 1
                        nnextnode = edges[nextnode][d]
                if j == 1:
                    verdict.append(nnextnode)
        if verdict != []:
            return verdict
    return None

#-----------------------------------------------------
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', int(sys.argv[1])))
send('Gamma')
(nodes, edges) = parseData(receive())
munched = set()

#stat = {1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0,13:0,14:0,15:0,16:0,17:0,18:0,19:0,20:0,21:0,22:0,23:0,24:0,25:0}
#for pos in range(0,len(nodes) - 1):
#    print graph_size(nodes,edges,munched,pos)
#    length,path =  whim_path(nodes,edges,munched,pos)
#    print length,path.path
#        if len(path) in stat:
#            stat[len(path)]+= 1
#print stat

munched_longest = set()

while(True):
    status = receive()
    if status == '0' or status == '':
        break
    (newlyMunched, liveMunchers, otherLiveMunchers, scores, remainingStuff) = parseStatus(status)
    munched.update(newlyMunched)
    if remainingStuff[1] == 0:
        sendmove = ''
        longest = 0
        longest_path = Path()
        for pos in range(0,len(nodes) - 1):
            if pos not in munched:
                # longest path
                    if munched_longest == set():
                        munched_longest = munched.copy()
                    length,path = find_longest(nodes,edges,munched_longest,pos)
                    if longest < length:
                        longest = length
                        longest_path = path
        munched_longest = munched_longest.union(longest_path.path)
        sendmove = '1:' + str(longest_path.path[0]) + '/' + longest_path.program

    else:
        sendmove = ''
        # longest unpredictable path
        i = remainingStuff[0]
        future_munched = munched.copy()
        while i != 0:
            longest = 0
            longest_path = Path()
            for pos in range(0,len(nodes) - 1):
                if pos not in future_munched:
                    length,path = whim_path(nodes,edges,future_munched,pos)
                    if length >= 3:
                        tmp_munched = future_munched.copy()
                        tmp_munched.add(path.path[0])
                        subgraph = graph_size(nodes,edges,tmp_munched,path.path[1])
                        if len(subgraph) <= 3 * length and len(path.path) >= 2 * length:
                            if longest < len(path.path):
                                longest = len(path.path)
                                longest_path = path
            if longest != 0:
                future_munched = future_munched.union(longest_path.path)
                sendmove+= str(longest_path.path[0]) + '/' + longest_path.program + ','
                i-= 1
            else:
                break

        sendmove = str(remainingStuff[0] - i) + ':' + sendmove[:-1]
        if sendmove == '0:':
            add_move = ''
            verdict = basic_predict(otherLiveMunchers,munched,nodes,edges)
            if verdict != None:
                for node in verdict:
                    length,path = whim_path(nodes,edges,munched,node)
                    if length >= 3:
                        add_move = str(path.path[0]) + '/' + path.program

            longest = 0
            longest_path = Path()
            for pos in range(0,len(nodes) - 1):
                if pos not in munched:
                    length,path = whim_path(nodes,edges,munched,pos)
                    if longest < length:
                        longest = length
                        longest_path = path
            if add_move != '':
                print 'hunger'
                sendmove = '2:' + str(longest_path.path[0]) + '/' + longest_path.program + ',' + add_move
            else:
                sendmove = '1:' + str(longest_path.path[0]) + '/' + longest_path.program

    send(sendmove)
