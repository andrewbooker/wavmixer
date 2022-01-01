

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
        self.mixStart = mixStart
        self.duration = duration

        if fileStart > 0:
            self.file.read(int(fileStart * self.file.sampleRate()))
        self.durationSamples = int(duration * self.file.sampleRate())
        self.samplesRead = 0
        self.done = False

    def __del__(self):
        self.file.close()

    def _read(self, length):
        self.samplesRead += length
        return [[s[0], s[1]] for s in self.file.read(length)]

    def occursInBlockStarting(self, t):
        return not self.done and ((t + 1) > self.mixStart)

    def nextBlock(self, fromT):
        end = self.mixStart + self.duration
        self.done = fromT == end or (fromT + 1) >= end
        if fromT >= end:
            return [[0.0, 0.0]] * self.file.sampleRate()
        if (fromT + 1) > end:
            self.done = True
            remainder = int(self.file.sampleRate() * (end - fromT))
            buff = [[0.0, 0.0]] * (self.file.sampleRate() - remainder)
            return self._read(remainder) + buff
        if self.samplesRead == 0 and (fromT + 1) > self.mixStart:
            pre = int(self.file.sampleRate() * (self.mixStart - fromT))
            buff = [[0.0, 0.0]] * pre
            return buff + self._read(self.file.sampleRate() - pre)
        if fromT < self.mixStart:
            return [[0.0, 0.0]] * self.file.sampleRate()

        return self._read(self.file.sampleRate())
