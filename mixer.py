

class Mixer:
    def __init__(self, sink_L, sink_R, limiter, sample_rate):
        self.sink_L = sink_L
        self.sink_R = sink_R
        self.limiter = limiter
        self.sample_rate = sample_rate

    def _merge(self, b1, b2):
        return [[b1[i][0] + b2[i][0], b1[i][1] + b2[i][1]] for i in range(self.sample_rate)]

    def mix(self, audioFiles):
        done = False
        started = False
        t = 0

        while not done:
            doneAll = True
            b = [[0.0, 0.0]] * self.sample_rate
            for f in audioFiles:
                if not f.done:
                    doneAll = False
                    if f.occursInBlockStarting(t):
                        started = True
                        b = self._merge(f.nextBlock(t), b)
            b = [[self.limiter.apply(s[0]), self.limiter.apply(s[1])] for s in b]
            self.sink_L.write([s[0] for s in b])
            self.sink_R.write([s[1] for s in b])
            t += 1
            done = started and doneAll
