
from enum import Enum

class Action(Enum):
    PreStart = 0
    Up = 1
    Plateau = 2
    Down = 3
    Ended = 4

class FadeUpDown():
    def __init__(self, rampTime, startTime, upTime, sampleRate):
        self.sampleRate = sampleRate
        self.rampTime = rampTime
        self.startUpTime = startTime
        self.pos = 0
        self.startUpPos = int((startTime) * sampleRate)
        self.startDownPos = int((rampTime + upTime) * self.sampleRate)
        self.action = Action.PreStart

    def apply(self, to):
        if self.action == Action.PreStart and self.pos == self.startUpPos:
            self.pos = 0
            self.action = Action.Up

        if self.action == Action.Plateau and self.pos == self.startDownPos:
            self.pos = 1
            self.action = Action.Down

        coeff = 1.0 * self.pos / (self.rampTime * self.sampleRate)

        self.pos += 1
        if self.action == Action.Plateau:
            return to

        if self.action == Action.Down:
            coeff = 1.0 - coeff

        if coeff > 1.0:
            coeff = 1.0
            self.action = Action.Plateau
        elif coeff < 0.0:
            coeff = 0.0
            self.action = Action.Ended

        return [s * coeff for s in to]
