import random

from GameSession import GameSession
from Model import (
    NewGameResponse, DecideRunning, DecideCompleted, DecideFailed, NextPerson
)

class Solution:
    def __init__(self, session: NewGameResponse):
        self.session = session
        self.frequencies = session.attributeStatistics.relativeFrequencies.copy()
        self.minCounts = {constraint.attribute: constraint.minCount for constraint in session.constraints}
        self.counts = {name: 0 for name in self.minCounts.keys()}
        self.targetPeople = 1000
        self.enteredPeople = 0
        self.rejectedPeople = 0

        self.tag = {}
        self.tag_reject = {}

        self.haveTag = False

    def decide(self, state: DecideRunning) -> bool:
        return True
