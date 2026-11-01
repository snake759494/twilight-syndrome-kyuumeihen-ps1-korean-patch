# CD-ROM Mode2 Form1 EDC/ECC
EDC=[0]*256
for i in range(256):
    e=i
    for _ in range(8): e=(e>>1)^(0xD8018001 if e&1 else 0)
    EDC[i]=e
FF=[0]*256; FB=[0]*256
for i in range(256):
    j=(i<<1)^(0x11D if i&0x80 else 0); FF[i]=j&0xff; FB[i^j&0xff]=i
def edc(d):
    e=0
    for b in d: e=(e>>8)^EDC[(e^b)&0xff]
    return e
def _ecc(sec,major_count,minor_count,major_mult,minor_inc,dest):
    size=major_count*minor_count
    for major in range(major_count):
        index=(major>>1)*major_mult+(major&1)
        a=b=0
        for minor in range(minor_count):
            t=sec[0xC+index]
            index+=minor_inc
            if index>=size: index-=size
            a^=t; b^=t; a=FF[a]
        a=FB[FF[a]^b]
        sec[dest+major]=a; sec[dest+major+major_count]=a^b
def form1(sec):
    """sec: bytearray(2352) with header/subheader/data filled. Computes EDC/ECC in place."""
    e=edc(sec[0x10:0x818]); sec[0x818:0x81C]=e.to_bytes(4,'little')
    hdr=bytes(sec[0xC:0x10]); sec[0xC:0x10]=b'\0\0\0\0'
    _ecc(sec,86,24,2,86,0x81C)
    _ecc(sec,52,43,86,88,0x8C8)
    sec[0xC:0x10]=hdr
    return sec
