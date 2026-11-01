import sys,time,os;sys.path.insert(0,os.path.dirname(__file__))
from emu import Emu
e=Emu(os.path.abspath('../Twilight Syndrome - Kyuumei-hen (Japan).cue'))
time.sleep(25); e.grab('shots/b1.png')
for i in range(6):
    e.press('start',1.5); time.sleep(2)
e.grab("shots/b2.png"); e.shot("shots/b2s.png")
open('states/ram_b2.bin','wb').write(e.read(0x80000000,0x200000))
e.close()
