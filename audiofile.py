

class FileReader():
    def sampleRate(self):
        return 44100

    def read(self, samples):
        pass

    def close(self):
        pass


class AudioFile():
    def __init__(self, fqfn, fileReader, fileStart, mixStart, duration):
        self.fqfn = fqfn
        self.file = fileReader
        self.fileStart = fileStart
        self.durationSamples = int(duration * self.file.sampleRate())
        self.samplesRead = 0
        self.start = mixStart
        if fileStart > 0.5:
            self.start = mixStart - 0.5
            self.file.read(int((fileStart - 0.5) * self.file.sampleRate()))
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
            pre = int(self.file.sampleRate() * (self.start - fromT))
            print("starting with", self.fqfn, "from sample", pre, "at", fromT)
            buff = [[0.0, 0.0]] * pre
            if self.fileStart > 0.5:
                pr = self._read(int(self.file.sampleRate() * 0.5))
                for i in range(len(pr)):
                    buff[i][0] += pr[i][0] * (i / self.file.sampleRate() * 0.5)
                    buff[i][1] += pr[i][1] * (i / self.file.sampleRate() * 0.5)
            return buff + self._read(self.file.sampleRate() - pre)
        else:
            if self.samplesRead == 0:
                print("straight in with", self.fqfn, "at", fromT)
            d = self._read(self.file.sampleRate())
            l = len(d)
            if l < self.file.sampleRate():
                self.done = True
                print("done with", self.fqfn, "at", fromT)
                return d + ([[0.0, 0.0]] * (self.file.sampleRate() - l))
            elif self.samplesRead > self.durationSamples:
                self.done = True
                excess = self.samplesRead - self.durationSamples
                print("overshot", self.fqfn, "by", excess, "samples from", fromT)
                return d[:self.file.sampleRate() - excess] + ([[0.0, 0.0]] * excess)

            return d
