# ADSR placeholder
import numpy as np

def adsr(A, D, S, R, sr, length):
    total = int(length * sr)
    env = np.zeros(total)

    a = int(A * sr)
    d = int(D * sr)
    r = int(R * sr)
    s_start = a + d
    s_end = total - r

    env[:a] = np.linspace(0,1,a)
    env[a:s_start] = np.linspace(1,S,d)
    env[s_start:s_end] = S
    env[s_end:] = np.linspace(S,0,r)

    return env
