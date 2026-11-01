import json,os,collections
meta=json.load(open('text/split/meta.json'))
out=collections.defaultdict(list)
for n,base,_,_ in meta:
    p='text/kop/%02d.json'%n
    if os.path.exists(p): out[base]+=json.load(open(p,encoding='utf-8'))
for b,l in out.items():
    json.dump(l,open('text/ko/%s.json'%b,'w',encoding='utf-8'),ensure_ascii=False,indent=0); print(b,len(l))
