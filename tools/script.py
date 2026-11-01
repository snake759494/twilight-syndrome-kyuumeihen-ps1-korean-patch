import struct,sys,os
sys.path.insert(0,os.path.dirname(__file__))
from lz import dec
from cdb import entries
def blocks(e):
    """엔트리를 LZ 블록 열로 분해. 실패 시 None"""
    o=0; res=[]
    end=len(e)
    while end>0 and e[end-1]==0: end-=1
    try:
        while o<end:
            out,o2=dec(e,o)
            if len(out)%2 or len(out)<4: return None
            res.append((o,o2,out)); o=o2
    except Exception: return None
    return res
def toks(out): return list(struct.unpack('<%dH'%(len(out)//2),out))
if __name__=='__main__':
    import glob
    for f in sorted(glob.glob('orig/DAT/**/*.CDB',recursive=True)):
        if 'KFONT' in f: continue
        b=open(f,'rb').read()
        for k,(s,n) in enumerate(entries(b)):
            e=b[s*2048:(s+n)*2048]
            if not e: continue
            bl=blocks(e)
            if bl and len(bl)>=2:
                ends=sum(1 for _,_,o in bl if 0xffff in toks(o))
                print(f,k,n,len(bl),ends)
