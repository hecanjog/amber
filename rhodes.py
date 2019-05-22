from pippi import dsp, oscs, noise

def rhodes(total_time, freq=220.0, ampscale=0.5):
    freq *= 2**dsp.randint(0, 2)
    partials = [
            # Multiple, amplitude, duration
            [1, 0.6, 1.0], 
            [2, 0.25, 0.35], 
            [3, 0.08, 0.15],
            [4, 0.005, 0.04],
        ]

    layers = []
    for plist in partials:
        #env_length = (total_time * plist[2] * 2) / 32 
        partial = oscs.Osc('sine', freq=plist[0] * freq, amp=plist[1] * ampscale).play(total_time).env('hannout')
        
        #partial = dsp.split(partial, 32)
        #partial = [ dsp.amp(partial[i], wtable[i]) for i in range(len(partial)) ]
        #layer = ''.join(partial)

        layers += [ partial ]

    out = dsp.mix(layers)
    n = noise.bln('sine', out.dur, 2000, 20000) * 0.005

    out = dsp.mix([out, n])

    return out
