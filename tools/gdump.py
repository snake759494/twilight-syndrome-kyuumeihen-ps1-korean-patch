# CDB 엔트리별 TIM 모음표: python tools/gdump.py <CDB 경로...>  -> gfx/<이름>_e<k>.png
import sys,os;sys.path.insert(0,os.path.dirname(__file__))
from tim import parse,image
from cdb import entries
from lz import dec
from PIL import Image,ImageDraw
def blobs(e):
    o=0;r=[]
    end=len(e.rstrip(b'\0'))
    while o<end:
        try:d,o2=dec(e,o)
        except Exception:break
        if o2<=o:break
        r.append(d);o=o2
    return r
for f in sys.argv[1:]:
    b=open('orig/'+f,'rb').read()
    for k,(s,c) in enumerate(entries(b)):
        e=b[s*2048:(s+c)*2048]; bl=blobs(e); ims=[]
        for j,d in enumerate(bl):
            t=parse(d,0)
            if t:
                try:
                    im=image(t)
                    if im: ims.append((j,im))
                except Exception: pass
        print(f.split('/')[-1],k,c,'blobs',len(bl),'tims',len(ims))
        if not ims: continue
        W=1024; x=y=rh=0; pos=[]
        for j,im in ims:
            w,h=im.size
            if x+w>W: x=0;y+=rh+12;rh=0
            pos.append((x,y)); x+=w+4; rh=max(rh,h)
        sh=Image.new('RGB',(W,y+rh+12),(40,90,40)); d=ImageDraw.Draw(sh)
        for (px,py),(j,im) in zip(pos,ims): sh.paste(im,(px,py+10)); d.text((px,py),str(j),fill=(255,255,0))
        sh.save('gfx/%s_e%d.png'%(f.split('/')[-1][:-4],k))
