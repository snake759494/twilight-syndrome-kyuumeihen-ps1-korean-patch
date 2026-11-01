import sys,os,numpy as np
sys.path.insert(0,os.path.dirname(__file__))
from PIL import Image,ImageDraw,ImageFont
from font import glyphs
from cmap import ROWS
COMMON=''.join(ROWS)
def norm(a):
    a=np.asarray(a,np.float32)
    ys,xs=np.nonzero(a>0.3)
    if len(xs)==0: return np.zeros(24*24,np.float32)
    im=Image.fromarray((a*255).astype(np.uint8)).crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1)).resize((24,24),Image.BILINEAR)
    v=np.asarray(im,np.float32).ravel(); v-=v.mean(); n=np.linalg.norm(v); return v/n if n else v
def cands():
    cs=[]
    for hi in range(0x88,0xa0):
        for lo in list(range(0x40,0x7f))+list(range(0x80,0xfd)):
            try: cs.append(bytes([hi,lo]).decode('cp932'))
            except: pass
    for hi in range(0xe0,0xeb):
        for lo in list(range(0x40,0x7f))+list(range(0x80,0xfd)):
            try: cs.append(bytes([hi,lo]).decode('cp932'))
            except: pass
    cs+=list('々〆〇ヶ×○●◎△▲□■◇◆★☆♪※→←↑↓')
    return cs
_ref=None
FONTS=[('msgothic.ttc',0),('msmincho.ttc',0),('BIZ-UDGothicR.ttc',0),('YuGothM.ttc',0)]
def vec(a):
    v=np.asarray(a,np.float32).ravel(); v=v-v.mean(); n=np.linalg.norm(v); return v/n if n else v
def ref():
    global _ref
    if _ref is None:
        cache='ocr_ref2.npz'
        if os.path.exists(cache):
            z=np.load(cache,allow_pickle=True); _ref=(list(z['c']),z['m'])
        else:
            cs=cands(); ms=[]; lab=[]
            fl=[ImageFont.truetype('C:/Windows/Fonts/'+f,sz,index=ix) for f,ix in FONTS for sz in (14,15,16)]
            for c in cs:
                for f in fl:
                    im=Image.new('L',(16,16)); d=ImageDraw.Draw(im)
                    bb=d.textbbox((0,0),c,font=f); w=bb[2]-bb[0]; h=bb[3]-bb[1]
                    d.text(((16-w)//2-bb[0],(16-h)//2-bb[1]),c,font=f,fill=255)
                    ms.append(vec(np.asarray(im,np.float32)/255)); lab.append(c)
            _ref=(lab,np.array(ms,np.float32)); np.savez(cache,c=np.array(lab),m=_ref[1])
    return _ref
def shifts(a):
    ys,xs=np.nonzero(a>0.3)
    if len(xs)==0: return [a]
    cy=(ys.min()+ys.max())/2; cx=(xs.min()+xs.max())/2
    out=[]
    for dy in (-1,0,1):
        for dx in (-1,0,1):
            sy=int(round(7.5-cy))+dy; sx=int(round(7.5-cx))+dx
            out.append(np.roll(np.roll(a,sy,0),sx,1))
    return out
_b=None
def lvl1(c):
    try: k=c.encode('cp932')
    except Exception: return False
    return len(k)==2 and 0x889f<=(k[0]<<8|k[1])<=0x9872
def BIAS():
    global _b
    if _b is None:
        cs,_=ref(); _b=np.array([0.04 if lvl1(c) else 0 for c in cs],np.float32)
    return _b
def ocr(cap,lo=0xdc):
    g=glyphs(cap); cs,M=ref(); out={}
    for code in range(lo,len(g)):
        w,px=g[code]
        a=np.array([1.0 if v==0 else (0.6 if v in(1,2,3) else 0) for v in px],np.float32).reshape(16,16)
        S=np.stack([vec(x) for x in shifts(a)])
        sc=(M@S.T).max(1)+BIAS(); i=int(sc.argmax()); out[code]=(cs[i],float(sc[i]))
    return out
if __name__=='__main__':
    import json
    cap=sys.argv[1]; r=ocr(cap)
    print(''.join(v[0] for v in r.values()))
    print('low:',[(hex(k),v) for k,v in r.items() if v[1]<0.75])
