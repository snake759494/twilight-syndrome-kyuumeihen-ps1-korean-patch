import sys,os,struct
sys.path.insert(0,os.path.dirname(__file__))
from mdis import load,md
import capstone
def consts(exe):
    """lui/addiu|ori 쌍으로 만든 32비트 상수 (주소, 레지스터, 값) 목록"""
    c,b=load(exe); md.skipdata=True; md.detail=False
    L=list(md.disasm(c,b)); hi={}; res=[]
    for k,i in enumerate(L):
        m=i.mnemonic; ops=i.op_str.split(', ')
        if m=='lui': hi[ops[0]]=(int(ops[1],16)<<16, i.address)
        elif m in('addiu','ori','lw','sw','lh','lhu','sh','lb','lbu','sb') :
            if m in('addiu','ori'):
                src=ops[1]; imm=int(ops[2],16) if not ops[2].startswith('-') else -int(ops[2][1:],16)
            else:
                if '(' not in ops[1]: continue
                off,src=ops[1].split('('); src=src[:-1]
                try: imm=int(off,16) if not off.startswith('-') else -int(off[1:],16)
                except ValueError: continue
            if src in hi and i.address-hi[src][1]<0x40:
                v=(hi[src][0]+ (imm if m!='ori' else imm))&0xffffffff
                res.append((i.address,m,v,hi[src][1]))
        if m in ('jal','jr','j','b'): pass
    return res
if __name__=='__main__':
    exe=sys.argv[1]; lo,hi_=int(sys.argv[2],16),int(sys.argv[3],16)
    for a,m,v,h in consts(exe):
        if lo<=v<hi_: print(hex(a),m,hex(v),'lui@',hex(h))
