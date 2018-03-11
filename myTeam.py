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
               first = 'OffensiveReflexAgent', second = 'OffensiveReflexAgent'):

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
    isFirst = self.index<2

    walls = gameState.getWalls()
    vertical = walls.height/2
    horizontal = walls.width/2


    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList()
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance

    my_x,my_y = myPos
    if isFirst and my_y > horizontal:
      features['right_side'] = -1
    elif isFirst and my_y <= horizontal:
      features['right_side'] = 1
    if not isFirst and my_y > horizontal:
      features['right_side'] = 1
    elif not isFirst and my_y <= horizontal:
      features['right_side'] = -1

    if my_x > vertical:
      features['attacking']=1
    else:
      features['attacking']=0

    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    ghost_dists = [self.getMazeDistance(myPos,ghost.getPosition()) for ghost in enemies if ghost.getPosition()!=None]
    invaders = [enemy for enemy in enemies if enemy.isPacman and enemy.getPosition()!=0]
    pm_dists = [self.getMazeDistance(myPos,invader.getPosition()) for invader in invaders if invader.getPosition()!=None]

    if len(ghost_dists)>0 and features['attacking']==1:
      min_ghost_dist = min(ghost_dists)
      features['min_ghost_dist']=min_ghost_dist**2
    if len(pm_dists)>0 and features['attacking']==0:
      min_pm_dists = min(pm_dists)
      features['min_pm_dist']=min_pm_dists**2
    elif len(pm_dists)==0:
      features['dangerous'] = 1
    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1, 'right_side': 75, 'attacking': 100, 'min_ghost_dist':25,
            'min_pm_dist': -25, 'dangerous': -200}

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
    features['successorScore'] = self.getScore(successor)
    foodList = self.getFood(successor).asList()
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = 1/(max(dists)+1)**2

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}
class uberDefenseAgent(ReflexCaptureAgent):
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # nextPos = successor.getAgentState(self.index).getPosition()
    # features['onDefense'] f= 1
    # if myState.isPacman: eatures['onDefense'] = 0


    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    enemyPacmans = [a for a in enemies if not a.isPacman and a.getPosition!=None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)


    # if len(closeToEating)>0:
    #   features["closeToEating"]= min (closeToEating)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    if myState.isPacman and min([enemy.scaredTimer for enemy in enemyPacmans])!=0:
      features["can_eat"] = min([self.getMazeDistance(myPos,ghost.getPosition()) for ghost in enemyPacmans])

    return features  
  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'invaderDistance': -100, 'stop': -10, 'reverse': -2, 'successorScore': 100,
            'distanceToFood': -1, 'closeToEating': -100, 'can_eat': -30}
