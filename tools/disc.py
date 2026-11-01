import struct,os,sys
sys.path.insert(0,os.path.dirname(__file__))
from cdsec import form1
from iso import Disc,SEC
class Writer(Disc):
    def __init__(s,p):
        s.f=open(p,'r+b'); s.files={x[0]:x for x in s.walk()}
        s.end=os.path.getsize(p)//SEC
    def wsec(s,lba,data2048,eof=False,last=False,keep_sub=False):
        sec=bytearray(s.sector(lba)) if lba<s.end else bytearray(SEC)
        if lba>=s.end:
            sec[0:12]=b'\x00'+b'\xff'*10+b'\x00'
            l=lba+150; bcd=lambda x:((x//10)<<4)|(x%10)
            sec[12:15]=bytes([bcd(l//4500),bcd((l//75)%60),bcd(l%75)]); sec[15]=2
        if not keep_sub:
            sm=0x08
            if last: sm|=0x81|0x08
            sec[16:24]=bytes([0,0,sm,0,0,0,sm,0])
        sec[24:24+2048]=data2048.ljust(2048,b'\0')
        form1(sec); s.f.seek(lba*SEC); s.f.write(sec)
        if lba>=s.end: s.end=lba+1
    def _update_dir(s,path,lba,size):
        _,_,_,dlba,doff=s.files[path]
        blk=bytearray(s.data(dlba+doff//2048)); o=doff%2048
        blk[o+2:o+10]=struct.pack('<I',lba)+struct.pack('>I',lba)
        blk[o+10:o+18]=struct.pack('<I',size)+struct.pack('>I',size)
        s.wsec(dlba+doff//2048,bytes(blk),keep_sub=True)
    def replace(s,path,data,allow_move=True):
        p,lba,size,dlba,doff=s.files[path]
        cap=s.capacity(path)
        if len(data)>cap:
            if not allow_move: raise ValueError(f'{path}: {len(data)} > {cap}')
            lba=s.end
        n=(len(data)+2047)//2048
        for i in range(n):
            s.wsec(lba+i,data[i*2048:(i+1)*2048],last=(i==n-1))
        s._update_dir(path,lba,len(data))
        s.files[path]=(p,lba,len(data),dlba,doff)
        return lba
    def capacity(s,path):
        p,lba,size,_,_=s.files[path]
        starts=sorted(set(x[1] for x in s.files.values()))
        nxt=min([x for x in starts if x>lba]+[s.end])
        return (nxt-lba)*2048
    def write_at(s,path,lba,data):
        p,_,_,dlba,doff=s.files[path]
        n=(len(data)+2047)//2048
        for i in range(n):
            s.wsec(lba+i,data[i*2048:(i+1)*2048],last=(i==n-1))
        s._update_dir(path,lba,len(data))
        s.files[path]=(p,lba,len(data),dlba,doff)
