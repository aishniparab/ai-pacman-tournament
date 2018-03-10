# myTeam.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, math
from game import Directions
import game
from util import nearestPoint

"""
DefensiveReflexAgent is same as baselineTeam. Only the OffensiveReflexAgent has been changed to a QLearningAgent
"""

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class QLearningAgent(CaptureAgent):
  """
  A base class for reflex agents that learns from experience
  """
  epsilon = float(0.05)
  discountRate = float(0.8)
  numTraining = int(10)

  qValues = util.Counter()

  def _init_(self, index, timeForComputing):
      CaptureAgent.__init__(self, index, timeForComputing)


  def getQValue(self, state, action):
      """
      Returns Q(state, action)
      """
      if (state,action) not in self.qValues:
          self.qValues[(state,action)] = 0.0
          return 0.0
      else:
          return self.qValues[(state,action)]

  def getValue(self, state):
      """
      Returns max_action Q(state,action)
      max over legal actions.
      """
      if len(state.getLegalActions(self.index)) == 0:
          return 0.0
      utility = util.Counter()
      for action in state.getLegalActions(self.index):
          qValue = self.getQValue(state,action)
          utility[action] = qValue
      return utility[utility.argMax()]

  def getPolicy(self, state):
      """
      compute the best action to take in a state.
      """

      maxUtility = float("-inf")
      policy = None
      legalActions = state.getLegalActions(self.index)
      if len(legalActions) == 0:
          return None
      for action in legalActions:
          qValue = self.getQValue(state, action)
          if qValue > maxUtility:
              maxUtility = qValue
              policy = action
      return policy

  def chooseAction(self, state):
      """
      compute action to take in the current state
      """
      legalActions = state.getLegalActions(self.index)
      action = None

      prob = util.flipCoin(float(0.05))
      if prob:
          action = random.choice(legalActions)
      else:
          action = self.getPolicy(state)

      return action

  def update(self, action, nextState, reward):
      alpha = self.alpha
      discountRate = self.discountRate
      qValue = self.getQValue(state,action)
      nextUtility = self.getValue(nextState)

      self.qValues[(state,action)] = ((1-alpha) * qValue) + alpha * (reward + discountRate * nextUtility)

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

class OffensiveReflexAgent(QLearningAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  """def __init__(self, index, timeForComputing):
      QLearningAgent.__init__(self, index, timeForComputing)"""

  def playOptimally(self, gameState):
      action = self.chooseAction(gameState)
      features = util.Counter()
      successor = self.getSuccessor(gameState, action)
      features['successorScore'] = self.getScore(successor)

      # Compute distance to the nearest food
      foodList = self.getFood(successor).asList()
      if len(foodList) > 0: # This should always be True,  but better safe than sorry
        myPos = successor.getAgentState(self.index).getPosition()
        minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
        features['distanceToFood'] = minDistance
      return getFeatures

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1}

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)
    print actions
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
