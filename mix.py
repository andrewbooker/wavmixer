#!/usr/bin/env python

import soundfile as sf
import sys
import os
from audiofile import AudioFile, FileReader
from limiter import Limiter
import json


SAMPLE_RATE = 44100


class SfReader(FileReader):
    def __init__(self, fqfn):
        self.file = sf.SoundFile(fqfn, "r")

    def read(self, samples):
        return self.file.read(samples)

    def close(self):
        self.file.close()


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

            outFileL.write([s[0] for s in b])
            outFileR.write([s[1] for s in b])
            t += 1
            done = started and doneAll


def parseLof(fqfn, substituteDir):
    files = []
    with open(fqfn, "r") as f:
        ls = f.readlines()
        for l in ls:
            s = float(l.split(" offset ")[1])
            f = os.path.join(substituteDir, os.path.basename(l.split("\"")[1]))
            files.append((f, s))
    return files


workingDir = sys.argv[1]
lofFn = sys.argv[2] if len(sys.argv) > 2 and "lof" in sys.argv[2].split(".")[1] else None
gain = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
outPrefix = sys.argv[4] if len(sys.argv) > 4 else "mixdown"
outFnPrefix = ""

audioFiles = []
if lofFn is not None:
    print("reading %s" % lofFn)
    outFnPrefix = os.path.join(os.path.dirname(workingDir), "%s_%s" % (outPrefix, os.path.basename(workingDir)))
    files = parseLof(lofFn, workingDir)
    for f in files:
        fqfn = f[0]
        data, sr = sf.read(fqfn)
        dur = len(data) / (1.0 * sr)
        audioFiles.append(AudioFile(fqfn, SfReader(fqfn), 0, f[1], dur))
else:
    cuesFn = sys.argv[2] if len(sys.argv) > 2 else os.path.join(workingDir, "cues.json")
    print("reading cues list %s" % cuesFn)
    outFnPrefix = os.path.join(workingDir, os.path.basename(cuesFn).split(".")[0])
    ac = open(cuesFn)
    cues = json.load(ac)
    ac.close()

    for c in cues:
        fqfn = os.path.join(workingDir, c["file"])
        audioFiles.append(AudioFile(fqfn, SfReader(fqfn), c["fileStart"], c["mixStart"], c["duration"], 0.75))

print("writing %s_(L|R).wav" % outFnPrefix)

outFileL = sf.SoundFile("%s_L.wav" % outFnPrefix, "w", samplerate=SAMPLE_RATE, channels=1)
outFileR = sf.SoundFile("%s_R.wav" % outFnPrefix, "w", samplerate=SAMPLE_RATE, channels=1)
limiter = Limiter(gain, threshold=0.8, assumedMax=1.6)

mixer = Mixer(outFileL, outFileR, limiter)
mixer.mix(audioFiles)

outFileL.close()
outFileR.close()

for a in audioFiles:
    del a
