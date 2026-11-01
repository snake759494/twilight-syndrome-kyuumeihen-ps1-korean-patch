# 상주 서버에 코드 전송: python tools/cl.py "코드" | python tools/cl.py -f file.py
import socket,sys
code=open(sys.argv[2],encoding='utf8').read() if sys.argv[1]=='-f' else sys.argv[1]
s=socket.create_connection(('127.0.0.1',5577)); s.sendall(code.encode('utf8')+b'\0')
out=b''
while True:
    k=s.recv(65536)
    if not k: break
    out+=k
sys.stdout.reconfigure(encoding='utf-8'); print(out.decode('utf8'))
