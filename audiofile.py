from fader import FadeUpDown


class FileReader():
    def sampleRate(self):
        return 44100

    def read(self, samples):
        pass

    def close(self):
        pass


class AudioFile():
    def __init__(self, fqfn, fileReader, fileStart, mixStart, duration, crossfade=0.0):
        self.fqfn = fqfn
        self.file = fileReader
        self.fileStart = fileStart
        self.mixStart = mixStart
        self.duration = duration
        self.crossfade = crossfade
        self.fadeUpDown = None

        if fileStart > 0:
            self.file.read(int((fileStart - crossfade) * self.file.sampleRate()))
        self.durationSamples = int(duration * self.file.sampleRate())
        self.samplesRead = 0
        self.done = False

    def __del__(self):
        self.file.close()

    def _read(self, length):
        self.samplesRead += length
        return [[s[0], s[1]] for s in self.file.read(length)]

    def occursInBlockStarting(self, t):
        return not self.done and ((t + 1 + self.crossfade) >= self.mixStart)

    def _readBlock(self, fromT):
        end = self.mixStart + self.duration

        if fromT >= end:
            self.done = True
            return [[0.0, 0.0]] * self.file.sampleRate()

        if (fromT + 1) >= end:
            self.done = True
            remainder = int(self.file.sampleRate() * (end - fromT))
            buff = [[0.0, 0.0]] * (self.file.sampleRate() - remainder)
            fbuff = self._read(remainder)
            return fbuff + buff

        if self.samplesRead == 0 and (fromT + 1 + self.crossfade) >= self.mixStart:
            if self.crossfade != 0.0 and self.fadeUpDown is None:
                startRamp = self.mixStart - fromT
                if startRamp > self.crossfade:
                    startRamp -= self.crossfade
                self.fadeUpDown = FadeUpDown(self.crossfade, startRamp, self.duration - self.crossfade, self.file.sampleRate())

            pre = int(self.file.sampleRate() * (self.mixStart - fromT))
            if pre > self.crossfade * self.file.sampleRate():
                pre -= int(self.crossfade * self.file.sampleRate())
            fbuff = self._read(self.file.sampleRate() - pre)
            buff = [[0.0, 0.0]] * pre
            return buff + fbuff

        if fromT < (self.mixStart - self.crossfade):
            return [[0.0, 0.0]] * self.file.sampleRate()

        return self._read(self.file.sampleRate())

    def nextBlock(self, fromT):
        b = self._readBlock(fromT)
        if self.fadeUpDown is not None:
            return [self.fadeUpDown.apply(s) for s in b]
        return b
