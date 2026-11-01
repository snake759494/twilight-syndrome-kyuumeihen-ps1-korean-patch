"""번역 검증: python tools/chk.py <이름>  (text/ja/<이름>.json vs text/ko/<이름>.json)"""
import sys,os,json,re
sys.path.insert(0,os.path.dirname(__file__))
import kfont
LIMITS={'CAP5_W5LINK_0':272,'CAP5_W5LINK_1':272,'CAP6_W6LINK_0':224,'CAP6_W6LINK_1':256,'CAP7_H7LINK_1':256,
 'CAP7_YHLINK_1':248,'CAP8_K8LINK_8':272,'CAP8_K8LINK_9':272,'CAP9_K9LINK_8':224,'CAP9_K9LINK_9':272,
 'CAPA_KALINK_8':216,'CAPA_KALINK_9':224,'CAPH_YHLINK_1':216}
_w={}
def cw(ch):
    if ch not in _w:
        if ch=='　': _w[ch]=16
        else: _w[ch]=kfont.render(ch)[1]
    return _w[ch]
TAG=re.compile(r'\{[^}]*\}')
def width(t): return sum(cw(c) for c in t)
def check(ja,ko,limit):
    errs=[]
    if TAG.findall(ja)!=TAG.findall(ko): errs.append('태그 불일치')
    if ja.count('\n')!=ko.count('\n'): errs.append('줄바꿈 수 불일치 ja=%d ko=%d'%(ja.count('\n'),ko.count('\n')))
    for seg in re.split(r'\n|\{(?:8[569ad]|98|a8)[0-9a-f]{2}\}',ko):
        t=TAG.sub('',seg)
        if ':' in t: t=t.split(':',1)[1]
        w=width(t)
        if w>limit: errs.append('줄 너무 김(%dpx>%d): %s'%(w,limit,t))
    if re.search(r'[\u3040-\u30fa\u30fc-\u30ff\u4e00-\u9fff]',TAG.sub('',ko)): errs.append('일본어 문자 남음')
    return errs
if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    n=sys.argv[1]; lim=LIMITS[n]
    ja={x['id']:x['ja'] for x in json.load(open('text/ja/%s.json'%n,encoding='utf-8'))}
    ko={x['id']:x['ko'] for x in json.load(open('text/ko/%s.json'%n,encoding='utf-8'))}
    bad=0
    for i in ja:
        if i not in ko: print(i,'누락'); bad+=1; continue
        e=check(ja[i],ko[i],lim)
        for m in e: print(i,m)
        bad+=bool(e)
    print('문제 블록:',bad,'/',len(ja))
