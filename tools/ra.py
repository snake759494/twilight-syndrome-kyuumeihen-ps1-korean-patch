# RetroArch(Beetle PSX) 백그라운드 제어: UDP 명령/입력, 스크린샷, 세이브스테이트
import socket, subprocess, time, os, glob, struct, shutil

RADIR = r'D:\ps1\RetroArch-Win64'
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATES = os.path.join(HERE, 'ra', 'states', 'Beetle PSX HW')
SHOTS = os.path.join(HERE, 'ra', 'shots')
BTN = {'x': 0, 'sq': 1, 'select': 2, 'start': 3, 'up': 4, 'down': 5, 'left': 6, 'right': 7,
       'o': 8, 'tri': 9, 'l1': 10, 'r1': 11, 'l2': 12, 'r2': 13}


class RA:
    def __init__(s, cue, state=None):
        subprocess.run(['taskkill', '/F', '/IM', 'retroarch.exe'], capture_output=True)
        time.sleep(1)
        os.makedirs(STATES, exist_ok=True)
        for f in glob.glob(os.path.join(STATES, '*')):
            os.remove(f)
        s.name = os.path.splitext(os.path.basename(cue))[0]
        if state:
            shutil.copyfile(state, os.path.join(STATES, s.name + '.state'))
        si = subprocess.STARTUPINFO(); si.dwFlags = 1; si.wShowWindow = 4
        s.p = subprocess.Popen([os.path.join(RADIR, 'retroarch.exe'), '-L',
                                os.path.join(RADIR, 'cores', 'mednafen_psx_hw_libretro.dll'),
                                '--appendconfig', os.path.join(HERE, 'ra', 'append.cfg'), cue],
                               cwd=RADIR, startupinfo=si)
        s.c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.c.settimeout(3)
        s.i = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        time.sleep(6)

    def cmd(s, t):
        s.c.sendto(t.encode(), ('127.0.0.1', 55355))

    def btn(s, name, state):
        s.i.sendto(struct.pack('<iiiiHxx', 0, 1, 0, BTN[name], state), ('127.0.0.1', 55400))

    def key(s, name, hold=0.3):
        s.btn(name, 1); time.sleep(hold); s.btn(name, 0); time.sleep(0.1)

    def press(s, seq, wait=0.4):
        for k in seq.split():
            if k.startswith('w'):
                time.sleep(float(k[1:])); continue
            s.key(k); time.sleep(wait)

    def shot(s, out):
        for _ in range(4):
            r = s._shot(out)
            if r:
                return r
            time.sleep(0.5)
        return None

    def _shot(s, out):
        before = set(glob.glob(os.path.join(SHOTS, '*')))
        s.cmd('SCREENSHOT')
        for _ in range(40):
            time.sleep(0.25)
            new = set(glob.glob(os.path.join(SHOTS, '*'))) - before
            if new:
                f = new.pop()
                for _ in range(20):
                    time.sleep(0.3)
                    try:
                        os.replace(f, out); return out
                    except PermissionError:
                        pass
        return None

    def ff(s):
        s.cmd('FAST_FORWARD')

    def load(s):
        s.cmd('LOAD_STATE')

    def save(s, keep=None):
        before = {f: os.path.getmtime(f) for f in glob.glob(os.path.join(STATES, '*'))}
        s.cmd('SAVE_STATE')
        if not keep:
            return
        for _ in range(40):
            time.sleep(0.5)
            c = [f for f in glob.glob(os.path.join(STATES, '*'))
                 if not f.endswith('.png') and before.get(f) != os.path.getmtime(f)]
            if c:
                time.sleep(1.5); shutil.copyfile(c[0], keep); return keep

    def close(s):
        s.p.kill(); s.p.wait()


def diff(a, b):
    if not a or not b:
        return 999
    from PIL import Image, ImageChops
    x = Image.open(a).convert('L').resize((160, 120)); y = Image.open(b).convert('L').resize((160, 120))
    h = ImageChops.difference(x, y).histogram()
    return sum(i * n for i, n in enumerate(h)) / (160 * 120)


def press_until_change(e, key, tmp, tries=8, hold=0.4, wait=1.5, thr=6):
    base = e.shot(tmp + '_a.png')
    for _ in range(tries):
        e.key(key, hold); time.sleep(wait)
        cur = e.shot(tmp + '_b.png')
        if base and cur and diff(base, cur) > thr:
            return True
    return False


def wait_for(e, ref, tmp, timeout=90, thr=8, every=1.5):
    t = time.time()
    while time.time() - t < timeout:
        f = e.shot(tmp)
        if f and diff(f, ref) < thr:
            return True
        time.sleep(every)
    return False


def until(e, key, ref, tmp, tries=10, thr=8, hold=0.3, wait=1.5):
    for _ in range(tries):
        e.key(key, hold); time.sleep(wait)
        f = e.shot(tmp)
        if f and diff(f, ref) < thr:
            return True
    return False


def changed(e, key, tmp, tries=6, thr=1.0, hold=0.3, wait=1.0):
    base = e.shot(tmp + 'a.png')
    for _ in range(tries):
        e.key(key, hold); time.sleep(wait)
        f = e.shot(tmp + 'b.png')
        if diff(base, f) > thr:
            return True
    return False


def cdiff(a, b, box):
    if not a or not b:
        return 999
    from PIL import Image, ImageChops
    x = Image.open(a).convert('L').resize((320, 240)).crop(box)
    y = Image.open(b).convert('L').resize((320, 240)).crop(box)
    h = ImageChops.difference(x, y).histogram()
    return sum(i * n for i, n in enumerate(h)) / (x.width * x.height)


MENU_BOX = (90, 140, 240, 180)


def to_scenario(e, item=2, boot_wait=30):
    """타이틀 메뉴에서 item(0=NEW,1=LOAD,2=SCENARIO) 선택"""
    ref = os.path.join(HERE, 'ra', 'ref_menu.png'); tmp = os.path.join(HERE, 'shots', '_m.png')
    time.sleep(boot_wait)
    for i in range(40):
        e.key('start', 0.3); time.sleep(1.0)
        f = e.shot(tmp)
        if f and cdiff(f, ref, MENU_BOX) < 11:
            break
    else:
        return False
    for _ in range(item):
        base = e.shot(tmp)
        for _ in range(6):
            e.key('down', 0.3); time.sleep(0.7)
            f = e.shot(tmp)
            if cdiff(f, base, MENU_BOX) > 3 and cdiff(f, ref, MENU_BOX) < 20:
                break
    for _ in range(10):
        e.key('o', 0.3); time.sleep(1.2)
        f = e.shot(tmp)
        if cdiff(f, ref, MENU_BOX) > 25:
            return True
    return False


def bright(f):
    if not f:
        return 128
    from PIL import Image, ImageStat
    return ImageStat.Stat(Image.open(f).convert('L')).mean[0]


def to_newgame(e, boot_wait=40):
    """START 반복으로 메뉴 열기 -> ○ 반복으로 NEW GAME 결정 -> 어두운 화면 확인"""
    time.sleep(boot_wait)
    menu = os.path.join(HERE, 'ra', 'ref_menu.png'); tmp = os.path.join(HERE, 'shots', '_n.png')
    for i in range(40):
        f = e.shot(tmp)
        if cdiff(f, menu, MENU_BOX) < 13 and bright(f) > 30:
            break
        e.key('start', 0.3); time.sleep(1.5)
    else:
        return False
    for i in range(15):
        e.key('o', 0.3); time.sleep(1.5)
        f = e.shot(tmp)
        if bright(f) < 25:
            return True
    return False


def to_sidesel(e, keep):
    if not to_newgame(e):
        print('newgame fail', flush=True); return False
    ref = os.path.join(HERE, 'ra', 'ref_sidesel.png'); tmp = os.path.join(HERE, 'shots', '_s.png')
    e.ff()
    for i in range(80):
        time.sleep(5)
        e.ff(); time.sleep(0.4)
        f = e.shot(tmp)
        d = diff(f, ref) if f else None
        print('sidesel?', i, d and round(d, 1), flush=True)
        if f and d < 18:
            time.sleep(1)
            return e.save(keep)
        e.ff()
    e.ff()
    return False
