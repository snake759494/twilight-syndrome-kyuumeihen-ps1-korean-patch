# 트와일라잇 신드롬 ~구명편~ 한글패치 빌드
import sys,os,json,struct,shutil
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(HERE,'tools'))
os.chdir(HERE)
from ents import SCRIPTS
from cdb import entries,parts
from script import blocks,toks
from tok import parse
from lz import comp,dec
from enc import tokens,plain
from ptrs import exe_ptrs
from xref import consts
from font import TABS,FONT_ENTRY
import kfont
from disc import Writer
ROOT=os.path.dirname(HERE)
ORIG=os.path.join(ROOT,'Twilight Syndrome - Kyuumei-hen (Japan).bin')
OUT=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'test.bin')
CAPS=['CAP5','CAP6','CAP7','CAP8','CAP9','CAPA','CAPH']
# 글꼴 엔트리 한도: 0x8001A200 뒤에 놓인 다른 버퍼(사운드 등) 시작까지
FONT_MAX={'CAP5':0x15e00,'CAP6':0x15e00,'CAP7':0x15e00,'CAP9':0x15e00,'CAP8':0x14b00,'CAPA':0x14000,'CAPH':0x9800}
SCRIPT_MAX=0xe000          # 0x801F0000 대본 버퍼 (0x801FE000부터 다른 데이터)
def name(cap,f,k): return '%s_%s_%d'%(cap,os.path.basename(f).split('.')[0],k)
def load_ko(n):
    p=os.path.join(os.environ.get('KO_DIR','text/ko'),'%s.json'%n)
    if not os.path.exists(p): return {}
    return {x['id']:x['ko'] for x in json.load(open(p,encoding='utf-8')) if x.get('ko')}
def pack_cdb(orig,newparts):
    """CDB 재구성: 헤더(엔트리 표) + 섹터 정렬 데이터"""
    ents=entries(orig); hdr=bytearray(orig[:2048]); body=bytearray(); sec=1
    for i,(s,n) in enumerate(ents):
        d=newparts.get(i)
        if d is None: d=orig[s*2048:(s+n)*2048]
        nn=(len(d)+2047)//2048
        struct.pack_into('<HH',hdr,4*i,sec,nn)
        body+=d.ljust(nn*2048,b'\0'); sec+=nn
    return bytes(hdr)+bytes(body)
def script_ptrs(cap):
    """실행파일 대본 포인터 표 -> {(파일,엔트리): [포인터 주소...]} (표는 대본 블록 목록을 이어 붙인 것)"""
    offs={(f,k):[o for o,_,_ in blocks(parts(open('orig/'+f,'rb').read())[k])] for c,f,k in SCRIPTS if c==cap}
    ps=exe_ptrs('orig/%s.EXE'%cap); groups=[]; cur=[ps[0]]
    for a,v in ps[1:]:
        if a-cur[-1][0]<=16: cur.append((a,v))
        else: groups.append(cur); cur=[(a,v)]
    groups.append(cur); res={}
    for g in groups:
        vals=[v for a,v in g]; pos=0
        while pos<len(vals):
            hit=[key for key,o in offs.items() if key not in res and vals[pos:pos+len(o)]==o]
            if not hit: break
            res[hit[0]]=[a for a,v in g[pos:pos+len(offs[hit[0]])]]; pos+=len(offs[hit[0]])
    return res
def main():
    exe_patch={c:{} for c in CAPS}
    charsets={c:{} for c in CAPS}; kos={}
    for cap,f,k in SCRIPTS:
        ko=load_ko(name(cap,f,k)); kos[(cap,f,k)]=ko
        for s in ko.values():
            for ch in plain(s):
                if ch not in '\n　': charsets[cap][ch]=charsets[cap].get(ch,0)+1
    cmaps={}; fonts={}
    for cap in CAPS:
        chars=sorted(charsets[cap],key=lambda c:(-charsets[cap][c],c))
        data,cm=kfont.build(cap,chars,drop_kana=(cap=='CAPH'))
        print(cap,'glyphs',len(chars),'font bytes',hex(len(data)),'max',hex(FONT_MAX[cap]))
        assert len(data)<=FONT_MAX[cap],(cap,hex(len(data)))
        cmaps[cap]=cm; fonts[cap]=data
    cdbs={}
    for cap in CAPS:
        sp=script_ptrs(cap)
        for c,f,k in SCRIPTS:
            if c!=cap: continue
            orig=open('orig/'+f,'rb').read(); e=parts(orig)[k]; bl=blocks(e); ko=kos[(cap,f,k)]
            if not ko: continue
            inplace=(f,k) not in sp      # 포인터를 못 찾은 대본: 블록 위치를 원본과 같게 유지
            newe=bytearray(); newoff=[]
            for n,(o,o2,dat) in enumerate(bl):
                if inplace: newe=newe.ljust(o,b'\0')
                newoff.append(len(newe))
                if n in ko:
                    p=parse(toks(dat))
                    head=[v for kd,v in p if kd=='H']; tail=[v for kd,v in p if kd in('E','X')]
                    tk=head+tokens(ko[n],cmaps[cap])+tail
                    # 화자 이름 태그 8dNN: NN이 3 이상이면 한글 이름 첫 글자 뒤에서 줄이 끊김 -> 02로 고정
                    tk=[0x8d02 if 0x8d03<=t<=0x8d0f else t for t in tk]
                    raw=struct.pack('<%dH'%len(tk),*tk)
                    z=comp(raw); assert dec(z)[0]==raw
                    if inplace and len(z)>o2-o:
                        print('  %s 블록 %d: 자리 부족(%d>%d), 원본 유지'%(name(cap,f,k),n,len(z),o2-o)); z=e[o:o2]
                    newe+=z
                else:
                    newe+=e[o:o2]
            if inplace: newe=newe.ljust(len(e.rstrip(b'\0')),b'\0')
            assert len(newe)<=SCRIPT_MAX,(f,k,hex(len(newe)))
            cdbs.setdefault(f,{})[k]=bytes(newe)
            if not inplace:
                for a,v in zip(sp[(f,k)],newoff): exe_patch[cap][a]=struct.pack('<I',0x801f0000+v)
            print(name(cap,f,k),hex(len(e)),'->',hex(len(newe)),'inplace' if inplace else '')
    cdbs.setdefault('DAT/FONT/KFONT.CDB',{})
    for cap in CAPS: cdbs['DAT/FONT/KFONT.CDB'][FONT_ENTRY[cap]]=fonts[cap]
    rep=[]; extra={}
    if not os.environ.get('NOGFX'):
        import gfxpatch
        for f,d in gfxpatch.all_patches().items(): cdbs.setdefault(f,{}).update(d)
        extra=dict(gfxpatch.files()); rep=gfxpatch.replacements()
    # 실행파일: 글꼴 표 참조(표 주소/폭 주소)를 새 표로, 글리프 해제 호출을 2bpp 확장 루틴으로
    T=kfont.BASE+kfont.TAB_OFF
    for cap in CAPS:
        b=open('orig/%s.EXE'%cap,'rb').read(); base=struct.unpack_from('<I',b,0x18)[0]-0x800
        tb,_=TABS[cap]
        refs=[(a,v,h) for a,m,v,h in consts('orig/%s.EXE'%cap) if tb<=v<tb+8]
        assert len(refs)==4 and sum(v==tb for a,v,h in refs)==1,(cap,refs)
        for a,v,h in refs:
            nv=T+(v-tb); hi=(nv+0x8000)>>16; lo=nv&0xffff
            ins=struct.unpack_from('<I',b,h-base)[0]; exe_patch[cap][h]=struct.pack('<I',(ins&0xffff0000)|hi)
            ins=struct.unpack_from('<I',b,a-base)[0]; exe_patch[cap][a]=struct.pack('<I',(ins&0xffff0000)|lo)
            if v==tb:
                j=a+0xc; ins=struct.unpack_from('<I',b,j-base)[0]
                assert ins>>26==3,(cap,hex(j))
                exe_patch[cap][j]=struct.pack('<I',(3<<26)|((kfont.EXPAND_ADDR>>2)&0x3ffffff))
    shutil.copyfile(ORIG,OUT)
    w=Writer(OUT)
    for cap in CAPS:
        b=bytearray(open('orig/%s.EXE'%cap,'rb').read()); base=struct.unpack_from('<I',b,0x18)[0]-0x800
        for a,d in exe_patch[cap].items(): b[a-base:a-base+4]=d
        w.replace('/%s.EXE'%cap,bytes(b),allow_move=False)
    def swap(p,data):
        """같은 그림 덩어리 사본 교체(길이 동일)"""
        y=bytearray(data); n=0
        for a,c in rep:
            k=data.find(a)
            while k>=0: y[k:k+len(a)]=c; n+=1; k=data.find(a,k+1)
        if n: print(p,'그림 사본',n,'곳 교체')
        return bytes(y)
    writes={}
    for f,np_ in cdbs.items(): writes[f]=pack_cdb(open('orig/'+f,'rb').read(),np_)
    writes.update(extra)
    import glob
    for g in glob.glob('orig/DAT/**/*',recursive=True):
        p=g[5:].replace(os.sep,'/')
        if os.path.isdir(g) or '/XA' in p or '/MOVIE/' in p or 'CTLINK' in p: continue
        d=writes.get(p) or open(g,'rb').read()
        if rep:
            nd=swap(p,d)
            if nd!=d or p in writes: writes[p]=nd
    for f,nb in writes.items():
        lba=w.replace('/'+f,nb)
        print(f,'->',len(nb),'lba',lba)
    cue=os.path.splitext(OUT)[0]+'.cue'
    open(cue,'w').write('FILE "%s" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n'%os.path.basename(OUT))
    print('done',OUT)
if __name__=='__main__': main()
