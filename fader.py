
from enum import Enum

class Action(Enum):
    Nothing = 0
    Up = 1
    Down = -1

class FadeUpDown():
    def __init__(self, rampTime, startTime, upTime, sampleRate):
        self.sampleRate = sampleRate
        self.rampTime = rampTime
        self.startUpTime = startTime
        self.pos = 0
        self.startUpPos = int((startTime) * sampleRate)
        self.startDownPos = int((rampTime + upTime) * self.sampleRate)
        self.action = Action.Nothing

    def apply(self, to):
        if self.action == Action.Nothing and self.pos == self.startUpPos:
            self.pos = 0
            self.action = Action.Up

        if self.pos == self.startDownPos:
            self.pos = 1
            self.action = Action.Down

        coeff = 1.0 * self.pos / (self.rampTime * self.sampleRate)

        self.pos += 1
        if self.action == Action.Nothing:
            return to

        if self.action == Action.Down:
            coeff = 1.0 - coeff

        if coeff > 1.0 or coeff < 0.0:
            self.action = Action.Nothing
            coeff = 1.0 if coeff > 1.0 else 0.0

        return [s * coeff for s in to]
