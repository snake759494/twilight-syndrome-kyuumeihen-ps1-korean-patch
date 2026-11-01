import time
for i in range(4): e.key('start',hold=0.2); time.sleep(2)
time.sleep(6)
print('title',wait_vis('shots/t0.png',tries=15,dt=2,th=20))
e.key('o',hold=0.2)
for i in range(12):
    time.sleep(2.5); e.shot('shots/u%d.png'%i)
