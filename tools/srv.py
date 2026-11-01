# 에뮬 상주 서버: TCP 5577 로 파이썬 코드를 받아 실행 (e=Emu)
import sys,os,socket,io,contextlib,traceback;sys.path.insert(0,os.path.dirname(__file__))
from emu import Emu
cue=sys.argv[1]; st=sys.argv[2] if len(sys.argv)>2 else None
e=Emu(os.path.abspath(cue),os.path.abspath(st) if st else None)
g={'e':e,'__name__':'srv'}
open('srv.pid','w').write('%d %d'%(os.getpid(),e.p.pid))
s=socket.socket(); s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1); s.bind(('127.0.0.1',5577)); s.listen(1)
while True:
    c,_=s.accept(); data=b''
    while not data.endswith(b'\0'):
        k=c.recv(65536)
        if not k: break
        data+=k
    code=data.rstrip(b'\0').decode('utf-8'); out=io.StringIO()
    try:
        with contextlib.redirect_stdout(out): exec(code,g)
    except SystemExit:
        c.sendall(b'bye'); c.close(); e.close(); break
    except Exception: out.write(traceback.format_exc())
    c.sendall(out.getvalue().encode('utf-8')); c.close()
