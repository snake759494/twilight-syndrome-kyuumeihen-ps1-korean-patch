import sys,os,glob,json
sys.path.insert(0,os.path.dirname(__file__))
from cdb import entries
from script import blocks,toks
from tok import parse
res=[]
for f in sorted(glob.glob('orig/DAT/**/*.CDB',recursive=True)):
    if 'KFONT' in f or 'HITO' in f: continue
    b=open(f,'rb').read()
    for k,(s,n) in enumerate(entries(b)):
        e=b[s*2048:(s+n)*2048]
        if not e: continue
        bl=blocks(e)
        if not bl or len(bl)<2: continue
        if not all(0xffff in toks(o) for _,_,o in bl): continue
        g=0; mx=0
        for _,_,o in bl:
            for kd,v in parse(toks(o)):
                if kd=='G': g+=1; mx=max(mx,v&0xfff)
        res.append((f.replace(os.sep,'/'),k,len(bl),g,hex(mx)))
for r in res: print(*r)
print(sum(r[3] for r in res))
