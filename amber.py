from pippi import dsp, oscs, tune, fx
from pippi.wavesets import Waveset
import glob
import drums
import rhodes

dsp.seed()

speeds = [ 1.0, 1.5, 1.25, 1.333, 2.0, 3.0 ]
envs = ['line', 'tri', 'hann', 'phasor', 'impulse']
wforms = ['tri', 'saw', 'impulse', 'square']
scale = tune.fromdegrees([1, 3, 4, 5, 3, 6, 8, 2, 9], octave=2, root='e', scale=tune.minor)
rmx = dsp.read('suitermx.wav')

BEAT = 0.2

out = dsp.buffer()

vary_sections = [ dsp.randint(7, 12) for vs in range(2) ]

def rotate(items, start=0, vary=False):
    if vary:
        start = dsp.randint(0, len(items))
    return items[-start % len(items):] + items[:-start % len(items)]

def mixdrift(snd):
    dsnd = snd.vspeed(dsp.win('sine', 1 - dsp.rand(0.005, 0.05), 1 + dsp.rand(0.005, 0.05)))
    snd = dsp.mix([ snd, dsnd * 0.75 ])
    return snd

def folds(length, pos, total_length):
    print('FOLDS', length, pos)
    freq = tune.ntf('e', octave=3)
    out = dsp.mix([ rhodes.rhodes(length, freq, 0.3) for freq in scale ])
    return mixdrift(out)

def blips(length, pos, total_length):
    print('BLIPS', length, pos)
    notes = [ rhodes.rhodes(dsp.rand(4, 7), freq, 0.3) for freq in scale ]

    the_blip = notes[0].speed(2.0 * dsp.randint(1, 3)) * 0.4
    blip = dsp.mix([ the_blip, notes[0].speed(1.5 * dsp.randint(1, 4)) * 0.4 ])

    out = dsp.buffer(length=length)
    for _ in range(dsp.randint(2, 6)):
        ba = blip.cut(dsp.rand(0, blip.dur / 4), length / 2).pad(dsp.rand(0, length))
        bb = blip.cut(dsp.rand(0, blip.dur / 4), length / 2).pad(dsp.rand(0, length))
        b = dsp.mix([ba.pan(dsp.rand()), bb.pan(dsp.rand())]).taper(0.01)
        b = fx.crush(b)
        b = mixdrift(b)
        out.dub(b)

    return out

def drumset(length, pos, total_length):
    print('DRUMSET', length, pos)

    if length < 10:
        div = dsp.choice([2,3,4])
    else:
        div = dsp.choice([4,6,8,12,16])

    beat = length / div
    seg = [ beat for _ in range(div) ]
    layers = []

    maxbeats = dsp.randint(len(seg) / 2, len(seg))
    hatpat = drums.eu(len(seg), maxbeats)

    hats = drums.make(drums.hihat, hatpat, seg) * 0.3
    hats = mixdrift(hats)

    if dsp.rand() > 0.5:
        hats = hats.cloud(length=length, grainlength=1.0/dsp.choice(scale))

    if dsp.rand() > 0.5:
        hats = mixdrift(hats)

    print('MADE HATS')
    layers += [ hats ]

    kpat = drums.eu(len(seg), maxbeats)
    kicks = drums.make(drums.kick, kpat, seg)

    if dsp.randint(0,1) == 1:
        kicks = kicks.cloud(length=length, grainlength=1.0/dsp.choice(scale))
    else:
        kdivs = dsp.randint(2, 4)
        kicks = kicks.cloud(length=length / kdivs, grainlength=(1.0/dsp.choice(scale)) * kdivs)

    if dsp.rand() > 0.5:
        kicks = mixdrift(kicks)

    layers += [ kicks * 0.4 ]

    maxbeats = dsp.randint(2, len(seg) / 2)
    clappat = drums.eu(len(seg), maxbeats)
    claps = drums.make(drums.clap, rotate(clappat, vary=True), seg)

    if dsp.randint(0,1):
        claps = claps.cloud(length=length, grainlength=1.0/dsp.choice(scale))
    else:
        cdivs = dsp.randint(2, 4)
        claps = claps.cloud(length=length / cdivs, grainlength=(dsp.choice(scale)) * cdivs)

    if dsp.rand() > 0.5:
        claps = mixdrift(claps)

    layers += [ claps * 0.4 ]

    drms = fx.softclip(dsp.mix(layers))
    if dsp.rand() > 0.5:
        return fx.lpf(drms, dsp.rand(500, 1000))
    else:
        return fx.bpf(drms, dsp.rand(500, 5000))

def bass_and_lead(length, pos, total_length):
    numbeats = int(length//BEAT)
    maxbeats = dsp.randint(2, 16)
    layers = []
    def bass(amp, length, oct=2):
        if amp == 0:
            return dsp.buffer(length=length)

        bass_note = dsp.choice(scale) * 0.25

        stack = Waveset(rmx, limit=dsp.randint(5, 20), offset=dsp.randint(0, 100))
        stack.normalize()
        out = oscs.Pulsar2d(stack, windows=['sine'], freq=bass_note).play(length) * dsp.rand(0.02, 0.2)
        out = fx.lpf(out, bass_note*2)

        return out.env('hannout').taper(dsp.MS*10)

    if dsp.rand() > 0.5:
        basses = bass(0.5, length, 1)
    else:

        bpat = drums.eu(numbeats, maxbeats)
        basses = drums.make(bass, bpat, [BEAT]*numbeats)

    layers += [ basses ]

    lead_note = dsp.choice(scale)
    stack = Waveset(rmx, limit=dsp.randint(5, 20), offset=dsp.randint(0, 100))
    stack.normalize()
    lead = oscs.Pulsar2d(stack, windows=['tri'], freq=lead_note*2, pulsewidth=dsp.win('rnd', 0.1, 1)).play(length/dsp.rand(1,5)).env('hannout').taper(0.01) * dsp.rand(0.02, 0.2)

    layers += [ lead ]

    return fx.norm(dsp.mix(layers), 1)

def arp_synth(length, pos, total_length):
    seg = [ BEAT for _ in range(int(length//BEAT)) ]
    def makeArps(seg, oct=3, reps=4):
        arp_degrees = [1,2,3,5,8,9,10]
        if dsp.randint(0,1) == 0:
            arp_degrees.reverse()

        arp_degrees = rotate(arp_degrees, vary=True)
        arp_notes = tune.fromdegrees(arp_degrees[:reps], octave=oct, root='e')

        arps = []

        arp_count = 0
        for arp_length in seg:
            arp_length /= 2
            arp_pair = arp_notes[ arp_count % len(arp_notes) ], arp_notes[ (arp_count + 1) % len(arp_notes) ]

            stack = Waveset(rmx, limit=dsp.randint(5, 20), offset=dsp.randint(0, 100))
            stack.normalize()
            arp_one = oscs.Pulsar2d(stack, windows=['tri'], freq=arp_pair[0]*dsp.choice([1,2]), pulsewidth=dsp.win('rnd', 0.1, 1)).play(arp_length).env('hannout').taper(0.01) * dsp.rand(0.02, 0.2)

            arp_two = oscs.Pulsar2d(stack, windows=['tri'], freq=arp_pair[1]*dsp.choice([1,2]), pulsewidth=dsp.win('rnd', 0.1, 1)).play(arp_length).env('hannout').taper(0.01) * dsp.rand(0.02, 0.2)
            arp_one.dub(arp_two)
            arps += [ arp_one ]
            arp_count += 2

        return dsp.join(arps).env('rnd').pan(dsp.rand())

    # Lead synth
    arps = dsp.mix([ makeArps(seg, dsp.randint(1,3), dsp.randint(3, 4)) for a in range(dsp.randint(1, 4)) ]) 
    arps = mixdrift(arps)

    return arps

def theme_synth(length, pos, total_length):
    notes = [ rhodes.rhodes(dsp.rand(4, 7), freq, 0.3) for freq in scale ]
    themes = [ [ note.speed(dsp.choice(speeds)) for note in notes * 2 ] for theme in range(8) ]
    theme = dsp.choice(themes)
    theme_note = dsp.choice(theme)

    note = fx.crush(theme_note)

    return fx.lpf(fx.softclip(note), dsp.win('rnd', 1000, 5000))

def grain_synth(length, pos, total_length):
    notes = [ rhodes.rhodes(dsp.rand(4, 7), freq, 0.3) for freq in scale ]
    themes = [ [ note.speed(dsp.choice(speeds)) for note in notes * 2 ] for theme in range(8) ]
    theme = dsp.choice(themes)
    theme_note = dsp.choice(theme)

    def makeGrains(snd):
        envs = ['tri', 'phasor', 'rsaw', 'sine', 'hann']
        grains = []
        for g in snd.grains(dsp.MS*20, dsp.MS*90):
            g = g.env('hann').pan(dsp.rand()).taper(dsp.MS*4)
            grains += [ g ]

        rgrains = []
        while len(grains) > 0:
            r = grains.pop(dsp.randint(0, len(grains)-1))
            rgrains += [ r ]

        out = dsp.join(rgrains)
        out = out.env(dsp.choice(envs))

        return out

    if dsp.rand() > 0.5:
        gnote = theme_note.speed(1.5)
    else:
        gnote = theme_note

    grains = [ makeGrains(gnote) for g in range(dsp.randint(4, 10)) ]
    for gi, grain in enumerate(grains):
        if dsp.rand() > 0.5:
            grains[gi] = grain.speed(2).taper(0.01).repeat(2)

    grains = dsp.mix(grains)
    grains = grains * dsp.rand(0.25, 0.55)
    grains = mixdrift(grains)

    return grains

def stutter(sounds):
    grains = []
    for g in sounds.grains(dsp.MS*1, dsp.MS*200):
        g.taper(dsp.MS*4).pad(end=dsp.MS*dsp.rand(50, 250))
        grains += [ g ]
    return dsp.join(grains)

ORC = dict(
        folds=folds, 
        blips=blips, 
        drumset=drumset, 
        bass=bass_and_lead, 
        arp=arp_synth, 
        theme=theme_synth, 
        grain=grain_synth
    )

bars = dsp.win('sinc', 3, 40, 50)
total_length = sum(bars)

stems = {}
for stem, cb in ORC.items():
    stems[stem] = dsp.buffer(length=total_length)
    pos = 0
    print('STEM', stem)
    for i, l in enumerate(bars):
        l = 3 if l <= 0 else l
        bar = cb(l, pos, total_length)
        stems[stem].dub(bar, pos)
        pos += l      

    print('      %s normalize' % stem)
    stems[stem] = fx.norm(stems[stem], 1)
    print('      %s write' % stem)
    stems[stem].write('stem-%s.wav' % stem)

print()

print('MIXING', total_length)
out = dsp.buffer(length=total_length)
for stem, layer in stems.items():
    out.dub(layer)

print('COMPRESSING/WRITING', total_length)
out *= 10
out = fx.compressor(out, -10, 10)
out = fx.norm(out, 1)
out.write('amber-bars.wav')
