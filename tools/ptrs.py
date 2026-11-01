import struct,sys,os,glob
sys.path.insert(0,os.path.dirname(__file__))
from cdb import entries
from script import blocks,toks
def exe_ptrs(p):
    b=open(p,'rb').read(); base=struct.unpack_from('<I',b,0x18)[0]-0x800
    res=[]
    for o in range(0x800,len(b)-3,4):
        v=struct.unpack_from('<I',b,o)[0]
        if 0x801f0000<=v<0x801fe800: res.append((base+o,v-0x801f0000))
    return res
def script_entries():
    out={}
    for f in sorted(glob.glob('orig/DAT/**/*.CDB',recursive=True)):
        if 'KFONT' in f or 'HITO' in f: continue
        b=open(f,'rb').read()
        for k,(s,n) in enumerate(entries(b)):
            e=b[s*2048:(s+n)*2048]
            bl=blocks(e) if e else None
            if not bl or len(bl)<2 or not all(0xffff in toks(o) for _,_,o in bl): continue
            out[(f.replace(os.sep,'/'),k)]=[o for o,_,_ in bl]
    return out
if __name__=='__main__':
    se=script_entries()
    for ex in sorted(glob.glob('orig/*.EXE')):
        ps=exe_ptrs(ex)
        if not ps: continue
        # 연속 구조체 묶기 (주소 간격 <=12)
        groups=[];cur=[ps[0]]
        for a,v in ps[1:]:
            if a-cur[-1][0]<=16: cur.append((a,v))
            else: groups.append(cur);cur=[(a,v)]
        groups.append(cur)
        for g in groups:
            offs=[v for a,v in g]
            m=[k for k,bo in se.items() if set(offs)<=set(bo)]
            print(ex,hex(g[0][0]),len(g),'match',[(k[0].split('/')[-1],k[1]) for k in m][:6])

def assign(cap,se=None):
    se=se or script_entries()
    cand={k:set(v) for k,v in se.items() if '/%s/'%cap in k[0]}
    res=[];bad=[]
    for a,v in exe_ptrs('orig/%s.EXE'%cap):
        if v>=0xe000: continue
        m=[k for k,s in cand.items() if v in s]
        if len(m)==1: res.append((a,m[0],v))
        else: bad.append((a,v,m))
    return res,bad
