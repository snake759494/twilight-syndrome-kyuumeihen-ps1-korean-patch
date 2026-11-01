# 챕터별 한글 폰트 엔트리 생성 (0x8001A200 적재)
# 구조: +0 확장 루틴(2bpp->4bpp), +0x100 글리프 테이블 N*8 {ptr,width}, 이후 2bpp 글리프 64바이트씩
import numpy as np,os,sys,struct
sys.path.insert(0,os.path.dirname(__file__))
from PIL import Image,ImageDraw,ImageFont
import keystone
from font import glyphs
BASE=0x8001a200
CODE_OFF=0x98
TAB_OFF=0x120
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONT_FILE=os.path.join(ROOT,'NanumSquareNeo-cBd.ttf'); FONT_SIZE=14
SPACE_W=5
SUB={"・":"·","～":"~"}   # 폰트에 없는 글자 대체
KS=keystone.Ks(keystone.KS_ARCH_MIPS,keystone.KS_MODE_MIPS32+keystone.KS_MODE_LITTLE_ENDIAN)
EXPAND='''
.set noreorder
 ori $t3,$zero,0x6204
 addiu $t9,$a0,64
lp:
 lbu $t0,0($a0)
 addiu $a0,$a0,1
 andi $t1,$t0,3
 sll $t1,$t1,2
 srlv $t2,$t3,$t1
 andi $t2,$t2,0xf
 srl $t1,$t0,2
 andi $t1,$t1,3
 sll $t1,$t1,2
 srlv $t4,$t3,$t1
 andi $t4,$t4,0xf
 sll $t4,$t4,4
 or $t2,$t2,$t4
 sb $t2,0($a1)
 srl $t1,$t0,4
 andi $t1,$t1,3
 sll $t1,$t1,2
 srlv $t2,$t3,$t1
 andi $t2,$t2,0xf
 srl $t1,$t0,6
 sll $t1,$t1,2
 srlv $t4,$t3,$t1
 andi $t4,$t4,0xf
 sll $t4,$t4,4
 or $t2,$t2,$t4
 sb $t2,1($a1)
 bne $a0,$t9,lp
 addiu $a1,$a1,2
 jr $ra
 nop
'''
def expand_code():
    enc,_=KS.asm(EXPAND,BASE+CODE_OFF); return bytes(enc)
EXPAND_ADDR=BASE+CODE_OFF
_f=None
def kfont():
    global _f
    if _f is None: _f=ImageFont.truetype(FONT_FILE,FONT_SIZE)
    return _f
def render(ch):
    """-> (16x16 2bpp 값 배열 0투명 1흰 2회색 3검정, 폭)"""
    if ch==' ': return np.zeros((16,16),np.uint8),SPACE_W
    ch=SUB.get(ch,ch)
    f=kfont(); im=Image.new('L',(48,32)); d=ImageDraw.Draw(im)
    d.text((8,6),ch,font=f,fill=255)
    a=np.asarray(im,np.float32)/255
    # 세로 위치: 한글 '가' 기준 고정 (행 1~14)
    ys,xs=np.nonzero(a>0.2)
    if len(xs)==0: return np.zeros((16,16),np.uint8),SPACE_W
    x0=xs.min(); x1=xs.max()+1; w=min(x1-x0,14)
    sub=a[6+TOPCUT:6+TOPCUT+15,x0:x0+w]
    g=np.zeros((16,16),np.float32); g[0:sub.shape[0],1:1+w]=sub
    v=np.zeros((16,16),np.uint8)
    m=g>0.3
    dil=np.zeros_like(m)
    for dy in(-1,0,1):
        for dx in(-1,0,1):
            dil|=np.roll(np.roll(m,dy,0),dx,1)
    v[dil]=3
    v[g>0.3]=2
    v[g>0.55]=1
    return v,w+2
TOPCUT=1
def calib():
    """'가','한' 잉크 상단이 1행이 되도록 TOPCUT 결정"""
    global TOPCUT
    f=kfont(); im=Image.new('L',(48,32)); d=ImageDraw.Draw(im); d.text((8,6),'한글가힣',font=f,fill=255)
    a=np.asarray(im)>50; ys=np.nonzero(a)[0]
    top,bot=ys.min(),ys.max()
    TOPCUT=top-6-1
    return top,bot
def pack(v):
    f=v.ravel(); return bytes(int(f[i])|int(f[i+1])<<2|int(f[i+2])<<4|int(f[i+3])<<6 for i in range(0,256,4))
M4={4:0,0:1,1:2,2:2,3:2,5:3,6:3}
def build(cap,chars,ncommon=0xdc,drop_kana=False):
    """chars: 코드 0xdc부터 배정할 문자 리스트. 반환 (entry bytes, code map)"""
    calib()
    old=glyphs(cap)[:ncommon]
    code=expand_code(); assert CODE_OFF+len(code)<=TAB_OFF
    N=ncommon+len(chars)
    gl_off=TAB_OFF+N*8
    from font import kfont_entry
    clut=kfont_entry(2)[:0x91]; assert len(clut)<=CODE_OFF
    data=bytearray((clut.ljust(CODE_OFF,b'\0')+code).ljust(TAB_OFF,b'\0'))+bytearray(N*8)
    cache={}
    def add(blob):
        if blob in cache: return cache[blob]
        p=BASE+len(data); data.extend(blob); cache[blob]=p; return p
    for c in range(ncommon):
        w,px=old[c]
        v=np.array([M4[x] for x in px],np.uint8).reshape(16,16)
        if drop_kana and (1<=c<0x83 or 0x93<=c<0xbc): v[:]=0   # 한글 대본에 안 쓰는 가나·한자 숫자 (공간 절약)
        p=add(pack(v)); struct.pack_into('<II',data,TAB_OFF+8*c,p,w)
    cmap={}
    for i,ch in enumerate(chars):
        v,w=render(ch); p=add(pack(v)); c=ncommon+i
        struct.pack_into('<II',data,TAB_OFF+8*c,p,w); cmap[ch]=c
    return bytes(data),cmap
def preview(cap,chars,out):
    calib()
    im=Image.new('RGB',(16*32,16*((len(chars)+31)//32)),(40,40,120))
    pal={0:None,1:(255,255,255),2:(160,160,160),3:(0,0,0)}
    for i,ch in enumerate(chars):
        v,w=render(ch)
        for y in range(16):
            for x in range(16):
                if v[y,x]: im.putpixel(((i%32)*16+x,(i//32)*16+y),pal[v[y,x]])
    im.resize((im.width*3,im.height*3),0).save(out)
