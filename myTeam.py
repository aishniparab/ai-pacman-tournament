# baselineTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util
from game import Directions, Actions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'JamesBond', second = 'JamesBond'):

  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)

    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList()
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance

    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    ghostPacman = [a for a in enemies if a.isPacman and a.getPosition() != None]
    ghostEnemy = [a for a in enemies if not a.isPacman and a.getPosition() != None]

    #if pacman is trying to eat pellets and there is a ghost being mean
    #get distance to closest ghost
    """dist2ghost = []
    if successor.getAgentState(self.index).isPacman:
        if len(ghostEnemy) > 0:
            for ghost in ghostEnemy:
                dist2ghost.append(self.getMazeDistance(myPos, ghost.getPosition()))
            features['dist2ghost'] = min(dist2ghost)"""

    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1}

class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}

class JamesBond(ReflexCaptureAgent):
    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        vectorPos = Actions.directionToVector(action)
        walls = gameState.getWalls()
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()
        x1,y1 = myPos
        x2, y2 = vectorPos
        nextPos = int(x1+x2), int(y1+y2)

        if self.index > 2:
            direction = 1
        else:
            direction = self.index+1

        food = self.getFood(gameState)
        foodList = food.asList()
        foodGoal = []
        if len(foodList) > 0:
            for f_x,f_y in foodList:
                if (f_y > direction * walls.height/2 and f_y < (direction+1)*walls.height/2):
                    foodGoal.append((f_x, f_y))
            if len(foodGoal) == 0:
                foodGoal = foodList
            if min([self.getMazeDistance(myPos, f) for f in foodGoal]) is not None:
                features['distanceToFood'] = float(min([self.getMazeDistance(myPos,f) for f in foodGoal]))/(walls.width*walls.height)

        if action == Directions.STOP: features['stop'] = 1

        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        ghostPacman = [a for a in enemies if a.isPacman and a.getPosition() != None]
        ghostEnemy = [a for a in enemies if not a.isPacman and a.getPosition() != None]

        if myState.scaredTimer == 0:
            if len(ghostPacman) > 0:
                dist2enemyPac = [self.getMazeDistance(myPos, a.getPosition()) for a in ghostPacman]
                features['attackEnemyPacman'] = min(dist2enemyPac)
        else:
            for ghost in enemies:
                if ghost.getPosition() != None:
                    if nextPos == ghost.getPosition():
                        features['attack'] = -16
                    elif nextPos in Actions.getLegalNeighbors(ghost.getPosition(), walls):
                        features['caveat'] += -8

        for ghost in ghostEnemy:
            if myState.isPacman and ghost.scaredTimer > 0:
                dist2enemyGhost = [self.getMazeDistance(myPos, a.getPosition()) for a in ghostEnemy]
                features['eatGhost'] = min(dist2enemyGhost)
            elif myState.isPacman and nextPos in Actions.getLegalNeighbors(ghost.getPosition(), walls) or nextPos == ghost.getPosition():
                dist2ghost = [self.getMazeDistance(myPos, a.getPosition()) for a in ghostEnemy]
                features['runFromGhost'] = max(dist2enemyGhost)
            else:
                features['attackEnemyPacman'] = min([self.getMazeDistance(myPos, a.getPosition()) for a in ghostEnemy])

        features.divideAll(10)
        return features

    def getWeights(self, gameState, action):
        return {'distanceToFood': -1, 'attackEnemyPacman': -15, 'attack': -3, 'caveat':3, 'eatGhost':-20 , 'runFromGhost':-30 , 'stop': -3}
