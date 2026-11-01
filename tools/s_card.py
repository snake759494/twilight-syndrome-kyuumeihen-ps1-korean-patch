# 시작 -> B:탐색 개시 -> 챕터 카드 캡처
import time
time.sleep(35); e.press('start',2); e.press('start',2); time.sleep(4)
e.key('x',0.3); time.sleep(1); e.key('x',0.3); time.sleep(22)
e.key('down',0.3); time.sleep(1); e.key('x',0.3)
for i in range(10):
    time.sleep(2.5); print(i,e.shot('tmp/c%d.png'%i))
