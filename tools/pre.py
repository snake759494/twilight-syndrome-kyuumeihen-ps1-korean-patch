import importlib,emu,types; importlib.reload(emu); e.shot=types.MethodType(emu.Emu.shot,e)
import types;e.read=types.MethodType(emu.Emu.read,e)
import time,numpy as np
from PIL import Image
def wait_vis(out,tries=20,dt=2,th=6):
    for i in range(tries):
        e.shot(out); m=np.asarray(Image.open(out).convert('L')).mean()
        if m>th: return i,m
        time.sleep(dt)
    return None
def tap(k,n=1,dt=0.6,hold=0.15):
    for i in range(n): e.key(k,hold=hold); time.sleep(dt)
REF_T=np.asarray(Image.open('states/ref_title.png').convert('L'),np.int16)
def is_title(p):
    a=np.asarray(Image.open(p).convert('L'),np.int16)
    return np.abs(a[600:720,240:700]-REF_T[600:720,240:700]).mean()<12
def goto_title(maxt=60):
    for i in range(maxt):
        if e.shot('shots/_t.png') and is_title('shots/_t.png'): return i
        time.sleep(2)
    return None
def text_present(p):
    a=np.asarray(Image.open(p).convert('RGB'),np.int16)
    reg=a[460:720,40:920]
    white=((reg[...,0]>200)&(reg[...,1]>200)&(reg[...,2]>200)).mean()
    return white
