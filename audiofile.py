

class FileReader():
    def sampleRate(self):
        return 44100

    def read(self, samples):
        pass

    def close(self):
        pass


class Fader():
    def __init__(self, sampleLength, startAt=0):
        self.sampleLength = sampleLength
        self.startAt = startAt
        self.pos = 0
        self.isUp = startAt == 0

    def isDone(self):
        return (self.pos - self.startAt) > self.sampleLength

    def apply(self, to):
        if self.isUp:
            if self.pos > self.sampleLength:
                return to
            coeff = 1.0 * self.pos / self.sampleLength
            v = [coeff * to[0], coeff * to[1]]
            self.pos += 1
            return v

        self.pos += 1
        if self.pos < self.startAt:
            return to
        coeff = 1.0 - (1.0 * (self.pos - self.startAt) / self.sampleLength)
        return [coeff * to[0], coeff * to[1]]


class AudioFile():
    def __init__(self, fqfn, fileReader, fileStart, mixStart, duration, crossfade=0.0):
        self.fqfn = fqfn
        self.file = fileReader
        self.fileStart = fileStart
        self.mixStart = mixStart
        self.duration = duration
        self.crossfade = crossfade
        self.fade = None

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
        return not self.done and ((t + 1) > self.mixStart)

    def nextBlock(self, fromT):
        end = self.mixStart + self.duration

        if fromT >= end:
            self.done = True
            return [[0.0, 0.0]] * self.file.sampleRate()

        if (fromT + 1) >= end:
            self.done = True
            remainder = int(self.file.sampleRate() * (end - fromT))
            buff = [[0.0, 0.0]] * (self.file.sampleRate() - remainder)
            fbuff = self._read(remainder)
            if self.crossfade == 0.0:
                return fbuff + buff
            xf = self.crossfade * self.file.sampleRate()
            self.fade = Fader(xf, remainder - xf)
            return [self.fade.apply(s) for s in fbuff] + buff

        if self.samplesRead == 0 and (fromT + 1 + self.crossfade) >= self.mixStart:
            pre = int(self.file.sampleRate() * (self.mixStart - fromT))
            if pre > self.crossfade * self.file.sampleRate():
                pre -= int(self.crossfade * self.file.sampleRate())
            fbuff = self._read(self.file.sampleRate() - pre)
            buff = [[0.0, 0.0]] * pre
            b = buff + fbuff
            if self.crossfade == 0.0:
                return b
            self.fade = Fader(self.crossfade * self.file.sampleRate())
            if self.mixStart == 0:
                return [self.fade.apply(s) for s in b]
            return buff + [self.fade.apply(s) for s in fbuff]

        if fromT < (self.mixStart - self.crossfade):
            return [[0.0, 0.0]] * self.file.sampleRate()

        b = self._read(self.file.sampleRate())
        if self.fade is None:
            return b
        return [self.fade.apply(s) for s in b]
