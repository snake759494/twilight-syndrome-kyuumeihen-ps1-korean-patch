import sys
sys.path.insert(0,'tools')
def chk(b,st,txt,w,m):
    m=dict(m)
    for i,c in enumerate(txt):
        x=b[st+i*w:st+i*w+w]
        if c in m:
            if m[c]!=x: return None
        else:
            if x in m.values(): return None
            m[c]=x
    return m
b=open(sys.argv[1],'rb').read(); w=int(sys.argv[2]); lines=sys.argv[3:]
for st in range(len(b)):
    m=chk(b,st,lines[0],w,{})
    if m is None: continue
    p=st+len(lines[0])*w; ok=True; m2=m
    for L in lines[1:]:
        f=None
        for gap in range(0,12):
            r=chk(b,p+gap,L,w,m2)
            if r is not None: f=(gap,r);break
        if not f: ok=False;break
        m2=f[1]; p=p+f[0]+len(L)*w
    if ok: print(hex(st), b[st:p].hex())
