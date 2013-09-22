from pippi import dsp

def rhodes(total_time, freq=220.0, ampscale=0.5):
    partials = [
            # Multiple, amplitude, duration
            [1, 0.6, 1.0], 
            [2, 0.25, 0.35], 
            [3, 0.08, 0.15],
            [4, 0.005, 0.04],
        ]

    layers = []
    for plist in partials:
        partial = dsp.tone(freq=plist[0] * freq, length=total_time, amp=plist[1] * ampscale)

        env_length = (total_time * plist[2] * 2) / 32 
        wtable = dsp.wavetable('hann', int(env_length))
        wtable = wtable[int(env_length / 2):]
        wtable.extend([0 for i in range(total_time - len(wtable))])
        print env_length, len(wtable), dsp.flen(partial)
        
        partial = dsp.split(partial, 32)
        partial = [ dsp.amp(partial[i], wtable[i]) for i in range(len(partial)) ]
        layer = ''.join(partial)

        layers += [ layer ]

    out = dsp.mix(layers)
    noise = dsp.amp(dsp.bln(dsp.flen(out) * 2, 2000, 20000), 0.005)
    noise = dsp.fill(noise, dsp.flen(out))

    out = dsp.mix([out, noise])



    return out
