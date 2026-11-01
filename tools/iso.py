import struct,sys
SEC=2352
class Disc:
    def __init__(s,p,mode='rb'):
        s.f=open(p,mode)
    def sector(s,lba):
        s.f.seek(lba*SEC); return s.f.read(SEC)
    def data(s,lba): return s.sector(lba)[24:24+2048]
    def read(s,lba,size):
        out=bytearray()
        n=(size+2047)//2048
        for i in range(n): out+=s.data(lba+i)
        return bytes(out[:size])
    def walk(s,lba=None,size=None,path=''):
        if lba is None:
            pvd=s.data(16); root=pvd[156:156+34]
            lba=struct.unpack_from('<I',root,2)[0]; size=struct.unpack_from('<I',root,10)[0]
        d=s.read(lba,size); i=0; res=[]
        while i<len(d):
            l=d[i]
            if l==0: i=(i//2048+1)*2048; continue
            e=d[i:i+l]; elba=struct.unpack_from('<I',e,2)[0]; esz=struct.unpack_from('<I',e,10)[0]
            fl=e[25]; nl=e[32]; name=e[33:33+nl]
            if name not in (b'\0',b'\1'):
                nm=name.decode('latin1').split(';')[0]
                if fl&2: res+=s.walk(elba,esz,path+'/'+nm)
                else: res.append((path+'/'+nm,elba,esz,lba,i))
            i+=l
        return res
if __name__=='__main__':
    d=Disc(sys.argv[1])
    for p,l,sz,_,_ in d.walk(): print(f'{l:8d} {sz:10d} {p}')
