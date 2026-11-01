import sys,os,json
sys.path.insert(0,os.path.dirname(__file__))
from cdb import parts
from script import blocks,toks
from tok import parse,render
from ocr import ocr
cap,f,k=sys.argv[1],sys.argv[2],int(sys.argv[3])
cm={c:v[0] for c,v in ocr(cap).items()}
e=parts(open(f,'rb').read())[k]
for n,(o,o2,out) in enumerate(blocks(e)):
    print('--- %d @%x'%(n,o)); print(render(parse(toks(out)),cm))
