# 사용법: python tools/run.py <cue> <state|-> <script.py>  — 에뮬 실행, 스크립트 수행 후 항상 종료
import sys,os,time,struct
sys.path.insert(0,os.path.dirname(__file__))
from emu import Emu
cue,st,sc=sys.argv[1:4]
e=Emu(os.path.abspath(cue),None if st=='-' else os.path.abspath(st),gdb=bool(os.environ.get('GDB')))
try: exec(open(sc,encoding='utf8').read())
finally: e.close()
