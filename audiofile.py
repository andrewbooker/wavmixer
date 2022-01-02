

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

    def up(self, to):
        if self.pos > self.sampleLength:
            return to
        coeff = 1.0 * self.pos / self.sampleLength
        v = [coeff * to[0], coeff * to[1]]
        self.pos += 1
        return v

    def down(self, to):
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
        self.done = fromT == end or (fromT + 1) >= end
        if fromT >= end:
            return [[0.0, 0.0]] * self.file.sampleRate()
        if (fromT + 1) >= end:
            remainder = int(self.file.sampleRate() * (end - fromT))
            buff = [[0.0, 0.0]] * (self.file.sampleRate() - remainder)
            fbuff = self._read(remainder)
            if self.crossfade == 0.0:
                return fbuff + buff
            xf = self.crossfade * self.file.sampleRate()
            fade = Fader(xf, remainder - xf)
            return [fade.down(s) for s in fbuff] + buff
        if self.samplesRead == 0 and (fromT + 1) >= self.mixStart:
            pre = int(self.file.sampleRate() * (self.mixStart - fromT))
            if self.mixStart > 0:
                pre -= int(self.crossfade * self.file.sampleRate())
            fbuff = self._read(self.file.sampleRate() - pre)
            buff = [[0.0, 0.0]] * pre
            b = buff + fbuff
            if self.crossfade == 0.0:
                return b
            fade = Fader(self.crossfade * self.file.sampleRate())
            if self.mixStart == 0:
                return [fade.up(s) for s in b]
            return buff + [fade.up(s) for s in fbuff]
        if fromT < self.mixStart:
            return [[0.0, 0.0]] * self.file.sampleRate()

        return self._read(self.file.sampleRate())
