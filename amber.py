from pippi import dsp
from pippi import tune
import glob
import drums

notes = [ dsp.read(note).data for note in glob.glob('sounds/note*') ]

speeds = [ 1.0, 1.5, 2.0 ]
scale = tune.fromdegrees([1, 4, 5, 6, 8, 9], octave=3, root='e')
envs = ['line', 'tri', 'hann', 'phasor', 'impulse']
wforms = ['tri', 'saw', 'impulse', 'square']

layer = [ dsp.randchoose(notes) for i in range(40) ]
layer = [ dsp.pan(note, dsp.rand()) for note in layer ]
layer = [ dsp.amp(note, dsp.rand(0.1, 0.7)) for note in layer ]
layer = [ dsp.transpose(note, dsp.randchoose(speeds)) for note in layer ]
layer = [ dsp.pad(note, 0, dsp.mstf(dsp.rand(500, 2000))) for note in layer ]
layer = ''.join(layer)

dsp.write(layer, 'layer-amber')

lcurve = dsp.breakpoint([ dsp.rand() for l in range(100) ], 2000)
#lcurve = [ dsp.mstf(length * 80 + 160) for length in lcurve ]
lcurve = [ dsp.mstf(length * 400 + 30) for length in lcurve ]

out = ''

# Break curve into variable size groups
segments = []
count = 0
minseg = 1
maxseg = 20
while count < len(lcurve):
    segsize = dsp.randint(minseg, maxseg)
    seg = lcurve[count : count + segsize]
    segments += [ seg ]

    count += segsize

print len(segments)

# Transpose source guitar melody
speeds = [ 1.0, 1.5, 1.25, 1.333 ]
theme = [ dsp.transpose(note, dsp.randchoose(speeds)) for note in notes * 2 ] 


for i, seg in enumerate(segments):
    the_blip = dsp.amp(dsp.transpose(notes[0], 2.0 * dsp.randint(1, 3)), 0.4)
    blip = dsp.mix([ the_blip, dsp.amp(dsp.transpose(notes[0], 1.5 * dsp.randint(1, 4)), 0.4) ])

    segsounds = []
    for length in seg:
        sounds = [ dsp.cut(layer, dsp.randint(0, dsp.flen(layer) - length), length) for s in range(6) ]
        sounds = dsp.mix(sounds)
        segsounds += [ sounds ]

    blips = []
    for length in seg:
        ba = dsp.cut(blip, dsp.randint(0, dsp.flen(blip) / 4), length / 2)
        bb = dsp.cut(blip, dsp.randint(0, dsp.flen(blip) / 4), length / 2)

        b = dsp.mix([dsp.pan(ba, dsp.rand()), dsp.pan(bb, dsp.rand())])

        blips += [ dsp.pad(b, 0, length / 2) ]

    tlen = sum(seg)

    hats = drums.make(drums.hihat, [1] * len(seg), seg)

    def bass(amp, length):
        out = dsp.tone(length, wavetype='square', freq=tune.ntf('d', 1), amp=0.3)
        out = dsp.env(out, 'phasor')

        return out

    p = drums.eu(len(seg), 1)
    #print p, len(seg) == len(p)
    kicks = drums.make(bass, p, seg)

    note = theme[i % len(theme)]
    #if dsp.randint(0, 1) == 0:
    note = dsp.alias(note)

    if dsp.randint(0, 5) != 0:
        note = dsp.fill(note, tlen)

    layers = [
        ''.join(segsounds), 
        note, 
        dsp.alias(''.join(blips)), 
        dsp.amp(hats, 0.5), 
        ]

    if dsp.flen(kicks) > 0:
        layers += [ kicks ]

    sounds = dsp.mix(layers)

    out += sounds

dsp.write(out, 'amber')
