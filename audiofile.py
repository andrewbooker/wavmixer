
SAMPLE_RATE = 44100


class FileReader():
    def read(self, samples):
        pass

    def close(self):
        pass


class AudioFile():
    def __init__(self, fqfn, fileReader, fileStart, mixStart, duration):
        self.fqfn = fqfn
        self.fileStart = fileStart
        self.durationSamples = int(duration * SAMPLE_RATE)
        self.samplesRead = 0
        self.start = mixStart
        self.file = fileReader
        if fileStart > 0.5:
            self.start = mixStart - 0.5
            self.file.read(int((fileStart - 0.5) * SAMPLE_RATE)) 
        self.done = False

    def __del__(self):
        self.file.close()

    def _read(self, length):
        self.samplesRead += length
        return [[s[0], s[1]] for s in self.file.read(length)]

    def occursInBlockStarting(self, t):
        return not self.done and ((t + 1) > self.start or (t + 0.5) > self.start)

    def nextBlock(self, fromT):
        if fromT < self.start:
            pre = int(SAMPLE_RATE * (self.start - fromT))
            print("starting with", self.fqfn, "from sample", pre, "at", fromT)
            buff = [[0.0, 0.0]] * pre
            if self.fileStart > 0.5:
                pr = self._read(int(SAMPLE_RATE * 0.5))
                for i in range(len(pr)):
                    buff[i][0] += pr[i][0] * (i / SAMPLE_RATE * 0.5) 
                    buff[i][1] += pr[i][1] * (i / SAMPLE_RATE * 0.5) 
            return buff + self._read(SAMPLE_RATE - pre)
        else:
            if self.samplesRead == 0:
                print("straight in with", self.fqfn, "at", fromT)
            d = self._read(SAMPLE_RATE)
            l = len(d)
            if l < SAMPLE_RATE:
                self.done = True
                print("done with", self.fqfn, "at", fromT)
                return d + ([[0.0, 0.0]] * (SAMPLE_RATE - l))
            elif self.samplesRead > self.durationSamples:
                self.done = True
                excess = self.samplesRead - self.durationSamples
                print("overshot", self.fqfn, "by", excess, "samples from", fromT)
                return d[:SAMPLE_RATE - excess] + ([[0.0, 0.0]] * excess)

            return d
