import sys,os,struct,glob
sys.path.insert(0,os.path.dirname(__file__))
from cdb import entries,parts
from script import blocks,toks
from lz import dec
C=[('ALLCAP/CTLINK',0),('ALLCAP/CTLINK',1),('ALLCAP/CTLINK',5),('CAP5/W5LINK',0),('CAP5/W5LINK',1),('CAP6/K6LINK',5),('CAP6/W6LINK',0),('CAP6/W6LINK',1),('CAP7/H7LINK',1),('CAP7/YHLINK',1),('CAP8/K8LINK',8),('CAP8/K8LINK',9),('CAP8/K8LINK',12),('CAP8/K8LINK',39),('CAP9/K9LINK',8),('CAP9/K9LINK',9),('CAP9/W9LINK',1),('CAPA/KALINK',8),('CAPA/KALINK',9),('CAPA/KALINK',13),('CAPH/YHLINK',1),('CAPZ/KZLINK',10),('LIFE/LMLINK',2)]
for f,k in C:
    e=parts(open('orig/DAT/%s.CDB'%f,'rb').read())[k]; bl=blocks(e)
    T=[t for _,_,o in bl for t in toks(o)]
    nl=T.count(0x8100); g=sum(1 for t in T if t<0x1000); print(f,k,len(bl),len(T),'nl',nl,'glyph',g, ' '.join('%04x'%t for t in toks(bl[1][2])[:16]))
# 글꼴 표 찾기
for ex in sorted(glob.glob('orig/*.EXE')):
    b=open(ex,'rb').read(); base=struct.unpack_from('<I',b,0x18)[0]-0x800
    best=None;o=0x800
    while o<len(b)-8:
        n=0
        while o+8*n+8<=len(b):
            p,w=struct.unpack_from('<II',b,o+8*n)
            if 0x8001a200<=p<0x80031200 and 4<=w<=16: n+=1
            else: break
        if n>100 and (best is None or n>best[1]): best=(base+o,n)
        o+=8*n+4 if n else 4
    print(ex,best and (hex(best[0]),hex(best[1])))
k=open('orig/DAT/FONT/KFONT.CDB','rb').read(); print('KFONT',entries(k))
