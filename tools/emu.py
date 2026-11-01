# DuckStation 백그라운드 제어: GDB RSP 메모리 접근 + PostMessage 키 입력 + 스크린샷
import socket,subprocess,time,ctypes,os,glob,sys
from ctypes import wintypes
EXE=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'duck','tw_duck.exe')
SHOTS=os.path.join(os.path.dirname(EXE),'screenshots')
u32=ctypes.windll.user32
VK={'up':0x26,'down':0x28,'left':0x25,'right':0x27,'x':ord('K'),'o':ord('L'),'sq':ord('J'),'tri':ord('I'),
    'start':0x0D,'select':0x08,'l1':ord('Q'),'r1':ord('E'),'shot':0x79,'tab':0x09,'f1':0x70,'f2':0x71}
class Emu:
    def __init__(s,cue,state=None,gdb=True):
        args=[EXE,'-batch','-nogui']
        if state: args+=['-statefile',state]
        args+=['--',cue]
        si=subprocess.STARTUPINFO(); si.dwFlags=1; si.wShowWindow=4  # SW_SHOWNOACTIVATE
        s.p=subprocess.Popen(args,startupinfo=si)
        s.sock=None
        if gdb:
            for i in range(60):
                time.sleep(1)
                try:
                    s.sock=socket.create_connection(('127.0.0.1',2399),timeout=5); break
                except OSError: pass
        else:
            for i in range(30):
                time.sleep(1)
                if s._find(): break
            time.sleep(2)
        s.hwnds=s._find()
        s.offscreen()
        if s.sock: s.cont()
    def _find(s):
        res=[]
        CB=ctypes.WINFUNCTYPE(ctypes.c_bool,wintypes.HWND,wintypes.LPARAM)
        pid=s.p.pid
        def cb(h,l):
            p=wintypes.DWORD(); u32.GetWindowThreadProcessId(h,ctypes.byref(p))
            if p.value==pid:
                res.append(h)
                def cb2(h2,l2): res.append(h2); return True
                u32.EnumChildWindows(h,CB(cb2),0)
            return True
        u32.EnumWindows(CB(cb),0); return res
    # --- GDB RSP ---
    def _send(s,cmd):
        pk=b'$'+cmd.encode()+b'#'+('%02x'%(sum(cmd.encode())&0xff)).encode()
        s.sock.sendall(pk)
    def _recv(s):
        buf=b''
        while True:
            c=s.sock.recv(65536)
            if not c: raise IOError('closed')
            buf+=c
            i=buf.find(b'$')
            if i>=0:
                j=buf.find(b'#',i)
                if j>=0 and len(buf)>=j+3:
                    s.sock.sendall(b'+'); return buf[i+1:j].decode()
    def cmd(s,c):
        s._send(c); return s._recv()
    def halt(s):
        s.sock.sendall(b'\x03'); s._recv()
    def cont(s):
        s._send('c')
    def read(s,addr,n):
        s.halt(); out=b''
        while n>0:
            k=min(n,0x800); r=s.cmd('m%x,%x'%(addr,k))
            while len(r)!=2*k or r[:1] in 'ST': r=s._recv() if r[:1] in 'ST' else s.cmd('m%x,%x'%(addr,k))
            out+=bytes.fromhex(r); addr+=k; n-=k
        s.cont(); return out
    def write(s,addr,data):
        s.halt()
        for i in range(0,len(data),0x400):
            s.cmd('M%x,%x:%s'%(addr+i,len(data[i:i+0x400]),data[i:i+0x400].hex()))
        s.cont()
    # --- input ---
    def offscreen(s):
        for h in s.hwnds:
            if not u32.GetParent(h): u32.SetWindowPos(h,0,-3000,100,0,0,0x0001|0x0010|0x0004)
    def refresh(s):
        s.hwnds=s._find(); s.offscreen()
    def key(s,k,hold=0.08):
        if not s.hwnds or len(s.hwnds)<7 or not all(u32.IsWindow(h) for h in s.hwnds): s.refresh()
        vk=VK[k]; sc=u32.MapVirtualKeyW(vk,0)
        ext=0x01000000 if vk in (0x25,0x26,0x27,0x28) else 0
        for h in s.hwnds: u32.PostMessageW(h,0x100,vk,1|(sc<<16)|ext)
        time.sleep(hold)
        for h in s.hwnds: u32.PostMessageW(h,0x101,vk,1|(sc<<16)|ext|0xC0000000)
        time.sleep(0.05)
    def press(s,seq,wait=0.3):
        for k in seq.split():
            s.key(k); time.sleep(wait)
    def grab(s,out):
        from PIL import Image
        s.refresh(); best=None
        for h in s.hwnds:
            r=wintypes.RECT(); u32.GetClientRect(h,ctypes.byref(r))
            a=r.right*r.bottom
            if best is None or a>best[0]: best=(a,h,r.right,r.bottom)
        _,h,w,ht=best
        g=ctypes.windll.gdi32
        hdc=u32.GetDC(h); mdc=g.CreateCompatibleDC(hdc); bmp=g.CreateCompatibleBitmap(hdc,w,ht); g.SelectObject(mdc,bmp)
        u32.PrintWindow(h,mdc,3)
        class BI(ctypes.Structure): _fields_=[('a',ctypes.c_uint32),('w',ctypes.c_int32),('h',ctypes.c_int32),('p',ctypes.c_uint16),('b',ctypes.c_uint16),('c',ctypes.c_uint32*6)]
        bi=BI(40,w,-ht,1,32); buf=ctypes.create_string_buffer(w*ht*4)
        g.GetDIBits(mdc,bmp,0,ht,buf,ctypes.byref(bi),0)
        g.DeleteObject(bmp); g.DeleteDC(mdc); u32.ReleaseDC(h,hdc)
        Image.frombuffer('RGBA',(w,ht),buf,'raw','BGRA',0,1).convert('RGB').save(out); return out
    def shot(s,out):
        import shutil
        s.refresh(); before=set(glob.glob(SHOTS+'/*'))
        s.key('shot')
        for i in range(2000):
            time.sleep(0.03)
            for f in set(glob.glob(SHOTS+'/*'))-before:
                if not f.endswith('.png'): continue
                for k in range(100):
                    try:
                        d=open(f,'rb').read()
                        if d.endswith(bytes.fromhex('ae426082')):
                            open(out,'wb').write(d)
                            try: os.remove(f)
                            except OSError: pass
                            return out
                    except OSError: pass
                    time.sleep(0.03)
        return None
    def savestate(s): s.key('f2')
    def close(s):
        try: s.sock and s.sock.close()
        except: pass
        s.p.kill(); s.p.wait()
