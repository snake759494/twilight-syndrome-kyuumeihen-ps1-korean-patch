import sys,os
def isj(b,i):
    c=b[i]
    if (0x81<=c<=0x9f or 0xe0<=c<=0xea) and i+1<len(b):
        d=b[i+1]
        if 0x40<=d<=0xfc and d!=0x7f: return 2
    return 0
def scan(b,minlen=3):
    i=0;res=[]
    while i<len(b):
        j=i;n=0
        while j<len(b):
            k=isj(b,j)
            if k: j+=2;n+=1
            else: break
        if n>=minlen:
            try: res.append((i,b[i:j].decode('cp932')))
            except: pass
            i=j
        else: i+=1
    return res
if __name__=='__main__':
    for root,_,fs in os.walk(sys.argv[1]):
        for f in fs:
            p=os.path.join(root,f); b=open(p,'rb').read()
            r=scan(b,4)
            if r: print(len(r),sum(len(x[1]) for x in r),p)
