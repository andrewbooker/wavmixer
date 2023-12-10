SAMPLE_RATE = 44100


class Mixer:
    def __init__(self, sink_L, sink_R, limiter):
        self.sink_L = sink_L
        self.sink_R = sink_R
        self.limiter = limiter

    def _merge(self, b1, b2):
        return [[self.limiter.apply(b1[i][0] + b2[i][0]), self.limiter.apply(b1[i][1] + b2[i][1])] for i in range(len(b1))]

    def mix(self, audioFiles):
        done = False
        started = False
        t = 0

        while not done:
            doneAll = True
            b = [[0.0, 0.0]] * SAMPLE_RATE
            for f in audioFiles:
                if not f.done:
                    doneAll = False
                    if f.occursInBlockStarting(t):
                        started = True
                        b = self._merge(f.nextBlock(t), b)

            self.sink_L.write([s[0] for s in b])
            self.sink_R.write([s[1] for s in b])
            t += 1
            done = started and doneAll
