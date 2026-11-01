import struct
def entries(b):
    res=[]
    for i in range(0,0x800,4):
        s,n=struct.unpack_from('<HH',b,i)
        if i>0 and s==0 and n==0: break
        res.append((s,n))
    return res
def parts(b):
    return [b[s*2048:(s+n)*2048] for s,n in entries(b)]
