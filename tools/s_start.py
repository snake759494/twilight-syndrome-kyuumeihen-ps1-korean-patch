# 부팅 -> 시작 -> 첫 대사까지 진행하며 캡처 (tools/run.py 용)
import time
time.sleep(35); e.press('start',2); e.press('start',2); time.sleep(4)
e.key('x',0.3); time.sleep(1); e.key('x',0.3)
for i in range(6):
    time.sleep(5); r=e.shot('tmp/f%d.png'%i); print(i,r)
    if r is None: break
    e.key('x',0.3)
