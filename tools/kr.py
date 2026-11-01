# 한글 글리프 렌더: 16x16, 흰 획(0)+회색(1~3)+검은 테두리(6)+투명(4)
import numpy as np,os
from PIL import Image,ImageDraw,ImageFont
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_f={}
def font(name,sz):
    k=(name,sz)
    if k not in _f: _f[k]=ImageFont.truetype(os.path.join(ROOT,name),sz)
    return _f[k]
FONT=('NanumSquareNeo-cBd.ttf',14)
def render(ch,fname=None,size=None,dy=0):
    f=font(fname or FONT[0],size or FONT[1])
    im=Image.new('L',(64,32)); d=ImageDraw.Draw(im)
    d.text((8,8+dy),ch,font=f,fill=255)
    a=np.asarray(im,np.float32)/255
    ys,xs=np.nonzero(a>0.15)
    if len(xs)==0: return np.zeros((16,16)),6
    # 수평: 왼쪽 1px 여백(테두리용)
    x0=xs.min(); w=xs.max()-x0+1
    # 수직: 폰트 기준선 고정 (8+dy 기준)
    g=np.zeros((16,16),np.float32)
    sub=a[8+dy-1:8+dy-1+15, x0:x0+min(w,14)]
    g[0:sub.shape[0],1:1+sub.shape[1]]=sub
    return g,min(w,14)+2
def to4(g):
    """그레이 -> 게임 팔레트 인덱스(0흰 1~3회색 4투명 6검정 테두리)"""
    px=np.full((16,16),4,np.uint8)
    on=g>0.5
    px[g>0.85]=0
    px[(g>0.6)&(g<=0.85)]=1
    px[(g>0.4)&(g<=0.6)]=2
    px[(g>0.2)&(g<=0.4)]=3
    m=g>0.2
    # 테두리: 8방향 팽창
    dil=np.zeros_like(m)
    for dy in(-1,0,1):
        for dx in(-1,0,1):
            dil|=np.roll(np.roll(m,dy,0),dx,1)
    px[dil&~m]=6
    return px
def pack4(px):
    f=px.ravel(); return bytes((int(f[i])|(int(f[i+1])<<4)) for i in range(0,256,2))
