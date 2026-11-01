# 모든 CDB의 라벨형(낮은 높이) TIM 수집 -> tmp/labels_N.png, tmp/labels.json
import sys,os,glob,json;sys.path.insert(0,os.path.dirname(__file__))
from tim import parse,image
from cdb import entries
from gfxpatch import blobs
from PIL import Image,ImageDraw
items=[]
for f in sorted(glob.glob('orig/DAT/**/*.CDB',recursive=True)):
    if 'FONT' in f or 'HITO' in f or 'CTLINK' in f: continue
    b=open(f,'rb').read(); p=f[5:].replace(os.sep,'/')
    for k,(s,c) in enumerate(entries(b)):
        for j,(o,o2,d) in enumerate(blobs(b[s*2048:(s+c)*2048])):
            t=parse(d,0)
            if not t or t['bpp']>1: continue
            im=image(t)
            if im and im.size[1]<=40 and im.size[0]>=24: items.append((p,k,j,im))
print(len(items))
W=1000; pages=[]; cur=[]; y=0; x=0; rh=0
meta=[]
for n,(p,k,j,im) in enumerate(items):
    w,h=im.size
    if x+w>W: x=0; y+=rh+12; rh=0
    if y+h+12>1400: pages.append(cur); cur=[]; x=y=rh=0
    cur.append((n,x,y,im)); meta.append([p,k,j]); x+=w+4; rh=max(rh,h)
pages.append(cur)
for i,pg in enumerate(pages):
    H=max(y+im.size[1]+12 for n,x,y,im in pg)
    sh=Image.new('RGB',(W,H),(40,90,40)); d=ImageDraw.Draw(sh)
    for n,x,y,im in pg: sh.paste(im,(x,y+10)); d.text((x,y),str(n),fill=(255,255,0))
    sh.save('tmp/labels_%d.png'%i)
json.dump(meta,open('tmp/labels.json','w'))
print(len(pages))
