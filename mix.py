#!/usr/bin/env python

import soundfile as sf
import sys
import os
from audiofile import AudioFile, FileReader
import json

class SfReader(FileReader):
    def __init__(self, fqfn):
        self.file = sf.SoundFile(fqfn, "r")

    def read(self, samples):
        return self.file.read(samples)

    def close(self):
        self.file.close()

class Limiter():
    def __init__(self):
        self.threshold = 0.8
        self.assumedMax = 1.5

    def apply(self, s):
        assumedMax = max(self.assumedMax, s)
        if abs(s) < self.threshold:
            return s

        r = self.threshold + ((abs(s) - self.threshold) * (1.0 - self.threshold) / (assumedMax - self.threshold))
        return -r if s < 0 else r

def merge(b1, b2, limiter):
    return [[limiter.apply(b1[i][0] + b2[i][0]), limiter.apply(b1[i][1] + b2[i][1])] for i in range(len(b1))]

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

outBase = "mix"
audioFiles = []
if lofFn is not None:
    print("reading %s" % lofFn)
    files = parseLof(os.path.join(workingDir, lofFn), workingDir)
    for f in files:
        fqfn = f[0]
        data, sr = sf.read(fqfn)
        dur = len(data) / (1.0 * sr)
        audioFiles.append(AudioFile(fqfn, SfReader(fqfn), 0, f[1], dur))
else:
    cuesFn = sys.argv[2] if len(sys.argv) > 2 else os.path.join(workingDir, "cues.json")
    print("reading cues list %s" % cuesFn)
    outBase = os.path.basename(cuesFn).split(".")[0]
    ac = open(cuesFn)
    cues = json.load(ac)
    ac.close()

    for c in cues:
        fqfn = os.path.join(workingDir, c["file"])
        audioFiles.append(AudioFile(fqfn, SfReader(fqfn), c["fileStart"], c["mixStart"], c["duration"], 0.75))

outDir = workingDir
print("writing %s_(L|R).wav" % outBase, "to", outDir)

    

SAMPLE_RATE = 44100
done = False
t = 0
outFileL = sf.SoundFile(os.path.join(outDir, "%s_L.wav" % outBase), "w", samplerate=SAMPLE_RATE, channels=1)
outFileR = sf.SoundFile(os.path.join(outDir, "%s_R.wav" % outBase), "w", samplerate=SAMPLE_RATE, channels=1)
started = False
limiter = Limiter()
while not done:
    doneAll = True
    b = [[0.0, 0.0]] * SAMPLE_RATE
    for f in audioFiles:
        if not f.done:
            doneAll = False
            if f.occursInBlockStarting(t):
                started = True
                b = merge(f.nextBlock(t), b, limiter)

    outFileL.write([s[0] * gain for s in b])
    outFileR.write([s[1] * gain for s in b])
    t += 1
    done = started and doneAll

outFileL.close()
outFileR.close()

for a in audioFiles:
    del a
