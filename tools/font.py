import struct,sys,os
sys.path.insert(0,os.path.dirname(__file__))
from lz import dec
from cdb import entries
TABS={'CAP5':(0x800959d4,0x31e),'CAP6':(0x80092be8,0x322),'CAP7':(0x80092a14,0x213),'CAP8':(0x800998a0,0x30c),'CAP9':(0x8009062c,0x2f7),'CAPA':(0x800926fc,0x2f4),'CAPH':(0x80083938,0x17a)}
def exe(cap):
    b=open('orig/%s.EXE'%cap,'rb').read(); return b,struct.unpack_from('<I',b,0x18)[0]-0x800
def table(cap):
    b,base=exe(cap); a,n=TABS[cap]
    return [struct.unpack_from('<II',b,a-base+8*i) for i in range(n)]
_k=None
def kfont_entry(i):
    global _k
    if _k is None: _k=open('orig/DAT/FONT/KFONT.CDB','rb').read()
    s,n=entries(_k)[i]; return _k[s*2048:(s+n)*2048]
FONT_ENTRY={'CAP5':2,'CAP6':3,'CAP7':0,'CAP8':5,'CAP9':6,'CAPA':4,'CAPH':7}
def find_entry(cap): return FONT_ENTRY[cap]
def glyphs(cap):
    t=table(cap); e=kfont_entry(find_entry(cap)); res=[]
    for p,w in t:
        out,_=dec(e,p-0x8001a200); res.append((w,[(out[i//2]>>(4*(i&1)))&15 for i in range(256)]))
    return res
