import sys,os,glob
sys.path.insert(0,'tools')
from tim import parse,image
from cdb import entries
from lz import dec
n=0
def scan(buf,tag):
    global n
    o=0
    while o<len(buf)-20:
        t=parse(buf,o)
        if t:
            try:
                im=image(t)
                if im and t['w']*t['h']>=256: im.save('gfx/%s_%x.png'%(tag,o)); n+=1
            except Exception as ex: pass
            o=t['end']
        else: o+=4
for f in glob.glob('orig/**/*',recursive=True):
    if os.path.isdir(f) or 'XA' in f or f.endswith('.EXE') or 'KFONT' in f: continue
    b=open(f,'rb').read(); tag=f[5:].replace(os.sep,'_').replace('/','_')
    scan(b,tag)
    if f.endswith('.CDB'):
        try: es=entries(b)
        except Exception: continue
        for k,(s,c) in enumerate(es):
            e=b[s*2048:(s+c)*2048]
            o=0;parts=[]
            try:
                while o<len(e) and len(parts)<64:
                    d,o2=dec(e,o)
                    if o2<=o: break
                    parts.append(d); o=o2
            except Exception: pass
            for j,d in enumerate(parts): scan(d,'%s_e%d_p%d'%(tag,k,j))
print(n)
