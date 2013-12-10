import socket
import random
import sys
import re
import time
from scipy.sparse.csgraph import connected_components

programs = ["uldr", "ulrd", "udlr", "udrl", "urld", "urdl", "ludr", "lurd", "ldur", "ldru", "lrud", "lrdu", "dulr", "durl", "dlur", "dlru", "drul", "drlu", "ruld", "rudl", "rlud", "rldu", "rdul", "rdlu"];
firstNames = ["Jaded", "Jaunty", "Jealous", "Jerky", "Jolly", "Joyful", "Juicy", "Jumpy", "Justifiable", "Juvenile"]
lastNames = ["Jam", "Janitor", "Jelly", "Jerk", "Jet", "Jitterbug", "Journalist", "Judge", "Juice", "Juxtaposition"]

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
    print 'receiving'
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
    adjmat = []
    for line in data.split():
        line = line.strip().lower()
        if 'nodeid,xloc,yloc' in line:
            isNode = True
        elif 'nodeid1' in line:
            isEdge = True
            edges = [dict() for i in xrange(len(nodes))]
            adjmat = [['' for x in xrange(len(nodes))] for x in xrange(len(nodes))]
            adjmatrix = [[0 for x in xrange(len(nodes))] for x in xrange(len(nodes))]
        elif isEdge:
            [node1, node2] = map(int, line.split(','))
            if nodes[node1][0] == nodes[node2][0]:
                if nodes[node1][1] > nodes[node2][1]:
                    edges[node1]['u'] = node2
                    edges[node2]['d'] = node1
                    adjmat[node1][node2] = 'u'
                    adjmat[node2][node1] = 'd'
                else:
                    edges[node1]['d'] = node2
                    edges[node2]['u'] = node1
                    adjmat[node1][node2] = 'd'
                    adjmat[node2][node1] = 'u'
            else:
                if nodes[node1][0] > nodes[node2][0]:
                    edges[node1]['l'] = node2
                    edges[node2]['r'] = node1
                    adjmat[node1][node2] = 'l'
                    adjmat[node2][node1] = 'r'
                else:
                    edges[node1]['r'] = node2
                    edges[node2]['l'] = node1
                    adjmat[node1][node2] = 'r'
                    adjmat[node2][node1] = 'l'
            adjmatrix[node1][node2] = 1
            adjmatrix[node2][node1] = 1
        elif isNode:
            temp = map(int, line.split(','))
            nodes.append((temp[1], temp[2]))
    return (nodes, edges, adjmat, adjmatrix)
        
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
    return nextMove

def updateIsMunched():
    for node in newlyMunched:
        for muncher in liveMunchers:
            if node != muncher[0]:
                isMunched[node] = 1

def updateMunched():
    for muncher in liveMunchers:
        isMunched[muncher[0]] = 1

def getMoves():
    updateIsMunched()
    updateAdjMatrix()
    n_comp, labels = connected_components(adjmatrix, False, 'weak', True)
    numMunchersToDeploy = getNumMunchersToDeploy()
    print numMunchersToDeploy
    updateMunched()
    munched.update(myMuncherPositions)
    nodesToCheck = []
    program_opp = []
    program_gen = []
    program = []
    if len(otherLiveMunchers) > 0:
        nodesToCheck = getOpponentsNeighborNodes()
        if len(nodesToCheck) > 0:
            munchers, prog, pathCount = getMunchers(nodesToCheck)
            munch = []
            program = []
            count = []
            for i in xrange(len(munchers)):
                if munchers[i] not in munch:
                    munch.append(munchers[i])
                    program.append(prog[i])
                    count.append(pathCount[i])
            program = zip(munch, program, count)
            program_opp = sorted(program, key = lambda prog: prog[2], reverse = True)
        #if len(nodesToCheck) < numMunchersToDeploy:
        components = getNLargestConnectedComponents(numMunchersToDeploy, n_comp, labels)
        nodesToCheck = []
        for component in components:
            if len(component) > 2:
                nodesToCheck.append(getNodesWithMinWeight(component))
            else:
                nodesToCheck.append(component)
        munchers, prog, pathCount = getMunchers(nodesToCheck)
        munch = []
        program = []
        count = []
        for i in xrange(len(munchers)):
            if munchers[i] not in munch:
                munch.append(munchers[i])
                program.append(prog[i])
                count.append(pathCount[i])
        program = zip(munch, program, count)
        program_gen = sorted(program, key = lambda prog: prog[2], reverse = True)
        print program_opp
        print program_gen
        if len(program_opp) > 0:
            program = []
            temp_opp = []
            temp_gen = []
            for prog in program_opp:
                if prog[2] > 0:
                    program.append(prog)
                else:
                    temp_opp.append(prog)
            for prog in program_gen:
                if prog[2] > 0:
                    program.append(prog)
                else:
                    temp_gen.append(prog)
            for prog in temp_opp:
                program.append(prog)
            for prog in temp_gen:
                program.append(prog)
        print program
    else:
        components = getNLargestConnectedComponents(numMunchersToDeploy, n_comp, labels)
        for component in components:
            if len(component) > 2:
                nodesToCheck.append(getNodesWithMinWeight(component))
            else:
                nodesToCheck.append(component)
        munchers, prog, pathCount = getMunchers(nodesToCheck)
        munch = []
        program = []
        count = []
        for i in xrange(len(munchers)):
            if munchers[i] not in munch:
                munch.append(munchers[i])
                program.append(prog[i])
                count.append(pathCount[i])
        program = zip(munch, program, count)
        program = sorted(program, key = lambda prog: prog[2], reverse = True)
    prog = []
    for item in program:
        prog.append(str(item[0]) + '/' + str(item[1]))
    #prog = ['{}/{}'.format(a, b) for a, b in zip(munchers, prog)]
    if len(otherLiveMunchers) > 0:
        if remainingStuff[0] >= numMunchersToDeploy:
            prog = prog[:numMunchersToDeploy]
        else:
            prog = prog[:remainingStuff[0]]
    else:
        prog = prog[:1]
    prog = str(len(prog))+':'+','.join(prog)
    print prog
    return prog

def getOpponentsNeighborNodes():
    nanos = []
    for node in otherLiveMunchers:
        n = edges[node].values()
        nds = list(n)
        for nd in n:
            if nd in munched:
                nds.remove(nd)
        if len(nds) == 1:
            nanos.append(nds)
    return nanos
    
def getMunchers(nodesToCheck):
    munchers = []
    prog = []
    pathCount = []
    #print nodesToCheck
    for set in nodesToCheck:
        bestNodeInSet = set[0]
        bestPathCountForSet = 0
        bestProgramForSet = programs[0]
        for node in set:
            bestPathCountForNode = 0
            bestProgramForNode = programs[0]
            countarr = []
            for program in programs:
                count = pathcount(node, program, munched.copy())
                countarr.append(count)
                if count > bestPathCountForNode:
                    bestPathCountForNode = count
                    bestProgramForNode = program
                    if bestPathCountForNode > bestPathCountForSet:
                        bestPathCountForSet = bestPathCountForNode
                        bestNodeInSet = node
                        bestProgramForSet = bestProgramForNode
            #print countarr
        munchers.append(bestNodeInSet)
        prog.append(bestProgramForSet)
        pathCount.append(bestPathCountForSet)
    return munchers, prog, pathCount

def pathcount(node, program, munched):
    count=0
    di=0
    nextnode=node
    if node in munched:
        return 0
    while len(edges[node])>0:
        for i,d in enumerate(program[di:]+program[:di]):
            if d in edges[node].keys():
                if edges[node][d] not in munched:
                    count+=1
                    nextnode=edges[node][d]
                    di=(di+i+1)%4
                    break
        if nextnode != node:
            munched.add(node)
            node=nextnode
        else: break
    return count

def getNodesWithMinWeight(component):
    nodes = []
    mn = sys.maxint
    for node in component:
        temp = sum(adjmatrix[node])
        if temp < mn:
            mn = temp
            nodes = []
            nodes.append(node)
        elif temp == mn:
            nodes.append(node)
    #print nodes
    return nodes

def getNumMunchersToDeploy():
    numMunchersToDeploy = 0
    shouldBeAtleastOne = True
    for muncher in liveMunchers:
        count = pathcount(muncher[0], muncher[1][muncher[2]:] + muncher[1][:muncher[2]], munched.copy())
        if count > 0:
            shouldBeAtleastOne = False
    if (len(otherLiveMunchers) == 0 and len(liveMunchers) == 0) or (len(liveMunchers) == 0 and ((remainingStuff[0] < remainingStuff[1]) or remainingStuff[1] == 0)):
        if remainingStuff[0] > 0:
            numMunchersToDeploy = 1
    elif len(liveMunchers) < len(otherLiveMunchers):
            numMunchersToDeploy = len(otherLiveMunchers) - len(liveMunchers)
            if remainingStuff[0] - numMunchersToDeploy < remainingStuff[1]:
                mumMunchersToDeploy = remainingStuff[1] - remainingStuff[0] - 1
    if numMunchersToDeploy == 0 and shouldBeAtleastOne:
        numMunchersToDeploy = 1
    return numMunchersToDeploy

def getNLargestConnectedComponents(numMunchersToDeploy, n_comp, labels):
    order = []
    components = []
    for i in xrange(n_comp):
        indices = [j for j, x in enumerate(labels) if x == i]
        components.append(indices)
    components = sorted(components, key = len, reverse = True)
    components = components[:numMunchersToDeploy]
    return components

def updateAdjMatrix():
    for i in xrange(len(nodes)):
        for node in newlyMunched:
            if i == node:
                adjmat[i] = ['' for x in xrange(len(nodes))]
                adjmatrix[i] = [0 for x in xrange(len(nodes))]
                break;
            else:
                adjmat[i][node] = ''
                adjmatrix[i][node] = 0

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', int(sys.argv[1])))
send('ShriveledTurtleMan')
(nodes, edges, adjmat, adjmatrix) = parseData(receive())
isMunched = [0 for x in xrange(len(nodes))]
munched = set()
newlyMunched = set()
liveMunchers = []
myMuncherPositions = set()
otherLiveMunchers = []
remainingStuff = []
while(True):
    status = receive()
    print status
    #time.sleep(3)
    if status == '0' or status == '':
        break
    (newlyMunched, liveMunchers, otherLiveMunchers, scores, remainingStuff) = parseStatus(status)
    for muncher in liveMunchers:
        myMuncherPositions.add(muncher[0])
    munched.update(newlyMunched.difference(myMuncherPositions))
    print "remaining munchers", remainingStuff[0]
    send(getMoves())