import struct
def exe(p):
    b=open(p,'rb').read(); t0=struct.unpack_from('<I',b,0x18)[0]; return b,t0-0x800
def tables(p):
    b,base=exe(p)
    rd=lambda a: struct.unpack_from('<I',b,a-base)[0]
    a=base+0x800;runs=[];st=None
    while a<base+len(b)-8:
        pp,w=rd(a),rd(a+4)
        ok=(0x80010000<=pp<0x80035000 and w<=16)
        if ok and st is None: st=a
        if not ok and st is not None:
            if (a-st)//8>20: runs.append((st,(a-st)//8))
            st=None
        a+=8 if st is not None else 4
    return [(s,n,[(rd(s+8*i),rd(s+8*i+4)) for i in range(n)]) for s,n in runs]
if __name__=='__main__':
    import glob
    for f in sorted(glob.glob('orig/CAP*.EXE'))+['orig/PROG.EXE']:
        for s,n,t in tables(f): print(f,hex(s),hex(n),hex(t[0][0]),hex(max(x[0] for x in t)),hash(tuple(t))%10000)
