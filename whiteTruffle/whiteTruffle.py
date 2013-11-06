import socket
import copy
import random
import sys
import re
import copy
import math

programs = ["dlru", "dlur", "drlu", "drul", "dulr", "durl", "ldru", "ldur", "lrdu", "lrud", "ludr", "lurd", "rdlu", "rdul", "rldu", "rlud", "rudl", "ruld", "udlr", "udrl", "uldr", "ulrd", "urdl", "urld"];

def send(s, msg):
    print("sending")
    print(msg)
    msg += "\n<EOM>\n"
    totalsent = 0
    while totalsent < len(msg):
        sent = s.send(msg[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent

def receive(s, timeout=0):
    msg = ''
    while '<EOM>\n' not in msg:
        chunk = s.recv(1024)
        if not chunk:
          break
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
    newlyPlacedMunchers = []
    liveMunchers = []
    otherLiveMunchers = []
    lines = status.split()
    if lines[0] != '0':
        [num, munchedNodes] = lines[0].split(':')
        newlyPlacedMunchers = copy.deepcopy(munchedNodes)
        newlyPlacedMunchers = newlyPlacedMunchers.split(',')
        newlyPlacedMunchers = [newlyPlaced
                               for newlyPlaced in newlyPlacedMunchers
                               if '/' in newlyPlaced]
        newlyPlacedMunchers = [(int(mov.split('/')[0]), int(mov.split('/')[1]))
                               for mov in newlyPlacedMunchers]
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
    return (newlyPlacedMunchers, munched, liveMunchers, otherLiveMunchers, scores, remainingStuff)

def randomMove(munched, nodesToPlace):
    rand = int(random.randint(math.floor(remainingStuff[0]*0.5), remainingStuff[0]))
    print(rand)
    nextMove = str(rand+len(nodesToPlace))
    if rand == 0:
        return nextMove
    nextMove += ':'
    for node in nodesToPlace:
      if nodesToPlace in munched:
        continue
      munched.add(node)
      nextMove += '{0}/{1},'.format(node, programs[random.randint(1, 24) - 1])
    for i in xrange(rand):
        randNode = random.randint(1, len(nodes)) - 1
        while randNode in munched:
            randNode = random.randint(1, len(nodes)) - 1
        munched.add(randNode)
        nextMove += '{0}/{1},'.format(randNode, programs[random.randint(1, 24) - 1])
    nextMove = nextMove[:-1]
    print("nextMove")
    print(nextMove)
    return nextMove

if __name__ == '__main__':
  from nanoMuncherTracker import NanoMuncherTracker

  port = 4567
  print(sys.argv)
  if len(sys.argv) > 1:
    port = int(sys.argv[1])
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect(('127.0.0.1', port))

  try:
    send(s, 'whiteTruffle')
    (nodes, edges) = parseData(receive(s))
    tracker = NanoMuncherTracker(edges)
  
    munched = set()
    while(True):
        status = receive(s)
        print(status)
        if status in ['0', '']:
            break
        (newlyPlacedMunchers, newlyMunched, liveMunchers, otherLiveMunchers, scores, remainingStuff) = parseStatus(status)
        tracker.addNewMunchers(newlyPlacedMunchers, munched, newlyMunched, liveMunchers, otherLiveMunchers)
        munched.update(newlyMunched)

        # Remove munched references in edges
        for edge in edges:
          keysToRemove = []
          for (key, value) in edge.iteritems():
            if value in munched:
              keysToRemove = keysToRemove + [key]
          for key in keysToRemove:
            del edge[key]

        nodesToPlace = []
        for muncher in tracker.munchers:
          nodeToPlace = muncher.getPredictedNextNode(edges)
          if nodeToPlace is not None:
            nodesToPlace += [nodeToPlace]
        print("remaining munchers", remainingStuff[0])
        send(s, randomMove(munched, nodesToPlace))
  except:
    raise
  finally:
    print('Close socket')
    s.close()
