import time
e.key('f2'); time.sleep(3)
e.key('o',hold=0.2)
for i in range(10):
    time.sleep(2.5); e.shot('shots/u%d.png'%i)
