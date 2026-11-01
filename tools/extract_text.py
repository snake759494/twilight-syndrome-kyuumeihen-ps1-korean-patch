# 스크립트 -> text/ja/<cap>_<file>_<k>.json : [{"id":n,"ja":tagged}]
import sys,os,json
sys.path.insert(0,os.path.dirname(__file__))
from ents import SCRIPTS
from cdb import parts
from script import blocks,toks
from tok import parse,COMMON
from ocr import ocr
def tagged(p,cm):
    s=''; i=0
    while i<len(p):
        k,v=p[i]
        if k=='G':
            c=v&0xfff
            if v&0xf000: s+='{g%04x}'%v
            else: s+= COMMON[c] if c<len(COMMON) else cm.get(c,'{g%04x}'%v)
        elif k=='C':
            if v==0x8100: s+='\n'
            else:
                t='{%04x'%v
                while i+1<len(p) and p[i+1][0]=='A': i+=1; t+=':%04x'%p[i][1]
                s+=t+'}'
        i+=1
    return s
def name(cap,f,k): return '%s_%s_%d'%(cap,os.path.basename(f).split('.')[0],k)
if __name__=='__main__':
    os.makedirs('text/ja',exist_ok=True)
    cms={}
    for cap,f,k in SCRIPTS:
        if cap not in cms: cms[cap]={c:v[0] for c,v in ocr(cap).items()}
        e=parts(open('orig/'+f,'rb').read())[k]
        out=[]
        for n,(o,o2,dat) in enumerate(blocks(e)):
            p=parse(toks(dat))
            body=[x for x in p if x[0] not in('H','E','X')]
            out.append({'id':n,'ja':tagged(body,cms[cap])})
        json.dump(out,open('text/ja/%s.json'%name(cap,f,k),'w',encoding='utf-8'),ensure_ascii=False,indent=0)
        print(name(cap,f,k),len(out),sum(len(x['ja']) for x in out))
