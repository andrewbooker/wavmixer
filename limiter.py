
class Limiter():
    def __init__(self, gain):
        self.threshold = 0.8
        self.assumedMax = 1.5
        self.gain = gain

    def apply(self, v):
        s = v * self.gain
        assumedMax = max(self.assumedMax, s)
        if abs(s) < self.threshold:
            return s

        r = self.threshold + ((abs(s) - self.threshold) * (1.0 - self.threshold) / (assumedMax - self.threshold))
        return -r if s < 0 else r
