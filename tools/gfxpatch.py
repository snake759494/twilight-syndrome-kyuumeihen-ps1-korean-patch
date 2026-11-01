"""그림 글자 한글화: 챕터 타이틀 카드(CTLINK), 타이틀·전리품 메뉴(PROGDAT/MENUDAT), 메모리 카드 안내(MEMDAT)"""
import sys,os,numpy as np
sys.path.insert(0,os.path.dirname(__file__))
from cdb import entries
from lz import dec,comp_fit
from tim import parse
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SERIF=os.path.join(ROOT,'SeoulHangangEB.ttf')
SERIF_M=os.path.join(ROOT,'SeoulHangangM.ttf')
G11=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'fonts','Galmuri11.ttf')
def blobs(e):
    o=0;r=[]; end=len(e.rstrip(b'\0'))
    while o<end:
        try: d,o2=dec(e,o)
        except Exception: break
        if o2<=o: break
        r.append((o,o2,d)); o=o2
    return r
def idx_of(t):
    d=np.frombuffer(t['data'],np.uint16).reshape(t['h'],t['w'])
    if t['bpp']==0: return np.stack([(d>>(4*i))&15 for i in range(4)],-1).reshape(t['h'],-1)
    return np.stack([d&255,d>>8],-1).reshape(t['h'],-1)
def set_idx(d,t,idx):
    h=t['h']
    if t['bpp']==0:
        v=idx.reshape(h,-1,4).astype(np.uint16); w=v[...,0]|v[...,1]<<4|v[...,2]<<8|v[...,3]<<12
    else:
        v=idx.reshape(h,-1,2).astype(np.uint16); w=v[...,0]|v[...,1]<<8
    p=t['ipos']+12; d[p:p+len(t['data'])]=w.astype('<u2').tobytes()
def lum(v): return ((v&31)*3+((v>>5)&31)*6+((v>>10)&31))/10
def patch_entry(e,mods):
    """mods: {blob 번호: fn(bytearray d, t)} -> 새 엔트리 (각 덩어리 길이·위치 보존)"""
    e=bytearray(e); bl=blobs(bytes(e))
    for j,fn in mods.items():
        o,o2,d=bl[j]; d=bytearray(d); t=parse(bytes(d),0); fn(d,t)
        c=comp_fit(bytes(d),o2-o); e[o:o+len(c)]=c
    return bytes(e)
# ---------------- 챕터 타이틀 카드 ----------------
CARDS={0:('다섯 번째 소문','히나시로의 숲'),1:('여섯 번째 소문','땅거미의 소년'),2:('일곱 번째 소문','텔레폰 콜'),
       3:('여덟 번째 소문','녹슨 함정'),4:('아홉 번째 소문','오컬트','미스터리 투어'),5:('열 번째 소문','뒤편의 거리')}
def bands(m,gap=6):
    rows=np.nonzero(m.any(1))[0]; out=[]; st=pv=rows[0]
    for r in rows[1:]:
        if r-pv>gap: out.append((st,pv+1)); st=r
        pv=r
    out.append((st,pv+1)); return [b for b in out if b[1]-b[0]>5]
def text_mask(lines,boxes,W,H,font=SERIF):
    """원본 글자 상자에 맞춰 오른쪽 정렬(원본 배치), 폭은 원본 폭+여유 이내"""
    im=Image.new('L',(W,H)); dr=ImageDraw.Draw(im)
    for s,(y0,y1,x0,x1) in zip(lines,boxes):
        h=y1-y0; size=int(h*1.2); maxw=min(W-8,(x1-x0)+36)
        while True:
            f=ImageFont.truetype(font,size); bb=dr.textbbox((0,0),s,font=f)
            if bb[2]-bb[0]<=maxw or size<10: break
            size-=1
        w=bb[2]-bb[0]; right=min(x1+4,W-4)
        dr.text((right-w-bb[0],(y0+y1)/2-(bb[1]+bb[3])/2),s,font=f,fill=255)
    return np.asarray(im,np.float32)/255
def blur(a,r):
    if r==0: return a
    return np.asarray(Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)),np.float32)/255
def card_entry(e,lines,seed):
    bl=blobs(e); ts=[parse(d,0) for _,_,d in bl]; n=len(bl)//2
    pal=np.array([lum(int(v)) for v in ts[0]['clut'][0]])
    def frame(i):
        a=idx_of(ts[2*i]); b=idx_of(ts[2*i+1]); return np.concatenate([a,b],1)
    frames=[frame(i) for i in range(n)]
    L=[np.array([lum(int(v)) for v in ts[2*i]['clut'][0]])[f] for i,f in enumerate(frames)]
    fin=np.max(L[-3:],0); H,W=fin.shape
    M=(fin>fin.max()*0.3).astype(np.float32)
    bs=bands(M>0)
    assert len(bs)==len(lines),(lines,bs)
    boxes=[]
    for y0,y1 in bs:
        xs=np.nonzero(M[y0:y1].any(0))[0]; boxes.append((y0,y1,xs.min(),xs.max()+1))
    K=text_mask(lines,boxes,W,H)
    Mj=blur(M,0.7); Kj=K
    Mrem=np.asarray(Image.fromarray(((fin>fin.max()*0.08)*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)))>0
    rng=np.random.default_rng(seed); outs=[]
    for i,f in enumerate(frames):
        l=L[i]; bg=np.median(l); best=None
        for r in (0,1,2,3,4,6,8,11,15,20):
            m=blur(Mj,r); den=(m*m).sum()
            if den==0: continue
            s=((l-bg)*m).sum()/den; err=((l-bg-s*m)**2).sum()
            if best is None or err<best[0]: best=(err,r,s)
        _,r,s=best
        if s<=1.0: outs.append((f,None)); continue       # 글자 없음 (흰/검은 화면)
        outs.append((f,r))
    def mode(v):
        u,c=np.unique(v,return_counts=True); return u[np.argmax(c)]
    def paint(f,r,nl,rows,flat=False):
        """nl: 밝기 단계 수, rows: 행별 최빈 색 사용 여부(False면 단계별 단색)"""
        vj=blur(Mj,r); vk=blur(Kj,r); mx=max(vj.max(),vk.max())
        qj=np.clip(np.round(vj/mx*nl),0,nl).astype(int); qk=np.clip(np.round(vk/mx*nl),0,nl).astype(int)
        out=f.copy(); H_=f.shape[0]
        glob_mode={q:mode(f[qj==q]) for q in range(nl+1) if (qj==q).any()}
        gk=np.array(sorted(glob_mode))
        rowmode={}
        if rows:
            for y in range(H_):
                for q in np.unique(qj[y]): rowmode[(y,q)]=mode(f[y][qj[y]==q])
        area=(qk>0)|(qj>0)|(Mrem if r<=2 else False)
        if flat: out[qk==0]=glob_mode[gk[0]]   # 배경 잡음 제거
        for y in range(H_):
            for x in np.nonzero(area[y])[0]:
                q=qk[y,x]; v=None
                if rows:
                    for dy in (0,-1,1,-2,2,-3,3):
                        v=rowmode.get((y+dy,q))
                        if v is not None: break
                if v is None: v=glob_mode[gk[np.argmin(abs(gk-q))]]
                out[y,x]=v
        return out
    eb=bytearray(e); res=[]
    for i,(f,r) in enumerate(outs):
        if r is None: res.append(f); continue
        for nl,rows,flat in ((12,True,False),(12,True,True),(12,False,True),(6,False,True),(3,False,True)):
            fr=paint(f,r,nl,rows,flat); cs=[]
            for h_ in (0,1):
                o,o2,d=bl[2*i+h_]; d=bytearray(d)
                set_idx(d,ts[2*i+h_],fr[:,h_*160:(h_+1)*160].astype(np.uint8))
                try: cs.append(comp_fit(bytes(d),o2-o))
                except ValueError: break
            if len(cs)==2: break
        else: raise ValueError('카드 %s 프레임 %d 크기 초과'%(lines[-1],i))
        if (nl,rows,flat)!=(12,True,False): print('카드',lines[-1],'프레임',i,'단순화',nl,rows,flat)
        for h_ in (0,1):
            o,o2,_=bl[2*i+h_]; eb[o:o2]=cs[h_]
        res.append(fr)
    return bytes(eb),res,ts
def ctlink():
    b=open('orig/DAT/ALLCAP/CTLINK.CDB','rb').read(); es=entries(b); out={}
    for k,lines in CARDS.items():
        s,c=es[k]; out[k]=card_entry(b[s*2048:(s+c)*2048],lines,k)[0]
    return out
# ---------------- 메뉴·메모리 카드 그림 ----------------
def draw_lines(W,H,lines,font,size,center=True,dy=0):
    im=Image.new('L',(W,H)); dr=ImageDraw.Draw(im)
    while size>8:
        f=ImageFont.truetype(font,size)
        if max(dr.textbbox((0,0),s,font=f)[2]-dr.textbbox((0,0),s,font=f)[0] for s in lines)<=W-2: break
        size-=1
    f=ImageFont.truetype(font,size)
    lh=H//len(lines)
    for i,s in enumerate(lines):
        bb=dr.textbbox((0,0),s,font=f); w=bb[2]-bb[0]
        x=(W-w)//2-bb[0] if center else 1-bb[0]
        if w>W: print('경고: 폭 초과',s,w,W)
        y=i*lh+(lh-(bb[3]-bb[1]))//2-bb[1]+dy
        dr.text((x,y),s,font=f,fill=255)
    return im
def relabel(lines,font=None,size=12,center=True,dy=0):
    font=font or G11
    def fn(d,t):
        idx=idx_of(t); H,W=idx.shape
        pal=[int(x) for x in t['clut'][0]]
        used,cnt=np.unique(idx,return_counts=True)
        bg=int(used[np.argmax(cnt)]); others=[int(u) for u in used if u!=bg]
        if not others: return
        lb=lum(pal[bg]); others.sort(key=lambda u:abs(lum(pal[u])-lb))
        a=np.asarray(draw_lines(W,H,lines,font,size,center,dy=dy)).astype(float)/255
        out=np.full((H,W),bg,np.uint8)
        levels=[(abs(lum(pal[u])-lb),u) for u in others]; mx=levels[-1][0] or 1
        for yy,xx in zip(*np.nonzero(a>0.15)):
            tgt=a[yy,xx]*mx; out[yy,xx]=min(levels,key=lambda l:abs(l[0]-tgt))[1]
        set_idx(d,t,out)
    return fn
MENU={0:['전리품 보기'],1:['창 색상'],2:['타이틀로'],
 3:['첫 번째 소문  심령사진 양산 공원'],4:['두 번째 소문  음악실의 M.F'],5:['세 번째 소문  막차'],
 6:['네 번째 소문  히나시로고교 7대 불가사의'],
 10:['I 공원  고베 다리'],11:['I 공원  화장실 앞'],12:['I 공원  한밤중의 큰 도리이'],13:['I 공원  주차장'],
 14:['M역 구내  여자 화장실'],15:['M역 구내  남자 화장실'],16:['M역 구내  육교'],17:['M역 구내  소바 가게'],
 18:['M역 구내  3번 홈'],19:['M역 구내  자판기'],20:['M역 구내  4번 홈'],21:['M역 구내  유야미가오카행'],
 22:['히나시로 고교  체육관 기구실'],23:['정수장에서 본 거리'],25:['조각관의 소리'],26:['고베 다리의 소리'],
 27:['한밤의 교내 방송'],28:['한밤의 피아노'],29:['도서실의 소리'],30:['방공호의 소리'],31:['I 공원  한낮의 큰 도리이']}
def menu_mods(off):
    m={j+off:relabel(v) for j,v in MENU.items()}
    m[7+off]=relabel(['시작'],SERIF_M,20); m[8+off]=relabel(['준비'],SERIF_M,20)
    m[9+off]=relabel(['『사진』'],SERIF_M,16); m[24+off]=relabel(['『녹음』'],SERIF_M,16)
    return m
MEM={0:['세이브에 실패했습니다.'],1:['로드에 실패했습니다.'],2:['초기화에 실패했습니다.'],
 3:['메모리 카드에','1블록의','빈 공간이 없습니다'],4:['메모리 카드를','인식할 수 없습니다'],5:['메모리 카드를','교체해 주세요'],
 6:['이 메모리 카드는','사용할 수 없습니다'],7:['메모리 카드에','액세스 중입니다'],
 8:['메모리 카드가','초기화되지 않았습니다','초기화하시겠습니까?'],9:['예'],10:['아니요'],
 11:['이 메모리 카드에는','「트와일라잇 신드롬」','탐색편의 세이브 데이터가','없습니다'],
 12:['이대로 계속하면','메모리 카드에','액세스할 수 없습니다'],13:['메모리 카드를','교체하시겠습니까?'],
 14:['메모리 카드를','넣으시겠습니까?'],15:['메모리 카드를','넣어 주세요'],16:['탐험 준비 중'],17:['탐험 기록 중']}
def pairs(orig,new):
    """같은 위치·길이 덩어리의 (원본 압축, 새 압축) 쌍"""
    return [(orig[o:o2],new[o:o2]) for o,o2,_ in blobs(orig) if orig[o:o2]!=new[o:o2]]
NANUM=os.path.join(ROOT,'NanumSquareNeo-dEb.ttf')
# 장소 이름·엔딩 문구 라벨: {(CDB, 엔트리): {덩어리: (문구, 글꼴, 크기)}}
LABELS={
 ('DAT/CAP5/K5LINK.CDB',8):{0:('도서실',NANUM,20)},
 ('DAT/CAP6/K6LINK.CDB',14):{0:('체육관',NANUM,20),1:('체육 기구실',NANUM,20)},
 ('DAT/CAP8/K8LINK.CDB',39):{10:('방공호 입구',NANUM,20),11:('우물 가는 통로',NANUM,20),12:('발전기 통로',NANUM,20),
   13:('병사 숙소',NANUM,20),14:('중앙 통로',NANUM,20),15:('금강 구역',NANUM,20),16:('수로 가는 통로',NANUM,20),17:('귀빈실 입구',NANUM,20)},
 ('DAT/CAPA/KALINK.CDB',10):{2:('판자 담장 길',NANUM,20),3:('뒷골목',NANUM,20),4:('풍경 길',NANUM,20),5:('민가 거리',NANUM,20),
   6:('구교사 1F',NANUM,20),7:('구교사 3F',NANUM,20),8:('구교사 옥상',NANUM,20),
   9:('망각...',SERIF_M,22),10:('상실...',SERIF_M,22),11:('암전...',SERIF_M,22)},
 ('DAT/CAPA/KALINK.CDB',39):{27:('「소문」 끝',SERIF_M,20)},
 ('DAT/CAPZ/KZLINK.CDB',10):{0:('신교사 1F',NANUM,20),1:('신교사 2F',NANUM,20),2:('신교사 3F',NANUM,20),3:('신교사 4F',NANUM,20),
   4:('미술실',NANUM,20),5:('서도실',NANUM,20),6:('연결 통로',NANUM,20),7:('구교사 1F',NANUM,20),8:('구교사 2F',NANUM,20),9:('구교사 3F',NANUM,20)},
}
def label_patches():
    out={}
    for (p,k),mods in LABELS.items():
        b=open('orig/'+p,'rb').read(); s,c=entries(b)[k]
        out.setdefault(p,{})[k]=patch_entry(b[s*2048:(s+c)*2048],{j:relabel([t],f,z) for j,(t,f,z) in mods.items()})
    return out
_cache={}
def all_patches():
    """CDB 엔트리 교체분 {경로: {엔트리: bytes}}"""
    if 'p' not in _cache:
        out={'DAT/ALLCAP/CTLINK.CDB':ctlink()}
        for p,d in label_patches().items(): out.setdefault(p,{}).update(d)
        _cache['p']=out
    return _cache['p']
def files():
    """파일 통째 교체분 {경로: bytes}"""
    if 'f' not in _cache: _cache['f']=_files()
    return _cache['f']
def replacements():
    """다른 파일에 들어 있는 같은 그림 덩어리 사본을 바꾸기 위한 (원본, 새) 압축 바이트 쌍"""
    rep=[]
    for p,d in files().items(): rep+=pairs(open('orig/'+p,'rb').read(),d)
    for p,ents in all_patches().items():
        if 'CTLINK' in p: continue
        b=open('orig/'+p,'rb').read(); es=entries(b)
        for k,d in ents.items():
            s,c=es[k]; rep+=pairs(b[s*2048:(s+c)*2048],d)
    return rep
def _files():
    out={}
    b=open('orig/DAT/SINKOU/MENUDAT.BIN','rb').read(); out['DAT/SINKOU/MENUDAT.BIN']=patch_entry(b,menu_mods(0))
    b=open('orig/DAT/SINKOU/PROGDAT.BIN','rb').read(); out['DAT/SINKOU/PROGDAT.BIN']=patch_entry(b,menu_mods(10))
    b=open('orig/DAT/SINKOU/MEMDAT.BIN','rb').read(); out['DAT/SINKOU/MEMDAT.BIN']=patch_entry(b,{j:relabel(v) for j,v in MEM.items()})
    return out
if __name__=='__main__':
    # 미리보기: tmp/card_<k>.png (프레임 몇 장), tmp/menu_*.png
    from tim import image
    b=open('orig/DAT/ALLCAP/CTLINK.CDB','rb').read(); es=entries(b)
    for k,lines in CARDS.items():
        s,c=es[k]; e,outs,ts=card_entry(b[s*2048:(s+c)*2048],lines,k)
        pal=np.array([[ (int(v)&31)<<3,((int(v)>>5)&31)<<3,((int(v)>>10)&31)<<3] for v in ts[-1]['clut'][0]],np.uint8)
        sel=[len(outs)//4,len(outs)//2,len(outs)-1]
        im=np.concatenate([pal[outs[i]] for i in sel],0)
        Image.fromarray(im).save('tmp/card_%d.png'%k)
    for name,data in files().items():
        ims=[image(parse(d,0)) for _,_,d in blobs(data) if parse(d,0)]
        ims=[x for x in ims if x and x.size[1]<=64]
        W=max(x.size[0] for x in ims); Hs=sum(x.size[1]+2 for x in ims)
        sh=Image.new('RGB',(W,Hs),(0,90,0)); y=0
        for x in ims: sh.paste(x,(0,y)); y+=x.size[1]+2
        sh.resize((W*2,Hs*2),0).save('tmp/menu_%s.png'%os.path.basename(name)[:-4])
