import struct,numpy as np
from PIL import Image
def parse(b,o=0):
    """-> dict(bpp,clut(list of rows),img xy,w,h,data,end) or None"""
    if len(b)<o+20: return None
    m,fl=struct.unpack_from('<II',b,o)
    if m!=0x10 or fl&~0xb or (fl&7)>3: return None
    p=o+8; bpp=fl&3; clut=None; cpos=None
    if fl&8:
        ln,x,y,w,h=struct.unpack_from('<IHHHH',b,p)
        if ln!=12+w*h*2 or w==0 or h==0 or w>1024: return None
        clut=np.frombuffer(b,np.uint16,w*h,p+12).reshape(h,w); cpos=p; p+=ln
    if len(b)<p+12: return None
    ln,x,y,w,h=struct.unpack_from('<IHHHH',b,p)
    if ln!=12+w*h*2 or w==0 or h==0 or w>1024 or h>512 or len(b)<p+ln: return None
    return dict(bpp=bpp,clut=clut,cpos=cpos,ipos=p,x=x,y=y,w=w,h=h,data=b[p+12:p+ln],end=p+ln)
def c15(v):
    r=(v&31)<<3;g=((v>>5)&31)<<3;bl=((v>>10)&31)<<3
    return r,g,bl
def image(t,row=0):
    w16=t['w'];h=t['h'];d=np.frombuffer(t['data'],np.uint16).reshape(h,w16)
    if t['bpp']==2:
        v=d; rgb=np.stack([(v&31)<<3,((v>>5)&31)<<3,((v>>10)&31)<<3],-1).astype(np.uint8)
    else:
        if t['bpp']==0:
            idx=np.stack([(d>>(4*i))&15 for i in range(4)],-1).reshape(h,w16*4)
        elif t['bpp']==1:
            idx=np.stack([d&255,d>>8],-1).reshape(h,w16*2)
        else: return None
        pal=t['clut'][row] if t['clut'] is not None else np.arange(256,dtype=np.uint16)*0x421//16
        pal=np.array([c15(int(x)) for x in pal],np.uint8)
        rgb=pal[np.minimum(idx,len(pal)-1)]
    return Image.fromarray(rgb)
