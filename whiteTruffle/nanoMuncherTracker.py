import copy
import random
import operator

class NanoMuncherTracker:

  def __init__(self, edges):
    self.munchers = set()
    self.edges = edges
    self.munched = []
    self.newlyMunched = []
    self.liveMunchers = []
    self.otherLiveMunchers = []
    self.newlyPlacedMunchers = []

  def update(self):
    ourNodes = [node for (node, _, _) in self.liveMunchers]
    newlyPlacedOpponentNodes = [nodes for pairNodes in self.newlyPlacedMunchers for nodes in pairNodes]
    excludeNodes = ourNodes+newlyPlacedOpponentNodes
    opponentNodesToUpdate = [nodes
                             for nodes in self.newlyMunched
                             if nodes not in excludeNodes]

    secondaryNodeStorage = set()
    removeMunchers = set()
    unresolvedMunchers = set()
    for muncher in self.munchers:
      edgePoints = self.edges[muncher.lastLocation].values()
      possibleMove = set(edgePoints).intersection(self.newlyMunched)
      if len(possibleMove) == 0:
        removeMunchers.add(muncher)
      elif len(possibleMove) == 1:
        nextNode = possibleMove.pop()
        secondaryNodeStorage.add(nextNode)
        muncher.updatePath(nextNode)
        updatedStrategy = self.predictMove(muncher.previousLocation, muncher.lastLocation, muncher.strategy)
        if updatedStrategy is not None:
          muncher.updateStrategy(updatedStrategy)
      else:
        unresolvedMunchers.add(muncher)
    self.munchers.difference_update(removeMunchers)

    removeMunchers = set()
    for muncher in unresolvedMunchers:
      edgePoints = self.edges[muncher.lastLocation].values()
      possibleMove = set(edgePoints).intersection(self.newlyMunched)
      possibleMove.difference_update(secondaryNodeStorage)
      if len(possibleMove) == 0:
        removeMunchers.add(muncher)
      elif len(possibleMove) == 1:
        nextNode = possibleMove.pop()
        muncher.updatePath(nextNode)
        updatedStrategy = self.predictMove(muncher.previousLocation, muncher.lastLocation, muncher.strategy)
        if updatedStrategy is not None:
          muncher.updateStrategy(updatedStrategy)
    self.munchers.difference_update(removeMunchers)

  def addNewMunchers(self, newlyPlacedMunchers, munched, newlyMunched, liveMunchers, otherLiveMunchers):
    self.munched = munched
    self.newlyMunched = newlyMunched
    self.liveMunchers = liveMunchers
    self.otherLiveMunchers = otherLiveMunchers
    self.newlyPlacedMunchers = newlyPlacedMunchers
    self.update()

    for i in newlyPlacedMunchers:
      self.addNewMuncher(i[0], i[1])

  def addNewMuncher(self, placedNode, movedToNode):
    muncher = Munchers(placedNode, movedToNode)
    updatedStrategy = self.predictMove(muncher.previousLocation, muncher.lastLocation, muncher.strategy)
    if updatedStrategy is not None:
      muncher.updateStrategy(updatedStrategy)
      self.munchers.add(muncher)

  def predictMove(self, previousLocation, lastLocation, strategy):
    edge = self.edges[previousLocation]
    directionMoved = [direction
                      for (direction, node) in edge.items()
                      if node == lastLocation]
    if len(directionMoved) > 0:
      directionMoved = directionMoved[-1]

      inferiorDirections = set([direction
                                for direction in edge.keys()
                                if direction != directionMoved])
      strategy = self.updateStrategy(strategy, directionMoved, inferiorDirections)
      return strategy
    return None

  def updateStrategy(self, strategy, directionMoved, inferiorDirections):
    strategy = copy.deepcopy(strategy)
    previousInfo = strategy.get(directionMoved)
    if previousInfo != None:
      inferiorDirections.update(previousInfo)
    strategy.update({directionMoved:inferiorDirections})
    return strategy

class Munchers:

  def __init__(self, placedNode, movedToNode):
    self.lastLocation = movedToNode
    self.previousLocation = placedNode
    self.strategy = dict()
    self.predictedNextMove = []

  def updatePath(self, nextNode):
    self.previousLocation = self.lastLocation
    self.lastLocation = nextNode

  def updateStrategy(self, strategy):
    self.strategy = strategy

  def getPredictedNextNode(self, edges):
    possibleLocations = edges[self.lastLocation]
    deadEnds = set()

    for (key, value) in sorted(self.strategy.iteritems(), key=operator.itemgetter(1), reverse=True):
      if len(value) == 3:
        if key in possibleLocations.keys():
          return possibleLocations[key]
        else:
          deadEnds.add(key)
      elif len(value) == 2:
        if len(deadEnds) > 0:
          if key in possibleLocations.keys():
            return possibleLocations[key]
          else:
            deadEnds.add(key)
      elif len(value) == 1:
        if len(deadEnds) > 1:
          if key in possibleLocations.keys():
            return possibleLocations[key]
          else:
            deadEnds.add(key)

      remaining = set(possibleLocations.keys()).intersection(deadEnds) 
      if len(remaining) > 0 and len(remainig) < 3:
        return random.choice(possibleLocations.values())

    return None
