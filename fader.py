
class FadeUpDown():
    def __init__(self, rampTime, startTime, upTime, sampleRate):
        self.sampleRate = sampleRate
        self.rampTime = rampTime
        self.startUpTime = startTime
        self.pos = 0
        self.startDownPos = int((rampTime + upTime) * self.sampleRate)
        self.isDown = False

    def apply(self, to):
        if self.pos == self.startDownPos:
            self.pos = 1
            self.isDown = True
        coeff = 1.0 * self.pos / (self.rampTime * self.sampleRate)
        self.pos += 1
        if coeff > 1.0:
            if not self.isDown:
                return to
            else:
                coeff = 1.0

        if self.isDown:
            coeff = 1.0 - coeff

        return [s * coeff for s in to]
