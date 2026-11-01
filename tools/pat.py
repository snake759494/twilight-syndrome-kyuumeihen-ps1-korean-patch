import sys
def find(b,txt,w):
    n=len(txt); res=[]
    for st in range(0,len(b)-n*w):
        if w==2 and st%1: pass
        v=[b[st+i*w:st+i*w+w] for i in range(n)]
        ok=True;m={}
        for c,x in zip(txt,v):
            if c in m:
                if m[c]!=x: ok=False;break
            else:
                if x in m.values(): ok=False;break
                m[c]=x
        if ok: res.append(st)
    return res
if __name__=='__main__':
    b=open(sys.argv[1],'rb').read()
    t=sys.argv[2]
    for w in (1,2):
        r=find(b,t,w); print(w,len(r),[hex(x) for x in r[:20]])
