import struct
def dec(b,o,rl=3,bl=3,lit=1,big=True,limit=128):
    assert b[o]==0xff; o+=1; out=bytearray()
    while len(out)<limit:
        c=b[o]; o+=1
        if c<0x80:
            n=c+lit; out+=b[o:o+n]; o+=n
        elif c<0xc0:
            n=(c&0x3f)+rl; out+=bytes([b[o]])*n; o+=1
        else:
            d=(b[o]<<8|b[o+1]) if big else (b[o]|b[o+1]<<8); o+=2; n=(c&0x3f)+bl
            for k in range(n): out.append(out[-d] if d<=len(out) and d>0 else 0)
    return bytes(out),o
